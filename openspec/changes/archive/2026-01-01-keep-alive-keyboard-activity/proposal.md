# Change: Add Keep-Alive Keyboard Activity

**Status:** ExecutionCompleted

## Why

在 Fedora 系统上，当用户长时间不进行输入操作时，系统会弹出键盘输入相关的提示或检测通知，打断正常工作流程并需要手动关闭。这会影响 AIPut 的用户体验，特别是在需要长时间保持后台运行的情况下。

## What Changes

- 在 `KeyboardAdapter` 基类中添加 `keep_alive()` 抽象方法
  - 使用通用方法名 `keep_alive()` 而非具体实现名
  - 每个平台适配器根据自身特点选择最合适的保持激活实现方式
- 为所有平台适配器实现 `keep_alive()` 方法：
  - Linux (X11/Wayland/Fedora/KDE): 使用 Scroll Lock 按键（连续按下两次）
    - X11: 使用 xdotool/xte/xvkbd 模拟
    - Wayland: 使用 wtype/ydotool 模拟
    - KDE Wayland: 可使用 xdotool 通过 Xwayland
  - Windows/macOS: 预留接口，可根据需要实现（也可使用 Scroll Lock）
- 在主服务器中实现后台保持激活机制：
  - 启动时立即触发一次 keep-alive
  - 使用独立线程每隔 5 分钟自动触发一次
- 添加可配置的保持激活间隔时间（通过环境变量或配置文件）

## Impact

- Affected specs: `platform-abstraction`
- Affected code:
  - `src/platform_adapters/base.py` - 添加抽象方法 `keep_alive()`
  - `src/platform_adapters/linux/wayland.py` - 实现 `keep_alive()` (使用 Scroll Lock)
  - `src/platform_adapters/linux/x11.py` - 实现 `keep_alive()` (使用 Scroll Lock)
  - `src/platform_adapters/windows/adapter.py` - 实现 `keep_alive()` (预留)
  - `src/platform_adapters/macos/adapter.py` - 实现 `keep_alive()` (预留)
  - `src/remote_server.py` - 添加保持激活线程
