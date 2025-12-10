## ADDED Requirements

### Requirement: Input-Focused Mobile Interface
The mobile web interface SHALL prioritize text input as the primary visual and interactive element, occupying the majority of the screen space.

#### Scenario: Input takes focus on page load
- **WHEN** user opens the mobile web interface
- **THEN** the text input field SHALL immediately gain focus
- **AND** the virtual keyboard SHALL appear

#### Scenario: Input occupies most of the screen
- **WHEN** viewing the interface in portrait mode
- **THEN** the input field SHALL occupy at least 80% of viewport height
- **AND** SHALL use appropriate font size for readability

### Requirement: Collapsible Menu System
All secondary functions SHALL be accessible through a hamburger menu located in the top-left corner of the screen.

#### Scenario: Menu access
- **WHEN** user taps the hamburger menu icon
- **THEN** a sliding panel SHALL appear from the left
- **AND** SHALL overlay the main content with a semi-transparent backdrop

#### Scenario: Menu contains all controls
- **WHEN** the menu is open
- **THEN** it SHALL display Send and Clear buttons
- **AND** SHALL show the history list
- **AND** SHALL maintain all existing functionality

### Requirement: Gesture-Based Interactions
The interface SHALL support common mobile gestures for quick actions without requiring menu interaction.

#### Scenario: Swipe to send
- **WHEN** user swipes up on the input field
- **THEN** the text content SHALL be sent to the desktop
- **AND** input field SHALL be cleared after successful send

#### Scenario: Swipe to clear
- **WHEN** user swipes down on the input field
- **THEN** the input field SHALL be cleared immediately
- **AND** focus SHALL remain on the input field

### Requirement: Persistent Input Focus
The input field SHALL maintain focus unless explicitly interacting with menu elements.

#### Scenario: Focus after menu interaction
- **WHEN** user closes the menu or completes an action
- **THEN** focus SHALL automatically return to the input field
- **AND** virtual keyboard SHALL remain visible

#### Scenario: Focus restoration
- **WHEN** user taps outside the input area but not on menu
- **THEN** focus SHALL immediately return to the input field