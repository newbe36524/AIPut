"""
Linux-specific platform adapter implementation.
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
except (ImportError, Exception) as e:
    # 捕获 ImportError 和 X11 连接错误
    # 在某些环境下，pyautogui 导入时会尝试连接 X11 display
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None

try:
    import pyperclip
    PIPERCLIP_AVAILABLE = True
except (ImportError, Exception):
    PIPERCLIP_AVAILABLE = False
    pyperclip = None

from platform_adapters.base import (
    KeyboardAdapter, ClipboardAdapter, SystemTrayAdapter,
    ResourceAdapter, NotificationAdapter, MenuItem
)
from platform_detection.detector import PlatformInfo
from platform_adapters.linux.wayland import WaylandKeyboardAdapter
from platform_adapters.linux.x11 import X11KeyboardAdapter


class LinuxKeyboardAdapter(KeyboardAdapter):
    """Linux keyboard simulation adapter supporting both X11 and Wayland."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._is_wayland = platform_info.display_protocol == 'Wayland'
        self._is_x11 = platform_info.display_protocol == 'X11'
        self._desktop_env = platform_info.desktop_environment or 'Unknown'

        # Create specific adapter based on display protocol
        if self._is_wayland:
            self._specific_adapter = WaylandKeyboardAdapter(platform_info)
        elif self._is_x11:
            self._specific_adapter = X11KeyboardAdapter(platform_info)
        else:
            # Fallback adapter
            self._specific_adapter = None

    async def send_paste_command(self) -> bool:
        """Send paste command using the appropriate method for the current environment."""
        if self._specific_adapter:
            return await self._specific_adapter.send_paste_command()

        # Fallback to pyautogui if available
        if PYAUTOGUI_AVAILABLE:
            try:
                pyautogui.hotkey('shift', 'insert')
                return True
            except Exception:
                pass

        return False

    async def send_ctrl_enter(self) -> bool:
        """Send Ctrl+Enter key combination using the appropriate method for the current environment."""
        if self._specific_adapter:
            return await self._specific_adapter.send_ctrl_enter()

        # Fallback to pyautogui if available
        if PYAUTOGUI_AVAILABLE:
            try:
                pyautogui.hotkey('ctrl', 'enter')
                return True
            except Exception:
                pass

        return False

    def is_available(self) -> bool:
        """Check if keyboard simulation is available."""
        if self._specific_adapter:
            return self._specific_adapter.is_available()
        return PYAUTOGUI_AVAILABLE

    def get_available_methods(self) -> List[str]:
        """Get list of available keyboard simulation methods."""
        methods = []

        if self._specific_adapter:
            methods.extend(self._specific_adapter.get_available_methods())

        if PYAUTOGUI_AVAILABLE:
            methods.append('pyautogui')

        return methods

    async def send_text(self, text: str) -> bool:
        """Send text directly using the specific adapter if available."""
        if self._specific_adapter:
            return await self._specific_adapter.send_text(text)
        return False

    async def keep_alive(self) -> bool:
        """Keep-alive implementation using Scroll Lock key.

        Returns:
            bool: True if keep-alive was performed successfully, False otherwise.
        """
        if self._specific_adapter:
            return await self._specific_adapter.keep_alive()
        return False


