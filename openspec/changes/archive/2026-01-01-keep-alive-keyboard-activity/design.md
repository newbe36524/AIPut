# Keep-Alive Keyboard Activity Design

## Context

AIPut 是一个运行在 Linux 桌面环境的无线语音输入工具。在 Fedora 系统上，当用户长时间不进行输入操作时，系统会弹出键盘输入相关的提示或检测通知。这会影响用户体验，因为需要手动关闭提示窗口，并可能导致 AIPut 的自动化输入被系统中断。

当前项目已经具备跨平台适配器架构，支持 X11 和 Wayland 显示服务器，并使用 `pyautogui` 等库实现键盘模拟功能。我们需要在此基础上实现一个后台保持激活机制。

## Goals / Non-Goals

**Goals:**
- 实现跨平台的保持激活机制，防止系统检测到空闲状态
- 使用通用的 `keep_alive()` 接口，允许各平台选择最合适的实现方式
- Linux 平台（特别是 Fedora/KDE）使用 Scroll Lock 按键实现
- 使用独立线程实现，避免阻塞主服务
- 支持可配置的触发间隔
- 确保与 X11/Wayland 的兼容性

**Non-Goals:**
- 修改系统电源管理设置（不涉及 suspend/hibernate）
- 防止屏幕锁定或屏保启动
- 鼠标移动模拟（只使用键盘事件）
- 复杂的空闲检测逻辑（使用固定间隔触发）
- 强制所有平台使用相同的实现方式

## Decisions

### Decision 1: 使用通用接口名 `keep_alive()`

**选择理由：**
- 接口名应该描述功能意图而非具体实现
- 不同平台可能需要不同的保持激活策略
- Linux (Fedora/KDE) 使用 Scroll Lock 是针对该平台的最佳实践
- 其他平台可以返回 False（表示不需要此功能）或采用其他实现

**架构优势：**
```python
# 基类定义通用接口
class KeyboardAdapter(ABC):
    @abstractmethod
    async def keep_alive(self) -> bool:
        """Keep system active to prevent idle detection.

        Each platform adapter decides the best implementation:
        - Linux: Scroll Lock key (twice)
        - Windows/macOS: May not need this, return False

        Returns:
            bool: True if keep-alive was performed, False otherwise.
        """
        pass

# Linux 实现
class LinuxKeyboardAdapter:
    async def keep_alive(self) -> bool:
        # 使用 Scroll Lock 实现
        return await self._send_scroll_lock_twice()

# Windows 实现
class WindowsKeyboardAdapter:
    async def keep_alive(self) -> bool:
        # Windows 可能不需要此功能
        return False
```

### Decision 2: Linux 平台使用 Scroll Lock 按键

**选择理由：**
- Scroll Lock 在日常使用中极少被触发
- 对系统状态影响最小（不像 Caps Lock 或 Num Lock 会影响输入）
- 不会干扰正在运行的应用程序
- 跨平台支持良好（xdotool, wtype, ydotool 都支持）

**其他考虑方案：**
- F15/F24 等功能键：虽然更少被使用，但在某些键盘上可能不存在
- 组合键（如 Ctrl+Shift）：可能触发系统快捷键

### Decision 3: 连续按下两次 Scroll Lock

**选择理由：**
- 一次按下可能被某些系统忽略
- 两次按下可以确保系统检测到键盘活动
- 不会造成任何副作用（Scroll Lock 本身很少被应用使用）

**触发时机：**
- 启动时立即触发一次
- 之后每隔 5 分钟自动触发一次

### Decision 4: 使用独立后台线程

**选择理由：**
- 不阻塞主服务线程
- 简单可靠的定时实现
- 易于启动和停止
- 使用 `threading.Event` 实现优雅关闭

**替代方案：**
- `asyncio.create_task()`: 需要将整个服务改为异步模式
- `threading.Timer`: 需要在每次触发后重新创建定时器
- 外部 cron 任务：增加部署复杂度

### Decision 5: 默认 5 分钟间隔

**选择理由：**
- Fedora 系统的空闲检测通常在 5-10 分钟后触发
- 5 分钟间隔足以防止系统检测到空闲
- 资源开销极低，不会影响性能

