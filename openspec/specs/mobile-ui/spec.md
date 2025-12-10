# mobile-ui Specification

## Purpose
TBD - created by archiving change redesign-mobile-ui. Update Purpose after archive.
## Requirements
### Requirement: Input-Focused Mobile Interface
The mobile web interface SHALL prioritize text input as the primary visual and interactive element, occupying the majority of the screen space with action buttons in the header.

#### Scenario: Input takes focus on page load
- **WHEN** user opens the mobile web interface
- **THEN** the text input field SHALL immediately gain focus
- **AND** the virtual keyboard SHALL appear

#### Scenario: Input occupies most of the screen
- **WHEN** viewing the interface in portrait mode
- **THEN** the input field SHALL occupy at least 80% of viewport height
- **AND** SHALL use appropriate font size for readability
- **AND** SHALL have unobstructed view without button-group below

### Requirement: Collapsible Menu System
All secondary functions SHALL be accessible through a hamburger menu located in the top-left corner of the screen, while primary actions (Send and Clear) SHALL be accessible through buttons in the top-right corner.

#### Scenario: Menu access
- **WHEN** user taps the hamburger menu icon
- **THEN** a sliding panel SHALL appear from the left
- **AND** SHALL overlay the main content with a semi-transparent backdrop

#### Scenario: Header buttons visibility
- **WHEN** viewing the interface
- **THEN** Send and Clear buttons SHALL be visible in the header on the right side
- **AND** SHALL be easily accessible without scrolling

