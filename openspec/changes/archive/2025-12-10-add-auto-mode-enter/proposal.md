# Change: Add Brave Mode with Automatic Ctrl+Enter

## Why
Users want to streamline voice input workflows by automatically submitting text with Ctrl+Enter after pasting, eliminating the need to manually press Ctrl+Enter after each voice input. This "brave" mode is for users who want to confidently send messages immediately after voice input without hesitation. This is particularly useful for chat applications, form submissions, and command-line interfaces where immediate text submission is the common pattern.

## What Changes
- Add brave mode toggle in mobile web interface (frontend-controlled)
- Extend backend API to support auto-submit parameter
- Enhance platform adapters with Ctrl+Enter key simulation
- Frontend stores brave mode preference in localStorage

## UI Design Changes

### Mobile Web Interface - Before/After

```
┌─────────────────────────────────────┐
│ ☰                清空  发送  ← Header│
├─────────────────────────────────────┤
│                                     │
│  [Text Input Area]                  │
│  +-------------------------------+  │
│  |                               |  │
│  | Voice input text appears...   │  │
│  |                               |  │
│  +-------------------------------+  │
│                                     │
│ [Status Message]                    │
│                                     │
└─────────────────────────────────────┘
              ↑ CURRENT


┌─────────────────────────────────────┐
│ ☰          勇敢模式 清空  发送      │
│            [ OFF ]                 │ ← Header with Brave Mode
├─────────────────────────────────────┤
│                                     │
│  [Text Input Area]                  │
│  +-------------------------------+  │
│  |                               |  │
│  | Voice input text appears...   │  │
│  |                               |  │
│  +-------------------------------+  │
│                                     │
│ [Status Message]                    │
│                                     │
└─────────────────────────────────────┘
              ↑ AFTER (BRAVE MODE OFF)


┌─────────────────────────────────────┐
│ ☰          勇敢模式 清空  发送      │
│            [ ON ]                  │ ← Header with Brave Mode ON
├─────────────────────────────────────┤
│                                     │
│  [Text Input Area]                  │
│  +-------------------------------+  │
│  |                               |  │
│  | "Hello world"                 │  │
│  | (Auto-Ctrl+Enter will trigger)│  │
│  +-------------------------------+  │
│                                     │
│ [Status: Text sent!]               │
│                                     │
└─────────────────────────────────────┘
              ↑ AFTER (BRAVE MODE ON)
```

### Toggle Switch Design (in Header)

The toggle will be integrated into the header between the menu button and action buttons:

**Option 1: Inline Toggle**
```
☰  勇敢模式: [ OFF ]  清空  发送
     └─────┬─────┘
           └─ Small switch in header
```

**Option 2: Compact Switch**
```
☰  ●─ 勇敢模式 ─○  清空  发送
    └─ Small inline toggle ┘
```

### Implementation Details

1. **Frontend Control**: Brave mode toggle is purely frontend, stored in localStorage
2. **API Integration**: When sending text, include `auto_submit: true` parameter if brave mode is ON
3. **Backend Logic**: Backend checks `auto_submit` parameter and automatically triggers Ctrl+Enter if true
4. **Visual Design**: Small, unobtrusive toggle that doesn't disrupt existing layout
5. **Responsive**: Toggle adjusts size on different screen sizes
6. **When ON**: Automatically sends Ctrl+Enter after voice input pasting
7. **When OFF**: Requires manual Ctrl+Enter or Send button click

## API Changes

### Enhanced POST /type Endpoint
```json
{
  "text": "Hello world",
  "auto_submit": true  // New parameter - indicates if Ctrl+Enter should be triggered
}
```

### Implementation Flow
1. Client sends POST /type with text and auto_submit parameter
2. Backend copies text to clipboard
3. Backend sends paste command (Ctrl+V)
4. If auto_submit is true, backend sends Ctrl+Enter after configurable delay

## Impact
- Affected specs: mobile-ui
- Affected code:
  - src/remote_server.py (backend endpoint to handle auto_submit parameter)
  - site/app.js (frontend toggle, localStorage, and API request handling)
  - src/platform_adapters/base.py (Ctrl+Enter key method)
  - All platform adapters (Ctrl+Enter key implementation)
- No backend storage required for brave mode state