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
    ResourceAdapter, MenuItem
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


class LinuxAdapter:
    """Main Linux adapter combining all sub-adapters."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self.keyboard = LinuxKeyboardAdapter(platform_info)
        self.clipboard = LinuxClipboardAdapter(platform_info)
        self.system_tray = LinuxSystemTrayAdapter(platform_info)
        self.resources = LinuxResourceAdapter(platform_info)

    def initialize(self):
        """Initialize all adapters."""
        self.clipboard.setup()