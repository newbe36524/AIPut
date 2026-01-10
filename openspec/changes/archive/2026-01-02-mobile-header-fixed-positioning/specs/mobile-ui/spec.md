# Mobile UI Specification

## ADDED Requirements

### Requirement: Fixed Header Positioning

The mobile web interface SHALL maintain the header bar in a fixed position at the top of the viewport, ensuring all header controls remain accessible to users at all times.

#### Scenario: Header remains visible during content scroll

- **WHEN** a user scrolls through the main content area
- **THEN** the header bar SHALL remain fixed at the top of the viewport
- **AND** all header buttons (menu, prompt selector, clear, send) SHALL remain visible and interactive

#### Scenario: Header persists with virtual keyboard

- **WHEN** the virtual keyboard is displayed or hidden
- **THEN** the header bar SHALL remain fixed at the top of the viewport
- **AND** no content SHALL be hidden behind the header

#### Scenario: Header adapts to orientation changes

- **WHEN** the device orientation changes between portrait and landscape
- **THEN** the header bar SHALL remain fixed at the top of the viewport
- **AND** the header SHALL span the full width of the screen

#### Scenario: Content is not obscured by fixed header

- **WHEN** the page loads initially
- **THEN** the main content SHALL have sufficient top padding to prevent content from being hidden behind the fixed header
- **AND** users SHALL be able to scroll through all content without it disappearing under the header
