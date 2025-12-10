# Change: Redesign Mobile UI with Input-Focused Layout

## Why
The current mobile web interface has multiple UI elements (title, buttons, history) competing for attention, making the input box feel small and secondary. For a voice input tool where text entry is the primary function, the input box should dominate the interface to provide optimal user experience and fast input workflow.

## What Changes
- **Input Box Expansion**: Make the text input fill most of the screen viewport
- **Quick Action Buttons**: Keep Send and Clear buttons below the input box for easy access
- **Hamburger Menu**: Move history and other secondary functions into a collapsible top-left menu
- **History Integration**: The history list will be fully integrated inside the menu panel with scrollable view
- **Auto-focus Management**: Ensure input stays focused unless interacting with buttons or menu
- **Gesture Support**: Add swipe gestures for quick actions (e.g., swipe to send)
- **Visual Hierarchy**: Remove title and decorative elements to maximize input space

## UI Design Overview

### Current Layout (Before)
```
┌─────────────────────┐
│    电脑远程输入板    │
├─────────────────────┤
│  ┌───────────────┐  │
│  │  输入框        │  │
│  └───────────────┘  │
│  ┌─────────┬───────┐│
│  │ 清空    │ 发送  ││
│  └─────────┴───────┘│
│                     │
│  最近记录           │
│  • 文本1          │
│  • 文本2          │
│  • ...            │
└─────────────────────┘
```

### New Layout (After)
```
Menu Closed:
┌─────────────────────┐
│ ☰                  │ ← Hamburger Menu
│                     │
│  ┌───────────────┐  │
│  │               │  │
│  │               │  │
│  │   大输入框     │  │ ← 占据70%屏幕
│  │               │  │
│  │               │  │
│  └───────────────┘  │
│  ┌─────────┬───────┐│
│  │ 清空    │ 发送  ││ ← 快捷按钮
│  └─────────┴───────┘│
└─────────────────────┘

Menu Open:
┌─────────────────────┐
│ ☰ X    ←菜单          │
├─────────────────────┤
│ ┌─────────────────┐ │ ← 半透明遮罩
│ │ 最近记录        │ │
│ │ • 文本1 >       │ │ ← 可点击重发
│ │ • 文本2 >       │ │
│ │ • ...           │ │
│ │                 │ │
│ │ ─────────────── │ │
│ │ 清空历史        │ │
│ └─────────────────┘ │
└─────────────────────┘
```
Key Design Changes:
- Input box occupies ~70% of viewport (leaving space for buttons)
- Send/Clear buttons stay on main screen below input for easy access
- Only history and secondary functions move to menu
- Buttons optimized for thumb reach in portrait mode

## Impact
- Affected specs: `mobile-ui` (new capability)
- Affected code: `src/templates/index.html`, related CSS and JavaScript
- Breaking: Yes - complete UI restructuring that changes user interaction patterns
- Dependencies: None - uses existing browser APIs