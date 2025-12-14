"""
macOS-specific platform adapter implementation.
"""

import asyncio
import os
import sys
import subprocess
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    import pyautogui
    pyautogui.PAUSE = 0.1
    pyautogui.FAILSAFE = False
    PYAUTOGUI_AVAILABLE = True
except (ImportError, Exception):
    # 捕获 ImportError 和其他异常（例如 X11 连接错误）
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None

try:
    import pyperclip
    PIPERCLIP_AVAILABLE = True
except (ImportError, Exception):
    PIPERCLIP_AVAILABLE = False
    pyperclip = None

try:
    import pystray
    from PIL import Image
    PYSTRAY_AVAILABLE = True
except (ImportError, Exception):
    # pystray 在导入时会尝试连接 X11，在 Linux 上可能失败
    PYSTRAY_AVAILABLE = False
    pystray = None
    Image = None

from platform_adapters.base import (
    KeyboardAdapter, ClipboardAdapter, SystemTrayAdapter,
    ResourceAdapter, NotificationAdapter, MenuItem
)
from platform_detection.detector import PlatformInfo


class MacOSKeyboardAdapter(KeyboardAdapter):
    """macOS keyboard adapter using pyautogui or AppleScript."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._methods = []
        self._detect_methods()

    def _detect_methods(self):
        """Detect available keyboard input methods."""
        if PYAUTOGUI_AVAILABLE:
            self._methods.append('pyautogui')

        # Check for AppKit
        try:
            from AppKit import NSEvent
            self._methods.append('AppKit')
        except ImportError:
            pass

        # Check for pynput
        try:
            import pynput
            self._methods.append('pynput')
        except ImportError:
            pass

        # osascript is always available on macOS
        self._methods.append('osascript')

    async def send_paste_command(self) -> bool:
        """Send paste command (Cmd+V on macOS)."""
        # Try pyautogui first
        if 'pyautogui' in self._methods:
            try:
                pyautogui.hotkey('command', 'v')
                return True
            except Exception:
                pass

        # Try osascript
        if 'osascript' in self._methods:
            try:
                script = '''
                tell application "System Events"
                    keystroke "v" using command down
                end tell
                '''
                subprocess.run(['osascript', '-e', script], check=False)
                return True
            except Exception:
                pass

        return False

    async def send_ctrl_enter(self) -> bool:
        """Send Ctrl+Enter key combination on macOS."""
        # Try pyautogui first
        if 'pyautogui' in self._methods:
            try:
                pyautogui.hotkey('ctrl', 'enter')
                return True
            except Exception:
                pass

        # Try osascript
        if 'osascript' in self._methods:
            try:
                script = '''
                tell application "System Events"
                    keystroke return using control down
                end tell
                '''
                subprocess.run(['osascript', '-e', script], check=False)
                return True
            except Exception:
                pass

        return False

    def is_available(self) -> bool:
        """Check if keyboard simulation is available."""
        return bool(self._methods)

    def get_available_methods(self) -> List[str]:
        """Get list of available methods."""
        return self._methods.copy()

    async def send_text(self, text: str) -> bool:
        """Send text directly."""
        if 'pyautogui' in self._methods:
            try:
                pyautogui.typewrite(text)
                return True
            except Exception:
                pass
        return False


class MacOSClipboardAdapter(ClipboardAdapter):
    """macOS clipboard adapter."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._preferred_tool = None

    def setup(self) -> None:
        """Initialize clipboard support."""
        # macOS has built-in clipboard support
        pass

    async def copy_text(self, text: str) -> bool:
        """Copy text to clipboard."""
        # Try pyperclip first
        if PIPERCLIP_AVAILABLE:
            try:
                pyperclip.copy(text)
                await asyncio.sleep(0.1)
                return True
            except Exception:
                pass

        # Try pbcopy command
        try:
            proc = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            proc.communicate(text.encode())
            return proc.returncode == 0
        except Exception:
            pass

        return False

    def is_available(self) -> bool:
        """Check if clipboard is available."""
        return True  # macOS always has clipboard

    def get_preferred_tool(self) -> Optional[str]:
        """Get preferred tool."""
        if PIPERCLIP_AVAILABLE:
            return 'pyperclip'
        return 'pbcopy'