class LinuxClipboardAdapter(ClipboardAdapter):
    """Linux clipboard adapter supporting multiple tools."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._is_wayland = platform_info.display_protocol == 'Wayland'
        self._is_x11 = platform_info.display_protocol == 'X11'
        self._preferred_tool = None
        self._available_tools = platform_info.additional_info.get('clipboard_tools', [])

    def setup(self) -> None:
        """Initialize clipboard support."""
        # Choose preferred tool based on environment
        if self._is_wayland:
            # Prefer Wayland-native tools
            for tool in ['wl-copy', 'wl-paste', 'wtype']:
                if tool in self._available_tools:
                    self._preferred_tool = tool
                    break

        # Fallback to X11 tools or generic
        if not self._preferred_tool:
            for tool in ['xclip', 'xsel']:
                if tool in self._available_tools:
                    self._preferred_tool = tool
                    break

    async def copy_text(self, text: str) -> bool:
        """Copy text to clipboard."""
        # Try tool-specific method first
        if self._preferred_tool:
            try:
                if self._preferred_tool == 'wl-copy':
                    subprocess.run(['wl-copy'], input=text.encode(), check=True)
                    return True
                elif self._preferred_tool == 'xclip':
                    proc = subprocess.Popen(['xclip', '-selection', 'clipboard'],
                                         stdin=subprocess.PIPE)
                    proc.communicate(text.encode())
                    return proc.returncode == 0
                elif self._preferred_tool == 'xsel':
                    proc = subprocess.Popen(['xsel', '--clipboard', '--input'],
                                         stdin=subprocess.PIPE)
                    proc.communicate(text.encode())
                    return proc.returncode == 0
            except Exception:
                pass

        # Fallback to pyperclip
        if PIPERCLIP_AVAILABLE:
            try:
                pyperclip.copy(text)
                # Give it a moment to take effect
                await asyncio.sleep(0.1)
                return True
            except Exception:
                pass

        return False

    def is_available(self) -> bool:
        """Check if clipboard operations are available."""
        return bool(self._available_tools) or PIPERCLIP_AVAILABLE

    def get_preferred_tool(self) -> Optional[str]:
        """Get the preferred clipboard tool being used."""
        return self._preferred_tool or ('pyperclip' if PIPERCLIP_AVAILABLE else None)


class LinuxSystemTrayAdapter(SystemTrayAdapter):
    """Linux system tray adapter using pystray."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self.tray_icon = None
        self.pystray = None

        # Try to import pystray
        try:
            import pystray
            self.pystray = pystray
        except (ImportError, Exception):
            # pystray 在导入时会尝试连接 X11，可能失败
            pass

    def create_tray_icon(self, menu_items: List[MenuItem]) -> bool:
        """Create system tray icon."""
        if not self.is_supported():
            return False

        try:
            # Create menu items for pystray
            menu_items_pystray = []
            for item in menu_items:
                menu_items_pystray.append(
                    self.pystray.MenuItem(item.label, item.action)
                )

            # Create a simple icon
            image = self._create_icon_image()

            # Create menu
            menu = self.pystray.Menu(*menu_items_pystray)

            # Create tray icon
            self.tray_icon = self.pystray.Icon(
                "AIPut",
                image,
                "AIPut - Remote Input",
                menu
            )

            # Run in background thread
            import threading
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

            return True
        except Exception:
            return False

    def is_supported(self) -> bool:
        """Check if system tray is supported."""
        if not self.pystray:
            return False

        # Wayland has limited support
        if self.platform_info.display_protocol == 'Wayland':
            # KDE Wayland might work, others probably not
            return self.platform_info.desktop_environment == 'KDE'

        return True

    def hide_window(self) -> None:
        """Hide the main window."""
        # This would need to be implemented with access to the window
        pass

    def show_window(self) -> None:
        """Show the main window."""
        # This would need to be implemented with access to the window
        pass

    def stop(self) -> None:
        """Stop the tray icon."""
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def _create_icon_image(self):
        """Create a simple icon image."""
        try:
            from PIL import Image
            # Create a simple blue square icon
            image = Image.new('RGB', (64, 64), color='#007AFF')
            return image
        except ImportError:
            # Fallback - pystray can create a default icon
            return None


