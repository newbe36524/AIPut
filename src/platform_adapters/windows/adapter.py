"""
Windows-specific platform adapter implementation.
"""

import asyncio
import os
import sys
import subprocess
import time
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


class WindowsKeyboardAdapter(KeyboardAdapter):
    """Windows keyboard adapter using pyautogui or native APIs."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._methods = []
        self._detect_methods()

    def _detect_methods(self):
        """Detect available keyboard input methods."""
        if PYAUTOGUI_AVAILABLE:
            self._methods.append('pyautogui')

        # Check for win32api
        try:
            import win32api
            import win32con
            self._methods.append('win32api')
        except ImportError:
            pass

        # Check for pynput
        try:
            import pynput
            self._methods.append('pynput')
        except ImportError:
            pass

    async def send_paste_command(self) -> bool:
        """Send paste command (Shift+Insert on Windows)."""
        # Try pyautogui first
        if 'pyautogui' in self._methods:
            try:
                pyautogui.hotkey('shift', 'insert')
                return True
            except Exception:
                pass

        # Try win32api
        if 'win32api' in self._methods:
            try:
                import win32api
                import win32con
                import win32gui

                # Press Shift
                win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                # Press Insert
                win32api.keybd_event(win32con.VK_INSERT, 0, 0, 0)
                # Release Insert
                win32api.keybd_event(win32con.VK_INSERT, 0, win32con.KEYEVENTF_KEYUP, 0)
                # Release Shift
                win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                return True
            except Exception:
                pass

        return False

    async def send_ctrl_enter(self) -> bool:
        """Send Ctrl+Enter key combination on Windows."""
        # Try pyautogui first
        if 'pyautogui' in self._methods:
            try:
                pyautogui.hotkey('ctrl', 'enter')
                return True
            except Exception:
                pass

        # Try win32api
        if 'win32api' in self._methods:
            try:
                import win32api
                import win32con
                import win32gui

                # Press Ctrl
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                # Press Enter
                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                # Release Enter
                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                # Release Ctrl
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
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


class WindowsClipboardAdapter(ClipboardAdapter):
    """Windows clipboard adapter."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._preferred_tool = None

    def setup(self) -> None:
        """Initialize clipboard support."""
        # Windows has built-in clipboard support
        pass

    async def copy_text(self, text: str) -> bool:
        """Copy text to clipboard."""
        # Try pyperclip first (cross-platform)
        if PIPERCLIP_AVAILABLE:
            try:
                pyperclip.copy(text)
                await asyncio.sleep(0.1)
                return True
            except Exception:
                pass

        # Try Windows-specific method
        try:
            import win32clipboard
            import win32con

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_TEXT)
            win32clipboard.CloseClipboard()
            return True
        except ImportError:
            pass
        except Exception:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass

        return False

    def is_available(self) -> bool:
        """Check if clipboard is available."""
        return True  # Windows always has clipboard

    def get_preferred_tool(self) -> Optional[str]:
        """Get preferred tool."""
        if PIPERCLIP_AVAILABLE:
            return 'pyperclip'
        return 'win32api'


class WindowsSystemTrayAdapter(SystemTrayAdapter):
    """Windows system tray adapter."""

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
        # Implementation would need access to the window
        pass

    def show_window(self) -> None:
        """Show the main window."""
        # Implementation would need access to the window
        pass

    def stop(self) -> None:
        """Stop the tray icon."""
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def _create_icon_image(self):
        """Create icon image."""
        if Image:
            # Create a Windows-style icon
            image = Image.new('RGB', (64, 64), color='#007AFF')
            return image
        return None


class WindowsResourceAdapter(ResourceAdapter):
    """Windows resource adapter."""

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

        # Check app data directory
        app_data = self.get_app_data_dir()
        if app_data:
            for icon_name in icon_names:
                icon_path = os.path.join(app_data, 'icons', icon_name)
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
        # Use %APPDATA% on Windows
        app_data = os.environ.get('APPDATA')
        if app_data:
            return os.path.join(app_data, 'AIPut')
        return None


class WindowsNotificationAdapter(NotificationAdapter):
    """Windows notification adapter using custom sound file."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._winsound_available = False
        self._check_winsound()

        # Path to custom sound file - adjust for Windows path if needed
        self._custom_sound = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', '029_Decline_09.wav')
        # Convert to absolute path
        self._custom_sound = os.path.abspath(self._custom_sound)

    def _check_winsound(self):
        """Check if winsound is available."""
        try:
            import winsound
            self._winsound = winsound
            self._winsound_available = True
        except ImportError:
            self._winsound_available = False

    def show_notification(self, title: str, message: str, duration: int = 5000) -> bool:
        """Show a Windows notification (not implemented for now)."""
        return False

    def is_supported(self) -> bool:
        """Check if notifications are supported."""
        return True  # Windows supports sound notifications

    def play_notification_sound(self, sound_type: str = NotificationAdapter.SOUND_NOTIFICATION) -> bool:
        """Play a custom notification sound."""
        print(f"[DEBUG] Trying to play custom sound: {os.path.basename(self._custom_sound)}")

        # Check if custom sound file exists
        if not os.path.exists(self._custom_sound):
            print(f"[DEBUG] Custom sound file not found: {self._custom_sound}")
            # Fallback to Windows system sounds
            if self._winsound_available:
                try:
                    # Use Windows MessageBeep for system sounds
                    # MB_ICONASTERISK = 0x00000040
                    self._winsound.MessageBeep(0x00000040)
                    return True
                except Exception as e:
                    print(f"Windows MessageBeep failed: {e}")

            # Final fallback to terminal bell
            try:
                print('\a', end='', flush=True)
                return True
            except:
                return False

        # Try to play the custom sound file using Windows media player
        try:
            print(f"[DEBUG] Playing custom sound with Windows default player...")
            # Use Windows built-in media player to play the sound
            subprocess.Popen(['powershell', '-c', f'(New-Object Media.SoundPlayer "{self._custom_sound}").PlaySync();'],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"[DEBUG] Failed to play custom sound: {e}")

            # Fallback to Windows system sounds
            if self._winsound_available:
                try:
                    self._winsound.MessageBeep(0x00000040)
                    return True
                except Exception as e2:
                    print(f"Windows MessageBeep failed: {e2}")

            # Final fallback to terminal bell
            try:
                print('\a', end='', flush=True)
                return True
            except:
                return False


class WindowsAdapter:
    """Main Windows adapter combining all sub-adapters."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self.keyboard = WindowsKeyboardAdapter(platform_info)
        self.clipboard = WindowsClipboardAdapter(platform_info)
        self.system_tray = WindowsSystemTrayAdapter(platform_info)
        self.resources = WindowsResourceAdapter(platform_info)
        self.notifications = WindowsNotificationAdapter(platform_info)

    def initialize(self):
        """Initialize all adapters."""
        self.clipboard.setup()