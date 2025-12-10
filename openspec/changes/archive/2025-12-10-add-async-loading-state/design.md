## Context

The current text submission flow provides minimal feedback during AI processing. Based on code analysis:
- Frontend already has basic loading states ("发送中...", "AI处理中...")
- Backend processes requests synchronously but may have long delays for AI processing
- No mechanism prevents users from submitting multiple times during processing
- Loading states are only shown in the status bar, not prominently near the input

## Goals / Non-Goals

**Goals:**
- Provide clear visual feedback during text submission and AI processing
- Prevent duplicate submissions during processing
- Improve user experience with prominent loading indicators
- Maintain current functionality while adding better state management

**Non-Goals:**
- Complete architectural overhaul to async processing (keep current sync model)
- Adding WebSocket support (unnecessary for current sync pattern)
- Modifying core AI processing logic

## Decisions

### 1. Loading State Strategy
**Decision:** Enhance existing synchronous pattern with better UI feedback
- Keep current synchronous API calls
- Add prominent loading overlay on the input area
- Show progress indicators for different stages (sending, AI processing)

### 2. UI Implementation Approach
**Decision:** Use CSS overlays and state management
- Add loading overlay div positioned over the textarea
- Use CSS animations for visual appeal
- Implement state flags to track submission phases

### 3. Duplicate Submission Prevention
**Decision:** Disable interactive elements during processing
- Disable textarea and submit button during processing
- Re-enable only after completion or error
- Maintain focus management for better UX

## Alternatives Considered

1. **WebSocket Implementation**
   - Pros: Real-time updates, better for long operations
   - Cons: Complex, requires backend changes, overkill for current needs
   - Decision: Not necessary given current synchronous processing

2. **Polling Approach**
   - Pros: Simpler than WebSocket
   - Cons: Still requires async backend support
   - Decision: Adds complexity without clear benefits

3. **Minimal Status Bar Updates**
   - Pros: Simple change
   - Cons: Not prominent enough, users might miss
   - Decision: Users need clear, obvious feedback

## Risks / Trade-offs

- **Risk**: Loading overlay might be perceived as blocking
  - **Mitigation**: Use semi-transparent overlay, keep text visible
- **Risk**: Disabling input might frustrate users
  - **Mitigation**: Clear messaging, quick responses for non-AI operations
- **Trade-off**: Slightly more complex frontend code for much better UX

## Migration Plan

1. Add HTML elements for loading overlay
2. Implement CSS styles for loading states
3. Update JavaScript to manage loading states
4. Add form disabling logic during processing
5. Test with various prompt types and processing times
6. Ensure graceful fallback on JavaScript errors

## Open Questions

- Should different AI processing modes show different loading messages?
- Should there be a timeout after which users can cancel the operation?
- Should history be accessible during loading states?