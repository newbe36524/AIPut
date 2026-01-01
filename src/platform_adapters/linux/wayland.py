"""
Wayland-specific keyboard adapter implementation.
"""

import asyncio
import os
import subprocess
from typing import List
from platform_detection.detector import PlatformInfo
from platform_adapters.base import KeyboardAdapter


class WaylandKeyboardAdapter(KeyboardAdapter):
    """Keyboard adapter for Wayland display protocol."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._is_kde = platform_info.desktop_environment == 'KDE'
        self._available_methods = []
        self._detect_methods()

    def _detect_methods(self):
        """Detect available Wayland keyboard simulation methods."""
        tools = self.platform_info.additional_info.get('keyboard_tools', [])

        # Check for Wayland-native tools
        if 'wtype' in tools:
            self._available_methods.append('wtype')
        if 'ydotool' in tools:
            self._available_methods.append('ydotool')

        # KDE Wayland might support xdotool through Xwayland
        if self._is_kde and 'xdotool' in tools:
            self._available_methods.append('xdotool (KDE Wayland)')

    async def send_paste_command(self) -> bool:
        """Send paste command using Wayland-compatible methods."""
        # Try xdotool first on KDE Wayland (最可靠的方法)
        if 'xdotool (KDE Wayland)' in self._available_methods:
            try:
                subprocess.run(['xdotool', 'key', 'shift+Insert'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try wtype (native Wayland, 但在某些 compositor 上可能不支持)
        if 'wtype' in self._available_methods:
            try:
                # wtype: -M shift -P Insert
                # wtype 会自动处理按键释放，不需要额外的命令
                subprocess.run(['wtype', '-M', 'shift', '-P', 'Insert'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try ydotool (works on Wayland)
        if 'ydotool' in self._available_methods:
            try:
                # ydotool key codes: 42=Shift, 118=Insert
                subprocess.run(['ydotool', 'key', '42:1', '118:1', '118:0', '42:0'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        return False

    async def send_ctrl_enter(self) -> bool:
        """Send Ctrl+Enter key combination using Wayland-compatible methods."""
        # Try xdotool first on KDE Wayland (最可靠的方法)
        if 'xdotool (KDE Wayland)' in self._available_methods:
            try:
                subprocess.run(['xdotool', 'key', 'Ctrl+Return'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try wtype (native Wayland)
        if 'wtype' in self._available_methods:
            try:
                # wtype: -M ctrl -P Return
                subprocess.run(['wtype', '-M', 'ctrl', '-P', 'Return'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try ydotool (works on Wayland)
        if 'ydotool' in self._available_methods:
            try:
                # ydotool key codes: 29=Ctrl, 28=Return
                subprocess.run(['ydotool', 'key', '29:1', '28:1', '28:0', '29:0'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        return False

    def is_available(self) -> bool:
        """Check if keyboard simulation is available on Wayland."""
        return bool(self._available_methods)

    def get_available_methods(self) -> List[str]:
        """Get list of available keyboard simulation methods."""
        return self._available_methods.copy()

    async def send_text(self, text: str) -> bool:
        """Send text directly using wtype if available."""
        if 'wtype' in self._available_methods:
            try:
                # wtype can type text directly
                subprocess.run(['wtype', text],
                             check=False, timeout=5)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass
        return False

    async def keep_alive(self) -> bool:
        """Send Scroll Lock twice using Wayland-compatible methods.

        Returns:
            bool: True if keep-alive was performed successfully, False otherwise.
        """
        # Try xdotool on KDE Wayland (via Xwayland)
        if 'xdotool (KDE Wayland)' in self._available_methods:
            try:
                subprocess.run(['xdotool', 'key', 'Scroll_Lock'],
                             check=False, timeout=1)
                await asyncio.sleep(0.1)
                subprocess.run(['xdotool', 'key', 'Scroll_Lock'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try wtype (native Wayland)
        if 'wtype' in self._available_methods:
            try:
                # wtype -P Scroll_Lock (press and release)
                subprocess.run(['wtype', '-P', 'Scroll_Lock'],
                             check=False, timeout=1)
                await asyncio.sleep(0.1)
                subprocess.run(['wtype', '-P', 'Scroll_Lock'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try ydotool
        if 'ydotool' in self._available_methods:
            try:
                # ydotool key code for Scroll Lock is 70
                subprocess.run(['ydotool', 'key', '70:1', '70:0'],
                             check=False, timeout=1)
                await asyncio.sleep(0.1)
                subprocess.run(['ydotool', 'key', '70:1', '70:0'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        return False