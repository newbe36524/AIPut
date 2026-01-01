"""
X11-specific keyboard adapter implementation.
"""

import asyncio
import os
import subprocess
from typing import List
from platform_detection.detector import PlatformInfo
from platform_adapters.base import KeyboardAdapter


class X11KeyboardAdapter(KeyboardAdapter):
    """Keyboard adapter for X11 display protocol."""

    def __init__(self, platform_info: PlatformInfo):
        self.platform_info = platform_info
        self._available_methods = []
        self._detect_methods()

    def _detect_methods(self):
        """Detect available X11 keyboard simulation methods."""
        tools = self.platform_info.additional_info.get('keyboard_tools', [])

        # Check for X11 tools (只检查工具是否存在，不测试 X11 连接)
        # 工具检测已经在 detector.py 中完成，这里直接使用结果
        if 'xdotool' in tools:
            self._available_methods.append('xdotool')
        if 'xte' in tools:
            self._available_methods.append('xte')
        if 'xvkbd' in tools:
            self._available_methods.append('xvkbd')

    async def send_paste_command(self) -> bool:
        """Send paste command using X11-compatible methods."""
        # Try xdotool first (most reliable)
        if 'xdotool' in self._available_methods:
            try:
                subprocess.run(['xdotool', 'key', 'Shift+Insert'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try xte (xautomation package)
        if 'xte' in self._available_methods:
            try:
                subprocess.run(['xte', 'key Shift_L Insert'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try xvkbd
        if 'xvkbd' in self._available_methods:
            try:
                subprocess.run(['xvkbd', '-text', r'\[Shift]\[Insert]'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        return False

    async def send_ctrl_enter(self) -> bool:
        """Send Ctrl+Enter key combination using X11-compatible methods."""
        # Try xdotool first (most reliable)
        if 'xdotool' in self._available_methods:
            try:
                subprocess.run(['xdotool', 'key', 'Ctrl+Return'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try xte (xautomation package)
        if 'xte' in self._available_methods:
            try:
                subprocess.run(['xte', 'key Control_L Return'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try xvkbd
        if 'xvkbd' in self._available_methods:
            try:
                subprocess.run(['xvkbd', '-text', r'\[Control]\[Return]'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        return False

    def is_available(self) -> bool:
        """Check if keyboard simulation is available on X11."""
        return bool(self._available_methods)

    def get_available_methods(self) -> List[str]:
        """Get list of available keyboard simulation methods."""
        return self._available_methods.copy()

    async def send_text(self, text: str) -> bool:
        """Send text directly using X11 tools."""
        # Try xdotool for typing
        if 'xdotool' in self._available_methods:
            try:
                # xdotool type --delay 50 "text"
                subprocess.run(['xdotool', 'type', '--delay', '50', text],
                             check=False, timeout=5)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try xte for typing
        if 'xte' in self._available_methods:
            try:
                # xte types with built-in delay
                subprocess.run(['xte', f'type {text}'],
                             check=False, timeout=5)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        return False

    async def keep_alive(self) -> bool:
        """Send Scroll Lock twice using X11-compatible methods.

        Returns:
            bool: True if keep-alive was performed successfully, False otherwise.
        """
        # Try xdotool
        if 'xdotool' in self._available_methods:
            try:
                subprocess.run(['xdotool', 'key', 'Scroll_Lock'],
                             check=False, timeout=1)
                await asyncio.sleep(0.1)
                subprocess.run(['xdotool', 'key', 'Scroll_Lock'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try xte
        if 'xte' in self._available_methods:
            try:
                subprocess.run(['xte', 'key Scroll_Lock'],
                             check=False, timeout=1)
                await asyncio.sleep(0.1)
                subprocess.run(['xte', 'key Scroll_Lock'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        # Try xvkbd
        if 'xvkbd' in self._available_methods:
            try:
                subprocess.run(['xvkbd', '-text', '\\[Scroll_Lock]'],
                             check=False, timeout=1)
                await asyncio.sleep(0.1)
                subprocess.run(['xvkbd', '-text', '\\[Scroll_Lock]'],
                             check=False, timeout=1)
                return True
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass

        return False