class LinuxResourceAdapter(ResourceAdapter):
    """Linux resource adapter."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info

    def get_icon_path(self, icon_names: List[str]) -> Optional[str]:
        """Get path to icon file."""
        # Check PyInstaller bundle first
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            for icon_name in icon_names:
                icon_path = os.path.join(sys._MEIPASS, icon_name)
                if os.path.exists(icon_path):
                    return icon_path

        # Check current directory
        for icon_name in icon_names:
            if os.path.exists(icon_name):
                return icon_name

        # Check standard icon locations
        icon_dirs = [
            '/usr/share/icons/hicolor/256x256/apps',
            '/usr/share/pixmaps',
            '~/.local/share/icons',
            '~/.icons'
        ]

        for icon_dir in icon_dirs:
            icon_dir = os.path.expanduser(icon_dir)
            for icon_name in icon_names:
                icon_path = os.path.join(icon_dir, icon_name)
                if os.path.exists(icon_path):
                    return icon_path

        return None

    def get_resource_path(self, resource_name: str) -> Optional[str]:
        """Get path to any resource file."""
        # Similar logic to get_icon_path
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            resource_path = os.path.join(sys._MEIPASS, resource_name)
            if os.path.exists(resource_path):
                return resource_path

        if os.path.exists(resource_name):
            return resource_name

        return None

    def load_image(self, path: str) -> Any:
        """Load an image file."""
        try:
            from PIL import Image
            return Image.open(path)
        except ImportError:
            # Could use another image library or return the path
            return path

    def get_app_data_dir(self) -> Optional[str]:
        """Get application data directory."""
        # Follow XDG Base Directory Specification
        xdg_data_home = os.environ.get('XDG_DATA_HOME')
        if xdg_data_home:
            return os.path.join(xdg_data_home, 'aiput')

        # Fallback to ~/.local/share
        return os.path.expanduser('~/.local/share/aiput')


class LinuxNotificationAdapter(NotificationAdapter):
    """Linux notification adapter using custom sound file."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._paplay_available = self._check_command('paplay')
        self._aplay_available = self._check_command('aplay')
        self._canberra_available = self._check_command('canberra-gtk-play')
        self._speaker_test_available = self._check_command('speaker-test')

        # Use custom sound file
        self._custom_sound = '/home/newbe36524/repos/newbe36524/qaa-airtype/src/assets/029_Decline_09.wav'

    def _check_command(self, command: str) -> bool:
        """Check if a command is available."""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except:
            return False

    def show_notification(self, title: str, message: str, duration: int = 5000) -> bool:
        """Show a Linux notification (not implemented for now)."""
        return False

    def is_supported(self) -> bool:
        """Check if notifications are supported."""
        return True  # Linux supports sound notifications

    def play_notification_sound(self, sound_type: str = NotificationAdapter.SOUND_NOTIFICATION) -> bool:
        """Play a custom notification sound."""
        print(f"[DEBUG] Audio tools - aplay: {self._aplay_available}, paplay: {self._paplay_available}")
        print(f"[DEBUG] Trying to play custom sound: {os.path.basename(self._custom_sound)}")

        # Check if custom sound file exists
        if not os.path.exists(self._custom_sound):
            print(f"[DEBUG] Custom sound file not found: {self._custom_sound}")
            # Fallback to terminal bell
            try:
                print('\a', end='', flush=True)
                return True
            except:
                return False

        # Try to play the custom sound file with available players
        # Priority 1: Use aplay (ALSA)
        if self._aplay_available:
            try:
                print(f"[DEBUG] Playing custom sound with aplay...")
                proc = subprocess.Popen(['aplay', self._custom_sound],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.PIPE)
                # Give it a moment to start
                import time
                time.sleep(0.1)
                if proc.poll() is None:
                    print("[DEBUG] ✓ aplay started successfully")
                    # Let it run in background
                    return True
                else:
                    _, stderr = proc.communicate()
                    if stderr:
                        print(f"[DEBUG] ✗ aplay error: {stderr.decode()}")
            except Exception as e:
                print(f"[DEBUG] aplay exception: {e}")

        # Priority 2: Use paplay (PulseAudio)
        if self._paplay_available:
            try:
                print(f"[DEBUG] Playing custom sound with paplay...")
                proc = subprocess.Popen(['paplay', self._custom_sound],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.PIPE)
                time.sleep(0.1)
                if proc.poll() is None:
                    print("[DEBUG] ✓ paplay started successfully")
                    return True
                else:
                    _, stderr = proc.communicate()
                    if stderr:
                        print(f"[DEBUG] ✗ paplay error: {stderr.decode()}")
            except Exception as e:
                print(f"[DEBUG] paplay exception: {e}")

        # Fallback to terminal bell
        print("[DEBUG] Using terminal bell fallback")
        try:
            print('\a', end='', flush=True)
            return True
        except:
            return False


class LinuxAdapter:
    """Main Linux adapter combining all sub-adapters."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self.keyboard = LinuxKeyboardAdapter(platform_info)
        self.clipboard = LinuxClipboardAdapter(platform_info)
        self.system_tray = LinuxSystemTrayAdapter(platform_info)
        self.resources = LinuxResourceAdapter(platform_info)
        self.notifications = LinuxNotificationAdapter(platform_info)

    def initialize(self):
        """Initialize all adapters."""
        self.clipboard.setup()