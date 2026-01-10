# Change: Mobile Header Fixed Positioning

**Status: ExecutionCompleted**

## Why

The mobile web interface header (`.header`) currently scrolls out of view when users scroll through content or when the virtual keyboard is displayed. This prevents users from accessing header buttons (menu, prompt selector, clear/send actions) and creates a poor user experience on mobile devices.

## What Changes

- Set `.header` position to `fixed` to keep it anchored at the top of the viewport
- Add `top: 0` and `width: 100%` to ensure proper positioning
- Set appropriate `z-index` to maintain layer ordering above content
- Add `padding-top` to `.main-content` to prevent content from being hidden behind the fixed header
- Ensure responsive behavior across different screen sizes and orientations

## Impact

- Affected specs: `mobile-ui`
- Affected code:
  - `site/style.css` - Header and main content area styling