**可配置性：**
- 通过环境变量 `AIPUT_KEEP_ALIVE_INTERVAL` 配置
- 最小值：1 分钟（防止过于频繁的键盘事件）
- 单位：秒

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Remote Server                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────┐        ┌─────────────────────────────┐   │
│  │ Main Service  │        │   Keep-Alive Thread         │   │
│  │   (Flask)     │        │                             │   │
│  └───────────────┘        │  ┌───────────────────────┐  │   │
│                           │  │  Timer Loop            │  │   │
│                           │  │  (every 5 min)         │  │   │
│                           │  └───────────┬───────────┘  │   │
│                           │              │               │   │
│                           │  ┌───────────▼───────────┐  │   │
│                           │  │  keep_alive()         │  │   │
│                           │  └───────────────────────┘  │   │
│                           │                             │   │
│                           └──────────────┬──────────────┘   │
│                                          │                   │
│                                          ▼                   │
│                           ┌─────────────────────────────────┐│
│                           │     Platform Adapter Factory    ││
│                           ├─────────────────────────────────┤│
│                           │  ┌──────────────────────────┐  ││
│                           │  │  KeyboardAdapter         │  ││
│                           │  │  ┌────────────────────┐  │  ││
│                           │  │  │ keep_alive()       │  │  ││
│                           │  │  │ (generic method)   │  │  ││
│                           │  │  └────────────────────┘  │  ││
│                           │  └──────────────────────────┘  ││
│                           └─────────────────────────────────┘│
│                                          │                   │
│                                          ▼                   │
│                           ┌─────────────────────────────────┐│
│                           │    Platform Implementations     ││
│                           ├─────────────────────────────────┤│
│                           │  • Linux (X11/Wayland)         ││
│                           │    → keep_alive(): Scroll Lock  ││
│                           │  • Windows                     ││
│                           │    → keep_alive(): False/other  ││
│                           │  • macOS                       ││
│                           │    → keep_alive(): False/other  ││
│                           └─────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Interface Definition

### KeyboardAdapter Extension

```python
class KeyboardAdapter(ABC):
    # ... existing methods ...

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
```

### Keep-Alive Thread Implementation

```python
class KeepAliveThread(threading.Thread):
    """Background thread that calls keep_alive() periodically."""

    def __init__(self, keyboard_adapter: KeyboardAdapter, interval: int = 300):
        """Initialize keep-alive thread.

        Args:
            keyboard_adapter: Platform keyboard adapter for keep-alive.
            interval: Trigger interval in seconds (default: 300 = 5 minutes).
        """
        super().__init__(daemon=True)
        self._keyboard_adapter = keyboard_adapter
        self._interval = interval
        self._stop_event = threading.Event()
        self._loop = asyncio.new_event_loop()

    def run(self):
        """Run the keep-alive loop."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._keep_alive_loop())

    async def _keep_alive_loop(self):
        """Keep-alive loop that triggers keep_alive() periodically."""
        # Immediate trigger on startup
        await self._trigger_keep_alive()

        while not self._stop_event.is_set():
            # Wait for interval or stop event
            self._stop_event.wait(self._interval)
            if self._stop_event.is_set():
                break
            await self._trigger_keep_alive()

    async def _trigger_keep_alive(self):
        """Trigger keep-alive action."""
        try:
            result = await self._keyboard_adapter.keep_alive()
            if result:
                logger.debug("Keep-alive triggered successfully")
            else:
                logger.debug("Keep-alive not supported or not needed on this platform")
        except Exception as e:
            logger.warning(f"Keep-alive trigger failed: {e}")

    def stop(self):
        """Stop the keep-alive thread gracefully."""
        self._stop_event.set()
        self.join(timeout=5)
```

## Platform-Specific Implementations

### Linux (X11/Wayland) - Scroll Lock Implementation

#### X11KeyboardAdapter
```python
async def keep_alive(self) -> bool:
    """Send Scroll Lock twice using X11 tools."""
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

    return False
```

#### WaylandKeyboardAdapter
```python
async def keep_alive(self) -> bool:
    """Send Scroll Lock twice using Wayland tools."""
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
```

### Windows - Optional Implementation

