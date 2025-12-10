"""
Platform detection module for identifying OS, display environment, and desktop environment.
"""

import platform
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class PlatformInfo:
    """Information about the current platform."""
    os_name: str  # 'Linux', 'Windows', 'Darwin'
    os_version: str
    display_protocol: Optional[str]  # 'Wayland', 'X11', None
    desktop_environment: Optional[str]  # 'KDE', 'GNOME', 'Windows', 'Aqua'
    is_wsl: bool = False
    additional_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}


class PlatformDetector:
    """Detects platform information from environment variables and system calls."""

    @staticmethod
    def detect() -> PlatformInfo:
        """Detect the current platform."""
        os_name = platform.system()
        os_version = platform.release()

        # Default values
        display_protocol = None
        desktop_env = None
        is_wsl = False
        additional_info = {}

        if os_name == 'Linux':
            display_protocol, desktop_env, is_wsl = PlatformDetector._detect_linux_env()
            additional_info = PlatformDetector._detect_linux_capabilities()
        elif os_name == 'Windows':
            desktop_env = 'Windows'
            additional_info = PlatformDetector._detect_windows_capabilities()
        elif os_name == 'Darwin':
            desktop_env = 'Aqua'
            display_protocol = 'Cocoa'
            additional_info = PlatformDetector._detect_macos_capabilities()

        return PlatformInfo(
            os_name=os_name,
            os_version=os_version,
            display_protocol=display_protocol,
            desktop_environment=desktop_env,
            is_wsl=is_wsl,
            additional_info=additional_info
        )

    @staticmethod
    def _detect_linux_env() -> tuple[Optional[str], Optional[str], bool]:
        """Detect Linux display environment and desktop."""
        # Check for WSL
        if os.path.exists('/proc/version'):
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                if 'microsoft' in version_info or 'wsl' in version_info:
                    return None, 'WSL', True

        # Detect display protocol
        display_protocol = None
        if os.environ.get('WAYLAND_DISPLAY'):
            display_protocol = 'Wayland'
        elif os.environ.get('DISPLAY'):
            display_protocol = 'X11'

        # Detect desktop environment
        desktop_env = None
        xdg_current = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        xdg_session = os.environ.get('XDG_SESSION_DESKTOP', '').lower()

        if 'kde' in xdg_current or 'kde' in xdg_session or os.environ.get('KDE_SESSION_VERSION'):
            desktop_env = 'KDE'
        elif 'gnome' in xdg_current or 'gnome' in xdg_session:
            desktop_env = 'GNOME'
        elif 'ubuntu' in xdg_current:
            desktop_env = 'Ubuntu'
        elif 'xfce' in xdg_current or 'xfce' in xdg_session:
            desktop_env = 'XFCE'
        elif 'i3' in xdg_current or os.environ.get('I3SOCK'):
            desktop_env = 'i3'

        return display_protocol, desktop_env, False

    @staticmethod
    def _detect_linux_capabilities() -> Dict[str, Any]:
        """Detect Linux-specific capabilities."""
        capabilities = {}

        # Check for clipboard tools
        clipboard_tools = []
        for tool in ['xclip', 'wl-copy', 'xsel', 'wl-paste']:
            try:
                result = os.system(f'which {tool} > /dev/null 2>&1')
                if result == 0:
                    clipboard_tools.append(tool)
            except:
                pass
        capabilities['clipboard_tools'] = clipboard_tools

        # Check for keyboard simulation tools
        keyboard_tools = []
        for tool in ['wtype', 'ydotool', 'xdotool', 'xte', 'xvkbd']:
            try:
                result = os.system(f'which {tool} > /dev/null 2>&1')
                if result == 0:
                    keyboard_tools.append(tool)
            except:
                pass
        capabilities['keyboard_tools'] = keyboard_tools

        # Check for Python packages
        capabilities['pyautogui_available'] = PlatformDetector._check_python_module('pyautogui')
        capabilities['pystray_available'] = PlatformDetector._check_python_module('pystray')
        capabilities['pynput_available'] = PlatformDetector._check_python_module('pynput')

        return capabilities

    @staticmethod
    def _detect_windows_capabilities() -> Dict[str, Any]:
        """Detect Windows-specific capabilities."""
        capabilities = {}

        # Check for Windows-specific features
        capabilities['win32api_available'] = PlatformDetector._check_python_module('win32api')
        capabilities['win32gui_available'] = PlatformDetector._check_python_module('win32gui')
        capabilities['pywin32_available'] = PlatformDetector._check_python_module('win32gui') or \
                                         PlatformDetector._check_python_module('win32api')
        capabilities['pyautogui_available'] = PlatformDetector._check_python_module('pyautogui')
        capabilities['pystray_available'] = PlatformDetector._check_python_module('pystray')

        return capabilities

    @staticmethod
    def _detect_macos_capabilities() -> Dict[str, Any]:
        """Detect macOS-specific capabilities."""
        capabilities = {}

        # Check for macOS-specific features
        capabilities['appkit_available'] = PlatformDetector._check_python_module('AppKit')
        capabilities['pyobjus_available'] = PlatformDetector._check_python_module('PyObjC')
        capabilities['pyautogui_available'] = PlatformDetector._check_python_module('pyautogui')
        capabilities['pystray_available'] = PlatformDetector._check_python_module('pystray')
        capabilities['pynput_available'] = PlatformDetector._check_python_module('pynput')

        return capabilities

    @staticmethod
    def _check_python_module(module_name: str) -> bool:
        """Check if a Python module is available."""
        try:
            import importlib
            importlib.import_module(module_name)
            return True
        except (ImportError, Exception):
            # 捕获所有异常，包括模块导入时的 X11 连接错误
            return False