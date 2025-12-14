"""
Factory for creating platform-specific adapters.
"""

import os
import subprocess
from typing import Dict, Type, Optional, Any
from platform_detection.detector import PlatformDetector, PlatformInfo
from platform_detection.capabilities import PlatformCapabilities
from platform_adapters.base import (
    KeyboardAdapter, ClipboardAdapter, SystemTrayAdapter,
    ResourceAdapter, NotificationAdapter
)
from platform_adapters.linux.adapter import LinuxAdapter
from platform_adapters.windows.adapter import WindowsAdapter
from platform_adapters.macos.adapter import MacOSAdapter


class GenericAdapter:
    """Generic fallback adapter for unsupported platforms."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self.keyboard = GenericKeyboardAdapter(platform_info)
        self.clipboard = GenericClipboardAdapter(platform_info)
        self.system_tray = GenericSystemTrayAdapter(platform_info)
        self.resources = GenericResourceAdapter(platform_info)
        self.notifications = GenericNotificationAdapter(platform_info)

    def initialize(self):
        """Initialize adapters."""
        self.clipboard.setup()


class GenericKeyboardAdapter(KeyboardAdapter):
    """Generic keyboard adapter with minimal functionality."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        try:
            import pyautogui
            pyautogui.PAUSE = 0.1
            pyautogui.FAILSAFE = False
            self._pyautogui = pyautogui
            self._available = True
        except (ImportError, Exception) as e:
            # 捕获 ImportError 和 X11 连接错误
            self._pyautogui = None
            self._available = False

    async def send_paste_command(self) -> bool:
        """Send paste command using generic method."""
        if self._available and self._pyautogui:
            try:
                # Try both Shift+Insert and Ctrl+V
                self._pyautogui.hotkey('shift', 'insert')
                return True
            except:
                try:
                    self._pyautogui.hotkey('ctrl', 'v')
                    return True
                except:
                    pass
        return False

    def is_available(self) -> bool:
        """Check if keyboard simulation is available."""
        return self._available

    def get_available_methods(self) -> list:
        """Get available methods."""
        return ['pyautogui'] if self._available else []


class GenericClipboardAdapter(ClipboardAdapter):
    """Generic clipboard adapter using pyperclip."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._pyperclip = None
        try:
            import pyperclip
            self._pyperclip = pyperclip
        except ImportError:
            pass

    def setup(self) -> None:
        """Initialize clipboard support."""
        pass

    async def copy_text(self, text: str) -> bool:
        """Copy text to clipboard."""
        if self._pyperclip:
            try:
                self._pyperclip.copy(text)
                return True
            except:
                pass
        return False

    def is_available(self) -> bool:
        """Check if clipboard is available."""
        return self._pyperclip is not None

    def get_preferred_tool(self) -> Optional[str]:
        """Get preferred tool."""
        return 'pyperclip' if self._pyperclip else None


class GenericSystemTrayAdapter(SystemTrayAdapter):
    """Generic system tray adapter (no-op implementation)."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info

    def create_tray_icon(self, menu_items) -> bool:
        """Create system tray icon (not supported)."""
        return False

    def is_supported(self) -> bool:
        """Check if system tray is supported."""
        return False

    def hide_window(self) -> None:
        """Hide window."""
        pass

    def show_window(self) -> None:
        """Show window."""
        pass

    def stop(self) -> None:
        """Stop tray icon."""
        pass


class GenericResourceAdapter(ResourceAdapter):
    """Generic resource adapter."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info

    def get_icon_path(self, icon_names) -> Optional[str]:
        """Get icon path."""
        import os
        import sys

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

        return None

    def get_resource_path(self, resource_name: str) -> Optional[str]:
        """Get resource path."""
        import os
        import sys

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            resource_path = os.path.join(sys._MEIPASS, resource_name)
            if os.path.exists(resource_path):
                return resource_path

        if os.path.exists(resource_name):
            return resource_name

        return None

    def load_image(self, path: str) -> Any:
        """Load image."""
        try:
            from PIL import Image
            return Image.open(path)
        except:
            return path


class GenericNotificationAdapter(NotificationAdapter):
    """Generic notification adapter using custom sound file."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info

        # Path to custom sound file
        self._custom_sound = os.path.join(os.path.dirname(__file__), '..', 'assets', '029_Decline_09.wav')
        # Convert to absolute path
        self._custom_sound = os.path.abspath(self._custom_sound)

    def show_notification(self, title: str, message: str, duration: int = 5000) -> bool:
        """Show notification (not supported in generic adapter)."""
        return False

    def is_supported(self) -> bool:
        """Check if notifications are supported."""
        return False

    def play_notification_sound(self, sound_type: str = NotificationAdapter.SOUND_NOTIFICATION) -> bool:
        """Play a custom notification sound."""
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

        # Try to play with common players
        players = ['aplay', 'paplay', 'afplay', 'mplayer', 'vlc']

        for player in players:
            try:
                # Check if player is available
                subprocess.run(['which', player], capture_output=True, check=True)
                print(f"[DEBUG] Playing custom sound with {player}...")
                subprocess.Popen([player, self._custom_sound],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                return True
            except:
                continue

        # Fallback to terminal bell
        try:
            print('\a', end='', flush=True)
            return True
        except:
            return False


class AdapterFactory:
    """Factory for creating platform-specific adapters."""

    _adapter_map: Dict[str, Type] = {
        'Linux': LinuxAdapter,
        'Windows': WindowsAdapter,
        'Darwin': MacOSAdapter,  # macOS reports as Darwin
    }

    _instances: Dict[str, Any] = {}

    @classmethod
    def create_adapters(cls, platform_info: Optional[PlatformInfo] = None):
        """Create appropriate adapters for the current platform.

        Args:
            platform_info: Optional pre-detected platform info

        Returns:
            Adapter instance with keyboard, clipboard, system_tray, and resources
        """
        # Detect platform if not provided
        if platform_info is None:
            platform_info = PlatformDetector.detect()

        # Create cache key
        cache_key = f"{platform_info.os_name}_{platform_info.display_protocol}_{platform_info.desktop_environment}"

        # Return cached instance if available
        if cache_key in cls._instances:
            return cls._instances[cache_key]

        # Get adapter class for platform
        adapter_class = cls._adapter_map.get(platform_info.os_name, GenericAdapter)

        # Create and cache instance
        adapter = adapter_class(platform_info)
        adapter.initialize()

        cls._instances[cache_key] = adapter
        return adapter

    @classmethod
    def get_capabilities(cls, platform_info: Optional[PlatformInfo] = None) -> PlatformCapabilities:
        """Get platform capabilities.

        Args:
            platform_info: Optional pre-detected platform info

        Returns:
            PlatformCapabilities instance
        """
        if platform_info is None:
            platform_info = PlatformDetector.detect()

        return PlatformCapabilities(platform_info)

    @classmethod
    def clear_cache(cls):
        """Clear cached adapter instances."""
        cls._instances.clear()

    @classmethod
    def is_platform_supported(cls, platform_info: Optional[PlatformInfo] = None) -> bool:
        """Check if platform has dedicated support.

        Args:
            platform_info: Optional pre-detected platform info

        Returns:
            bool: True if platform has dedicated adapter
        """
        if platform_info is None:
            platform_info = PlatformDetector.detect()

        return platform_info.os_name in cls._adapter_map

    @classmethod
    def get_supported_platforms(cls) -> list:
        """Get list of supported platforms."""
        return list(cls._adapter_map.keys())