```python
async def keep_alive(self) -> bool:
    """Keep-alive implementation for Windows.

    Windows may not need this functionality, but can implement
    using Scroll Lock if needed.
    """
    # Option 1: Return False if not needed
    # return False

    # Option 2: Implement using Scroll Lock
    if 'pyautogui' in self._methods:
        try:
            pyautogui.press('scrolllock')
            await asyncio.sleep(0.1)
            pyautogui.press('scrolllock')
            return True
        except Exception:
            pass

    return False
```

### macOS - Optional Implementation

```python
async def keep_alive(self) -> bool:
    """Keep-alive implementation for macOS.

    macOS may not need this functionality, but can implement
    using Scroll Lock if needed.
    """
    # Option 1: Return False if not needed
    # return False

    # Option 2: Implement using Scroll Lock
    if 'pyautogui' in self._methods:
        try:
            pyautogui.press('scrolllock')
            await asyncio.sleep(0.1)
            pyautogui.press('scrolllock')
            return True
        except Exception:
            pass

    return False
```

## Configuration

### Environment Variables

| Variable | Description | Default | Minimum |
|----------|-------------|---------|---------|
| `AIPUT_KEEP_ALIVE_ENABLED` | Enable/disable keep-alive feature | `true` | - |
| `AIPUT_KEEP_ALIVE_INTERVAL` | Trigger interval in seconds | `300` | `60` |

### Configuration File (optional)

```yaml
keep_alive:
  enabled: true
  interval_seconds: 300
```

## Risks / Trade-offs

### Risk 1: Scroll Lock 可能影响某些应用

**描述：** 某些应用可能监听 Scroll Lock 按键（如某些屏幕阅读器或专业软件）。

**缓解措施：**
- Scroll Lock 在现代应用中极少被使用
- 连续按下两次的模式可以避免误触发
- 如果问题严重，可以添加白名单机制

### Risk 2: 5 分钟间隔可能不够频繁

**描述：** 某些系统可能在更短的时间（如 3 分钟）后检测空闲。

**缓解措施：**
- 提供可配置的间隔时间
- 文档说明如何调整间隔
- 默认 5 分钟适用于大多数情况

### Risk 3: 其他平台可能不需要此功能

**描述：** Windows 和 macOS 可能没有类似 Fedora 的空闲检测问题。

**缓解措施：**
- 使用通用的 `keep_alive()` 接口
- 允许平台适配器返回 False 表示不需要
- Linux 平台实现 Scroll Lock，其他平台可选择实现

### Trade-off: 额外的后台线程

**描述：** 增加了一个后台线程，增加了代码复杂度。

**收益：**
- 不阻塞主服务
- 简单可靠的实现
- 资源开销极低（每 5 分钟一次操作）

## Migration Plan

1. **Phase 1: Add abstract method to base adapter**
   - Update `KeyboardAdapter` base class with `keep_alive()` method
   - Document that each platform chooses its implementation

2. **Phase 2: Implement platform-specific methods**
   - Linux: Implement `keep_alive()` using Scroll Lock
   - Windows/macOS: Implement stub returning False

3. **Phase 3: Add keep-alive thread**
   - Create `KeepAliveThread` class
   - Integrate with main server lifecycle

4. **Phase 4: Add configuration support**
   - Add environment variable parsing
   - Add validation for interval values

5. **Phase 5: Testing**
   - Test on Linux (X11/Wayland/KDE/Fedora)
   - Verify system idle prevention
   - Test that other platforms return False gracefully

6. **Phase 6: Documentation**
   - Update README
   - Document that implementation varies by platform
   - Add troubleshooting section

## Open Questions

1. **是否需要在 GUI 中显示 keep-alive 状态？**
   - 建议：先实现基础功能，后续根据用户反馈决定

2. **是否需要日志记录 keep-alive 触发？**
   - 建议：添加 debug 级别的日志，方便排查问题

3. **如果 keep-alive 失败，是否需要通知用户？**
   - 建议：只在失败时记录 warning 日志，不打扰用户

4. **Windows 和 macOS 是否需要实现？**
   - 建议：先返回 False，如果用户反馈需要再实现

5. **是否需要支持不同的保持激活策略？**
   - 建议：先使用 Scroll Lock（Linux），如果用户反馈有问题，再考虑添加配置选项