#### Scenario: Menu contains history only
- **WHEN** the menu is open
- **THEN** it SHALL display the history list
- **AND** SHALL show the clear history option
- **AND** SHALL NOT duplicate Send and Clear buttons (they're in header)

### Requirement: Gesture-Based Interactions
The interface SHALL support common mobile gestures for quick actions without requiring button interaction.

#### Scenario: Swipe to send
- **WHEN** user swipes up on the input field
- **THEN** the text content SHALL be sent to the desktop
- **AND** input field SHALL be cleared after successful send

#### Scenario: Swipe to clear
- **WHEN** user swipes down on the input field
- **THEN** the input field SHALL be cleared immediately
- **AND** focus SHALL remain on the input field

#### Scenario: Tap to send/clear
- **WHEN** user taps the Send button in header
- **THEN** the text content SHALL be sent to the desktop
- **WHEN** user taps the Clear button in header
- **THEN** the input field SHALL be cleared immediately

### Requirement: Persistent Input Focus
The input field SHALL maintain focus unless explicitly interacting with menu elements.

#### Scenario: Focus after menu interaction
- **WHEN** user closes the menu or completes an action
- **THEN** focus SHALL automatically return to the input field
- **AND** virtual keyboard SHALL remain visible

#### Scenario: Focus restoration
- **WHEN** user taps outside the input area but not on menu
- **THEN** focus SHALL immediately return to the input field

### Requirement: Header Action Buttons
Send and Clear action buttons SHALL be prominently displayed in the header area for immediate access, with state-aware behavior during processing.

#### Scenario: Header button layout
- **WHEN** viewing the interface
- **THEN** Send button SHALL be positioned on the right side of the header
- **AND** Clear button SHALL be positioned to the left of Send button
- **AND** Both buttons SHALL maintain their current styling and colors

#### Scenario: Header button responsiveness
- **WHEN** viewing on different screen sizes
- **THEN** header buttons SHALL scale appropriately
- **AND** SHALL remain touch-friendly with minimum 44px touch target
- **AND** SHALL maintain proper spacing from other header elements

#### Scenario: Header button state during processing
- **WHEN** text submission is in progress
- **THEN** the Send button SHALL be visually disabled
- **AND** SHALL not respond to taps
- **AND** the Clear button SHALL remain operational
- **AND** button states SHALL return to normal after processing completes

### Requirement: Independent IP Selection for QR Code
The desktop application SHALL provide separate IP selection controls for server binding and QR code display.

#### Scenario: Dual IP dropdowns
- **WHEN** the application UI is displayed
- **THEN** there SHALL be two IP selection dropdowns
- **AND** the first dropdown SHALL be for server binding (includes 0.0.0.0)
- **AND** the second dropdown SHALL be for QR code display (excludes 0.0.0.0)
- **AND** the second dropdown SHALL default to the first valid IP address

#### Scenario: QR Code IP exclusion
- **WHEN** populating the QR code IP dropdown
- **THEN** the "0.0.0.0 (所有网卡)" option SHALL be excluded
- **AND** only valid, scannable IP addresses SHALL be shown
- **AND** the first non-0.0.0.0 IP SHALL be selected by default

### Requirement: QR Code Display Control
The application SHALL provide a button to display the QR code based on the selected QR IP address.

#### Scenario: Manual QR code display
- **WHEN** the user clicks the "显示二维码" button
- **THEN** a QR code popup window SHALL appear
- **AND** the QR code SHALL contain the URL from the selected QR IP + port
- **AND** the QR code SHALL be generated dynamically on button click

#### Scenario: QR code URL format
- **WHEN** generating the QR code
- **THEN** the URL SHALL be in format `http://[QR_IP]:[PORT]`
- **AND** the IP SHALL be from the QR code dropdown selection
- **AND** the port SHALL match the service port

### Requirement: Independent Operation of Controls
The server binding and QR code display SHALL operate independently.

#### Scenario: Service control independence
- **WHEN** the service is started or stopped
- **THEN** the QR code dropdown SHALL remain enabled
- **AND** the QR code display button SHALL remain functional
- **AND** users SHALL be able to change QR IP selection while service is running

#### Scenario: QR code display independence
- **WHEN** the QR code window is displayed
- **THEN** the user SHALL be able to stop/start the service
- **AND** the user SHALL be able to change the server binding IP
- **AND** the QR code window SHALL remain open until explicitly closed

### Requirement: QR Code Window Management
The QR code display SHALL provide a user-friendly window that can be closed independently.

#### Scenario: QR code window behavior
- **WHEN** the QR code window is displayed
- **THEN** it SHALL be a non-modal top-level window
- **AND** SHALL include the URL text below the QR code image
- **AND** SHALL have a close button
- **AND** closing it SHALL NOT affect the service status

#### Scenario: QR code size and clarity
- **WHEN** displaying the QR code
- **THEN** it SHALL be sized appropriately for mobile scanning (minimum 200x200 pixels)
- **AND** SHALL have clear contrast
- **AND** SHALL include error correction for reliable scanning

### Requirement: Loading State During Text Submission
The mobile interface SHALL display a prominent loading indicator over the text input area during submission and AI processing.

#### Scenario: Loading overlay appears on submission
- **WHEN** user submits text via Send button, swipe gesture, or keyboard shortcut
- **THEN** a semi-transparent loading overlay SHALL appear over the textarea
- **AND** the overlay SHALL display a loading animation and descriptive text
- **AND** the textarea and submit button SHALL be disabled during processing

#### Scenario: Loading state messages
- **WHEN** text is being sent to the server
- **THEN** the loading message SHALL read "发送中..."
- **WHEN** AI processing is active
- **THEN** the loading message SHALL read "AI处理中..."
- **WHEN** brave mode AI processing is active
- **THEN** the loading message SHALL read "AI处理中... (勇敢模式)"

#### Scenario: Loading state completion
- **WHEN** processing completes successfully
- **THEN** the loading overlay SHALL disappear
- **AND** the textarea SHALL be cleared and re-enabled
- **AND** focus SHALL return to the textarea
- **WHEN** processing encounters an error
- **THEN** the loading overlay SHALL disappear
- **AND** the textarea SHALL be re-enabled with original text preserved
- **AND** focus SHALL return to the textarea

### Requirement: Duplicate Submission Prevention
The mobile interface SHALL prevent users from submitting text multiple times during processing.

#### Scenario: Input disabling during processing
- **WHEN** a submission is in progress
- **THEN** the textarea SHALL be read-only
- **AND** all keyboard input SHALL be ignored
- **AND** swipe gestures on the textarea SHALL be disabled
- **WHEN** processing completes or fails
- **THEN** the textarea SHALL become fully interactive again

#### Scenario: Button state management
- **WHEN** a submission is in progress
- **THEN** the Send button SHALL be disabled
- **AND** the Send button SHALL show reduced opacity
- **AND** the Clear button SHALL remain enabled to allow cancellation
- **WHEN** processing completes
- **THEN** the Send button SHALL be re-enabled

### Requirement: Visual Loading Indicators
The loading overlay SHALL provide clear visual feedback about the current operation state.

#### Scenario: Loading animation
- **WHEN** the loading overlay is displayed
- **THEN** a spinning loader animation SHALL be visible
- **AND** the animation SHALL be smoothly animated
- **AND** the animation SHALL be centered in the overlay

#### Scenario: Progress indication
- **WHEN** multiple operations are occurring (send + AI processing)
- **THEN** the message SHALL update to reflect the current operation
- **AND** transitions between messages SHALL be smooth
- **AND** users SHALL be able to distinguish between sending and processing phases

