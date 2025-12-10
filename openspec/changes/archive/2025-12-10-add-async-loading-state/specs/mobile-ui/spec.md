## ADDED Requirements

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

## MODIFIED Requirements

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