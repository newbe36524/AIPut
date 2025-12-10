## Context
The brave mode feature addresses user workflow efficiency by eliminating the manual step of pressing Ctrl+Enter after voice input. This "brave" approach is for users who want to confidently send messages immediately without hesitation. This is especially valuable for repetitive text entry scenarios like chat conversations, form filling, and command-line operations. The feature needs to be carefully designed to work across different platforms and applications while maintaining the simplicity and reliability of the existing system.

## Goals / Non-Goals
- Goals:
  - Provide seamless auto-submit functionality after voice input
  - Maintain cross-platform compatibility
  - Preserve existing workflow for users who don't need brave mode
  - Ensure reliable operation with configurable timing
  - Keep mode state purely on frontend side
- Non-Goals:
  - Implement complex auto-detection of when to send Ctrl+Enter
  - Add AI-powered text processing before submission
  - Create application-specific auto-mode behaviors
  - Store brave mode state on backend

## Decisions
- Decision: Add brave mode as optional toggle rather than default behavior
  - Reason: Preserves existing user experience, avoids unexpected behavior
  - Alternatives considered: Always-on auto-mode, gesture-based activation

- Decision: Use localStorage for frontend toggle persistence
  - Reason: Simple, reliable, no server-side storage needed
  - Alternatives considered: Server-side preferences, cookies

- Decision: Frontend controls mode state, backend receives auto_submit parameter
  - Reason: Clear separation of concerns, backend doesn't need to persist state
  - Alternatives considered: Backend state management, session storage

- Decision: Implement configurable delay between paste and Ctrl+Enter
  - Reason: Different applications need different timing for proper text registration
  - Alternatives considered: Fixed delay, application-specific delays

- Decision: Extend existing KeyboardAdapter interface rather than create new component
  - Reason: Leverages existing platform abstraction, maintains architectural consistency
  - Alternatives considered: Separate AutoSubmitAdapter, direct platform calls

## Technical Implementation

### Frontend Responsibilities
1. Store brave mode toggle state in localStorage
2. Include `auto_submit: true` in API requests when brave mode is ON
3. Handle toggle UI updates and state persistence
4. Restore toggle state on page load

### Backend Responsibilities
1. Accept `auto_submit` parameter in /type endpoint
2. Copy text to clipboard and send paste command (Ctrl+V)
3. If `auto_submit` is true, send Ctrl+Enter after configurable delay
4. No storage of brave mode state required

### API Contract
```javascript
// Frontend sends:
POST /type
{
  "text": "Hello world",
  "auto_submit": true  // Present only when brave mode is ON
}

// Backend behavior:
if (auto_submit === true) {
  // Copy text to clipboard
  // Send Ctrl+V to paste
  // Wait configurable delay (e.g., 100ms)
  // Send Ctrl+Enter key combination
} else {
  // Copy text to clipboard
  // Send Ctrl+V to paste only
}
```

## Risks / Trade-offs
- [Timing Issues] → Implement configurable delay with sensible defaults
- [Application Compatibility] → Test with common applications, provide user control
- [Platform Differences] → Use existing adapter pattern, thorough testing
- [Network Latency] → Frontend includes auto_submit in request, no additional round trips needed

## Migration Plan
- Add new auto_submit parameter as optional to existing API
- Maintain backward compatibility for existing API
- Default brave mode to disabled for all users
- No breaking changes to existing functionality

## Open Questions
- What should be the default delay between paste and Ctrl+Enter? (Initial: 100ms)
- Should we support different Ctrl+Enter key variants? (Ctrl+Return, Ctrl+NumPad Enter)
- How to handle cases where Ctrl+Enter key simulation fails? (Retry count, user notification)
- Should auto_submit be sent as false when brave mode is OFF, or omitted entirely? (Prefer omitted)