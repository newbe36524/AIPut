"""
Platform detection package for identifying OS, display environment, and capabilities.
"""

from .detector import PlatformDetector, PlatformInfo
from .capabilities import PlatformCapabilities

__all__ = [
    'PlatformDetector',
    'PlatformInfo',
    'PlatformCapabilities'
]