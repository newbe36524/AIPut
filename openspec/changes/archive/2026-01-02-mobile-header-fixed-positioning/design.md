# Design: Mobile Header Fixed Positioning

## Context

The AIPut mobile web interface uses a simple HTML/CSS/JavaScript stack served by Flask. The current layout uses flexbox with the header as a normal flow element, which causes it to scroll with content. This is a common mobile UX pattern that needs to be fixed.

## Goals / Non-Goals

**Goals:**
- Keep header permanently visible at the top of the viewport
- Maintain all existing header functionality (menu, prompt selector, buttons)
- Ensure content is not obscured by the fixed header
- Preserve responsive design for different screen sizes

**Non-Goals:**
- No changes to header content or HTML structure
- No JavaScript changes required
- No changes to side menu behavior

## Decisions

### Fixed Positioning Strategy

**Decision:** Use CSS `position: fixed` for the `.header` element

**Rationale:**
- Standard CSS solution with excellent browser support
- No JavaScript overhead or complexity
- Prevents element from scrolling with document flow
- Works well with existing flexbox layout on `body`

**Alternatives considered:**
1. `position: sticky` - Could work but has quirks with stacking contexts and parent overflow settings
2. JavaScript scroll listeners - Unnecessary complexity and performance overhead
3. Flexbox with `overflow: hidden` - Would require restructuring the entire layout

### Content Offset Strategy

**Decision:** Add `padding-top` to `.main-content` equal to header height

**Rationale:**
- Simple CSS-only solution
- Maintains existing flexbox structure
- Header height is relatively stable (~66px with 15px padding + content)

**Calculation:**
- Current header padding: `15px` (top + bottom = 30px total vertical)
- Header content height: ~36px (button height)
- Estimated total: ~66px (will use `80px` for safe margin)

### Z-index Layering

**Decision:** Maintain `z-index: 100` on header

**Rationale:**
- Current value already places header above main content
- Side menu uses `z-index: 300` and overlay uses `z-index: 200`
- Layering hierarchy is already correct

## CSS Changes

```css
/* Before */
.header {
    padding: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    z-index: 100;
}

/* After */
.header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    padding: 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    z-index: 100;
}

/* Main content adjustment */
.main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 20px;
    padding-top: 80px;  /* NEW: Account for fixed header */
    justify-content: center;
    min-height: 0;
}
```

## Media Query Considerations

The existing `@media (orientation: landscape)` query reduces header padding to `10px 20px`. The fixed positioning will work correctly in both orientations since the `padding-top` on `.main-content` provides sufficient space.

## Risks / Trade-offs

### Risk 1: Content overlap on small screens

**Risk:** Fixed header might cover content on very small screens or with large dynamic text sizing

**Mitigation:** Using `80px` padding-top provides buffer. Users can also scroll content area.

### Risk 2: Virtual keyboard interaction

**Risk:** On some mobile browsers, virtual keyboard might push fixed header off-screen

**Mitigation:** Most modern mobile browsers handle this correctly. Can be tested during validation.

## Migration Plan

**Steps:**
1. Edit `site/style.css`
2. Add fixed positioning properties to `.header` rule
3. Add `padding-top: 80px` to `.main-content` rule
4. Test in browser/mobile emulation

**Rollback:**
Simply remove the added properties from both CSS rules to revert to original behavior.

## Open Questions

None. The implementation is straightforward CSS changes with well-understood behavior.
