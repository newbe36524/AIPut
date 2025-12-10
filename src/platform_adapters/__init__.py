"""
Platform adapters package providing cross-platform abstractions.
"""

from .base import (
    KeyboardAdapter,
    ClipboardAdapter,
    SystemTrayAdapter,
    ResourceAdapter
)
from .factory import AdapterFactory

__all__ = [
    'KeyboardAdapter',
    'ClipboardAdapter',
    'SystemTrayAdapter',
    'ResourceAdapter',
    'AdapterFactory'
]