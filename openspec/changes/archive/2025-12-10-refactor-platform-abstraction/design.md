# Platform Abstraction Layer Design

## Context
The current implementation mixes platform-specific code with business logic, creating maintenance challenges and limiting extensibility. This design separates concerns through a clean abstraction layer.

## Goals / Non-Goals
- Goals:
  - Enable easy addition of new platform support
  - Improve testability through dependency injection
  - Reduce code duplication across platforms
  - Maintain backward compatibility
- Non-Goals:
  - Complete rewrite of existing functionality
  - Breaking changes to current API
  - Performance optimization (current performance is acceptable)

## Decisions
- Decision: Use Abstract Base Classes (ABCs) for platform interfaces
  - Rationale: Clear contracts, type hinting support, runtime validation
  - Alternatives considered: Protocol classes (duck typing), explicit inheritance

- Decision: Factory pattern for platform adapter instantiation
  - Rationale: Centralized creation logic, easy mocking for tests
  - Alternatives considered: Service locator, direct instantiation

- Decision: Separate packages per platform family
  - Rationale: Clear ownership, independent versioning, reduced coupling
  - Alternatives considered: Single file with conditionals, feature flags

## Architecture Overview

```
src/
├── platform_detection/
│   ├── __init__.py
│   ├── detector.py          # Platform detection logic
│   └── capabilities.py      # Feature availability
│
├── platform_adapters/
│   ├── __init__.py
│   ├── base.py             # Abstract interfaces
│   ├── factory.py          # Adapter factory
│   ├── linux/
│   │   ├── __init__.py
│   │   ├── adapter.py      # Linux implementation
│   │   ├── wayland.py      # Wayland-specific
│   │   └── x11.py          # X11-specific
│   ├── windows/
│   │   ├── __init__.py
│   │   └── adapter.py      # Windows implementation
│   └── macos/
│       ├── __init__.py
│       └── adapter.py      # macOS implementation
│
└── remote_server.py        # Refactored main server
```

## Interface Definitions

### KeyboardAdapter
```python
class KeyboardAdapter(ABC):
    @abstractmethod
    async def send_paste_command(self) -> bool:
        """Send paste command (Shift+Insert or Ctrl+V)"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if keyboard simulation is available"""
        pass
```

### ClipboardAdapter
```python
class ClipboardAdapter(ABC):
    @abstractmethod
    async def copy_text(self, text: str) -> bool:
        """Copy text to clipboard"""
        pass

    @abstractmethod
    def setup(self) -> None:
        """Initialize clipboard support"""
        pass
```

### SystemTrayAdapter
```python
class SystemTrayAdapter(ABC):
    @abstractmethod
    def create_tray_icon(self, menu_items: List[MenuItem]) -> bool:
        """Create system tray icon"""
        pass

    @abstractmethod
    def is_supported(self) -> bool:
        """Check if system tray is supported"""
        pass
```

## Risks / Trade-offs
- Risk: Increased complexity in package structure
  - Mitigation: Clear documentation, simple factory pattern
- Trade-off: More files to maintain
  - Benefit: Easier testing and modification
- Risk: Performance overhead from abstraction layer
  - Mitigation: Adapter instances created once at startup

## Migration Plan
1. Create new package structure
2. Move platform-specific code to adapters
3. Update main server to use factory
4. Run integration tests
5. Remove old platform-specific code
6. Update documentation

## Open Questions
- Should we use async/await for all adapter methods?
- How to handle partial platform support (e.g., clipboard but no tray)?
- Should adapters support fallback mechanisms?