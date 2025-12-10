"""
Platform capabilities detection and reporting.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from .detector import PlatformInfo


@dataclass
class FeatureSupport:
    """Represents support level for a feature."""
    SUPPORTED = 'supported'
    PARTIAL = 'partial'
    NOT_SUPPORTED = 'not_supported'
    UNKNOWN = 'unknown'


class PlatformCapabilities:
    """Manages and reports platform capabilities."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._capabilities_cache: Optional[Dict[str, str]] = None

    def get_keyboard_simulation_support(self) -> str:
        """Check keyboard simulation support level."""
        if self.platform_info.os_name == 'Windows':
            return FeatureSupport.SUPPORTED
        elif self.platform_info.os_name == 'Darwin':
            return FeatureSupport.SUPPORTED
        elif self.platform_info.os_name == 'Linux':
            tools = self.platform_info.additional_info.get('keyboard_tools', [])
            if tools:
                if self.platform_info.display_protocol == 'Wayland':
                    # Wayland has limited support
                    if 'wtype' in tools or 'ydotool' in tools:
                        return FeatureSupport.PARTIAL
                    else:
                        return FeatureSupport.NOT_SUPPORTED
                else:
                    return FeatureSupport.SUPPORTED
            else:
                return FeatureSupport.NOT_SUPPORTED
        return FeatureSupport.UNKNOWN

    def get_clipboard_support(self) -> str:
        """Check clipboard support level."""
        if self.platform_info.os_name == 'Windows':
            return FeatureSupport.SUPPORTED
        elif self.platform_info.os_name == 'Darwin':
            return FeatureSupport.SUPPORTED
        elif self.platform_info.os_name == 'Linux':
            tools = self.platform_info.additional_info.get('clipboard_tools', [])
            if tools:
                return FeatureSupport.SUPPORTED
            else:
                return FeatureSupport.PARTIAL  # Can use pyperclip as fallback
        return FeatureSupport.UNKNOWN

    def get_system_tray_support(self) -> str:
        """Check system tray support level."""
        # Check if pystray is available
        has_pystray = self.platform_info.additional_info.get('pystray_available', False)

        if not has_pystray:
            return FeatureSupport.NOT_SUPPORTED

        if self.platform_info.os_name == 'Linux':
            # Wayland has limited tray support
            if self.platform_info.display_protocol == 'Wayland':
                return FeatureSupport.PARTIAL
            return FeatureSupport.SUPPORTED
        elif self.platform_info.os_name in ['Windows', 'Darwin']:
            return FeatureSupport.SUPPORTED

        return FeatureSupport.UNKNOWN

    def get_resource_loading_support(self) -> str:
        """Check resource loading support level."""
        return FeatureSupport.SUPPORTED  # Basic file loading should work everywhere

    def get_recommended_approaches(self) -> Dict[str, List[str]]:
        """Get recommended approaches for each feature."""
        recommendations = {
            'keyboard_simulation': [],
            'clipboard': [],
            'system_tray': [],
            'resource_loading': []
        }

        if self.platform_info.os_name == 'Linux':
            if self.platform_info.display_protocol == 'Wayland':
                recommendations['keyboard_simulation'].extend([
                    'Use wtype if available',
                    'Try ydotool as fallback',
                    'Use KDE-specific workarounds if on KDE'
                ])
                recommendations['system_tray'].append(
                    'Consider tray may not work on Wayland'
                )
            else:
                recommendations['keyboard_simulation'].extend([
                    'Use xdotool as primary method',
                    'Try xte as fallback'
                ])

            if self.platform_info.desktop_environment == 'KDE':
                recommendations['keyboard_simulation'].append(
                    'KDE Wayland may support xdotool'
                )

            # Clipboard tools recommendation
            tools = self.platform_info.additional_info.get('clipboard_tools', [])
            if tools:
                recommendations['clipboard'].append(f"Available tools: {', '.join(tools)}")
            else:
                recommendations['clipboard'].append(
                    "Install xclip for X11 or wl-clipboard for Wayland"
                )

        elif self.platform_info.os_name == 'Windows':
            recommendations['keyboard_simulation'].append(
                "Use pyautogui or Windows API"
            )
            recommendations['clipboard'].append(
                "Use built-in Windows clipboard APIs"
            )

        elif self.platform_info.os_name == 'Darwin':
            recommendations['keyboard_simulation'].append(
                "Use pyautogui or AppleScript"
            )
            recommendations['clipboard'].append(
                "Use pbcopy/pbpaste or pyperclip"
            )

        recommendations['resource_loading'].append(
            "Use os.path for cross-platform compatibility"
        )

        return recommendations

    def get_all_capabilities(self) -> Dict[str, str]:
        """Get all capabilities in a dictionary."""
        if not self._capabilities_cache:
            self._capabilities_cache = {
                'keyboard_simulation': self.get_keyboard_simulation_support(),
                'clipboard': self.get_clipboard_support(),
                'system_tray': self.get_system_tray_support(),
                'resource_loading': self.get_resource_loading_support()
            }
        return self._capabilities_cache

    def supports_feature(self, feature: str) -> bool:
        """Check if a feature is supported (supported or partial)."""
        support_level = self.get_all_capabilities().get(feature, FeatureSupport.UNKNOWN)
        return support_level in [FeatureSupport.SUPPORTED, FeatureSupport.PARTIAL]

    def get_fallback_methods(self) -> Dict[str, List[str]]:
        """Get fallback methods for features with limited support."""
        fallbacks = {}

        if self.platform_info.os_name == 'Linux':
            if self.get_keyboard_simulation_support() != FeatureSupport.SUPPORTED:
                fallbacks['keyboard_simulation'] = [
                    'Ask user to manually paste',
                    'Use clipboard-only mode'
                ]

            if self.get_system_tray_support() != FeatureSupport.SUPPORTED:
                fallbacks['system_tray'] = [
                    'Keep window visible',
                    'Use minimize to taskbar'
                ]

        return fallbacks