# Change: Add Sound Notifications for Text Sent Events

## Why
Users want audio feedback when text is successfully sent to the target application, providing immediate confirmation without relying on visual notifications that appear in the system tray.

## What Changes
- Extend the existing `NotificationAdapter` base class to support sound playback
- Implement platform-specific sound playback for Windows, macOS, and Linux
- Integrate sound notification trigger after successful text sending operations
- Use built-in system notification sounds (no external audio files required)
- Ensure cross-platform compatibility using the existing platform abstraction layer

## Interaction Flow

```mermaid
flowchart TD
    A[用户输入文本到文本框] --> B[点击发送按钮/按Enter]
    B --> C{文本是否成功发送?}
    C -->|是| D[播放系统通知声音]
    C -->|否| E[显示错误提示]
    D --> F[文本显示在目标应用中]
    E --> G[保持焦点在当前文本框]

    style D fill:#90EE90
    style A fill:#E0E0E0
    style B fill:#E0E0E0
    style C fill:#FFE4B5
    style F fill:#E0E0E0
    style G fill:#FFB6C1
```

## Impact
- Affected specs: New capability `notifications` will be created
- Affected code:
  - `src/platform_adapters/base.py` - Add sound methods to NotificationAdapter
  - `src/platform_adapters/*/adapter.py` - Implement platform-specific sound playback
  - `src/remote_server.py` - Integrate sound notification trigger