class MacOSSystemTrayAdapter(SystemTrayAdapter):
    """macOS system tray adapter."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self.tray_icon = None

    def create_tray_icon(self, menu_items: List[MenuItem]) -> bool:
        """Create system tray icon."""
        if not self.is_supported():
            return False

        try:
            # Create menu items
            pystray_items = []
            for item in menu_items:
                pystray_items.append(
                    pystray.MenuItem(item.label, item.action)
                )

            # Create icon
            image = self._create_icon_image()

            # Create menu
            menu = pystray.Menu(*pystray_items)

            # Create tray icon
            self.tray_icon = pystray.Icon(
                "AIPut",
                image,
                "AIPut - Remote Input",
                menu
            )

            # Run in background
            import threading
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

            return True
        except Exception:
            return False

    def is_supported(self) -> bool:
        """Check if system tray is supported."""
        return PYSTRAY_AVAILABLE

    def hide_window(self) -> None:
        """Hide the main window."""
        pass

    def show_window(self) -> None:
        """Show the main window."""
        pass

    def stop(self) -> None:
        """Stop the tray icon."""
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def _create_icon_image(self):
        """Create macOS-style icon."""
        if Image:
            # Create a macOS-style icon
            image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            # Simple circle icon
            from PIL import ImageDraw
            draw = ImageDraw.Draw(image)
            draw.ellipse([8, 8, 56, 56], fill='#007AFF')
            return image
        return None


class MacOSResourceAdapter(ResourceAdapter):
    """macOS resource adapter."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info

    def get_icon_path(self, icon_names: List[str]) -> Optional[str]:
        """Get path to icon file."""
        # Check PyInstaller bundle
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            for icon_name in icon_names:
                icon_path = os.path.join(sys._MEIPASS, icon_name)
                if os.path.exists(icon_path):
                    return icon_path

        # Check current directory
        for icon_name in icon_names:
            if os.path.exists(icon_name):
                return icon_name

        # Check Application Support directory
        app_support = self.get_app_data_dir()
        if app_support:
            for icon_name in icon_names:
                icon_path = os.path.join(app_support, 'icons', icon_name)
                if os.path.exists(icon_path):
                    return icon_path

        return None

    def get_resource_path(self, resource_name: str) -> Optional[str]:
        """Get path to resource file."""
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            resource_path = os.path.join(sys._MEIPASS, resource_name)
            if os.path.exists(resource_path):
                return resource_path

        if os.path.exists(resource_name):
            return resource_name

        return None

    def load_image(self, path: str) -> Any:
        """Load an image file."""
        if Image:
            try:
                return Image.open(path)
            except:
                pass
        return path

    def get_app_data_dir(self) -> Optional[str]:
        """Get application data directory."""
        # Use ~/Library/Application Support on macOS
        home = os.path.expanduser('~')
        return os.path.join(home, 'Library', 'Application Support', 'AIPut')


class MacOSNotificationAdapter(NotificationAdapter):
    """macOS notification adapter using custom sound file."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._afplay_available = self._check_afplay()

        # Path to custom sound file - adjust for macOS path if needed
        self._custom_sound = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', '029_Decline_09.wav')
        # Convert to absolute path
        self._custom_sound = os.path.abspath(self._custom_sound)

    def _check_afplay(self) -> bool:
        """Check if afplay command is available."""
        try:
            subprocess.run(['afplay', '--help'], capture_output=True, check=True)
            return True
        except:
            return False

    def show_notification(self, title: str, message: str, duration: int = 5000) -> bool:
        """Show a macOS notification (not implemented for now)."""
        return False

    def is_supported(self) -> bool:
        """Check if notifications are supported."""
        return True  # macOS supports sound notifications

    def play_notification_sound(self, sound_type: str = NotificationAdapter.SOUND_NOTIFICATION) -> bool:
        """Play a custom notification sound."""
        print(f"[DEBUG] Trying to play custom sound: {os.path.basename(self._custom_sound)}")

        # Check if custom sound file exists
        if not os.path.exists(self._custom_sound):
            print(f"[DEBUG] Custom sound file not found: {self._custom_sound}")
            # Fallback to system sounds
            return self._play_fallback_sounds()

        # Try to play the custom sound file with afplay
        if self._afplay_available:
            try:
                print(f"[DEBUG] Playing custom sound with afplay...")
                # Play sound in background
                subprocess.Popen(['afplay', self._custom_sound],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                return True
            except Exception as e:
                print(f"[DEBUG] afplay failed for custom sound: {e}")

        # Fallback to other methods
        return self._play_fallback_sounds()

    def _play_fallback_sounds(self) -> bool:
        """Play fallback system sounds."""
        # Try osascript to play system sound
        try:
            script = 'beep'
            subprocess.Popen(['osascript', '-e', script],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"osascript beep failed: {e}")

        # Try NSSound via PyObjC
        try:
            from AppKit import NSSound
            sound = NSSound.soundNamed_('Ping')
            if sound:
                sound.play()
                return True
        except Exception as e:
            print(f"NSSound failed: {e}")

        # Fallback to terminal bell
        try:
            print('\a', end='', flush=True)
            return True
        except:
            return False


class MacOSAdapter:
    """Main macOS adapter combining all sub-adapters."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self.keyboard = MacOSKeyboardAdapter(platform_info)
        self.clipboard = MacOSClipboardAdapter(platform_info)
        self.system_tray = MacOSSystemTrayAdapter(platform_info)
        self.resources = MacOSResourceAdapter(platform_info)
        self.notifications = MacOSNotificationAdapter(platform_info)

    def initialize(self):
        """Initialize all adapters."""
        self.clipboard.setup()