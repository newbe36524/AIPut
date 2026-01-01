"""
Abstract base classes for platform adapters.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class MenuItem:
    """Represents a menu item for system tray."""
    label: str
    action: Callable
    enabled: bool = True


class KeyboardAdapter(ABC):
    """Abstract interface for keyboard input simulation."""

    @abstractmethod
    async def send_paste_command(self) -> bool:
        """Send paste command (Shift+Insert or Ctrl+V).

        Returns:
            bool: True if command was sent successfully, False otherwise.
        """
        pass

    @abstractmethod
    async def send_ctrl_enter(self) -> bool:
        """Send Ctrl+Enter key combination.

        Returns:
            bool: True if command was sent successfully, False otherwise.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if keyboard simulation is available on this platform.

        Returns:
            bool: True if keyboard simulation is available.
        """
        pass

    @abstractmethod
    def get_available_methods(self) -> List[str]:
        """Get list of available keyboard simulation methods.

        Returns:
            List[str]: List of method names.
        """
        pass

    async def send_text(self, text: str) -> bool:
        """Send text directly (optional implementation).

        Args:
            text: Text to send.

        Returns:
            bool: True if text was sent successfully.
        """
        return False

    @abstractmethod
    async def keep_alive(self) -> bool:
        """Keep system active to prevent idle detection.

        This is a generic interface - each platform adapter decides
        the best implementation approach:

        - Linux (Fedora/KDE): Send Scroll Lock key twice
        - Windows/macOS: May return False if not needed

        Returns:
            bool: True if keep-alive action was performed successfully,
                  False if keep-alive is not needed or failed.
        """
        pass


class ClipboardAdapter(ABC):
    """Abstract interface for clipboard operations."""

    @abstractmethod
    async def copy_text(self, text: str) -> bool:
        """Copy text to clipboard.

        Args:
            text: Text to copy.

        Returns:
            bool: True if copied successfully.
        """
        pass

    @abstractmethod
    def setup(self) -> None:
        """Initialize clipboard support. Called once at startup."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if clipboard operations are available.

        Returns:
            bool: True if clipboard is available.
        """
        pass

    @abstractmethod
    def get_preferred_tool(self) -> Optional[str]:
        """Get the preferred clipboard tool being used.

        Returns:
            Optional[str]: Name of the tool or None if using generic method.
        """
        pass


class SystemTrayAdapter(ABC):
    """Abstract interface for system tray integration."""

    @abstractmethod
    def create_tray_icon(self, menu_items: List[MenuItem]) -> bool:
        """Create system tray icon with menu.

        Args:
            menu_items: List of menu items to show.

        Returns:
            bool: True if tray icon was created successfully.
        """
        pass

    @abstractmethod
    def is_supported(self) -> bool:
        """Check if system tray is supported on this platform.

        Returns:
            bool: True if system tray is supported.
        """
        pass

    @abstractmethod
    def hide_window(self) -> None:
        """Hide the main window."""
        pass

    @abstractmethod
    def show_window(self) -> None:
        """Show the main window."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the tray icon and clean up resources."""
        pass

    def update_tooltip(self, tooltip: str) -> None:
        """Update the tray icon tooltip.

        Args:
            tooltip: New tooltip text.
        """
        pass  # Optional implementation


class ResourceAdapter(ABC):
    """Abstract interface for resource management."""

    @abstractmethod
    def get_icon_path(self, icon_names: List[str]) -> Optional[str]:
        """Get path to icon file.

        Args:
            icon_names: List of preferred icon names (e.g., ['icon.png', 'icon.ico']).

        Returns:
            Optional[str]: Path to found icon file.
        """
        pass

    @abstractmethod
    def get_resource_path(self, resource_name: str) -> Optional[str]:
        """Get path to any resource file.

        Args:
            resource_name: Name of the resource file.

        Returns:
            Optional[str]: Path to resource file.
        """
        pass

    @abstractmethod
    def load_image(self, path: str) -> Any:
        """Load an image file.

        Args:
            path: Path to image file.

        Returns:
            Image object (platform-specific).
        """
        pass

    def get_app_data_dir(self) -> Optional[str]:
        """Get application data directory for storing user data.

        Returns:
            Optional[str]: Path to app data directory.
        """
        return None  # Optional implementation


class NotificationAdapter(ABC):
    """Abstract interface for system notifications."""

    # Sound notification types
    SOUND_NOTIFICATION = "notification"

    @abstractmethod
    def show_notification(self, title: str, message: str, duration: int = 5000) -> bool:
        """Show a system notification.

        Args:
            title: Notification title.
            message: Notification message.
            duration: Duration in milliseconds.

        Returns:
            bool: True if notification was shown successfully.
        """
        pass

    @abstractmethod
    def is_supported(self) -> bool:
        """Check if notifications are supported.

        Returns:
            bool: True if notifications are supported.
        """
        pass

    @abstractmethod
    def play_notification_sound(self, sound_type: str = SOUND_NOTIFICATION) -> bool:
        """Play a system notification sound.

        Args:
            sound_type: Type of sound to play (e.g., SOUND_NOTIFICATION).

        Returns:
            bool: True if sound was played successfully, False otherwise.
        """
        pass