## ADDED Requirements

### Requirement: Brave Mode Toggle
The system SHALL provide a brave mode toggle that allows users to enable automatic Ctrl+Enter key execution after text pasting.

#### Scenario: Enable brave mode
- **WHEN** user taps the brave mode toggle in the mobile interface
- **THEN** the toggle state persists across browser sessions
- **AND** subsequent text inputs will automatically execute Ctrl+Enter after pasting

#### Scenario: Disable brave mode
- **WHEN** user disables the brave mode toggle
- **THEN** the system reverts to standard paste-only behavior
- **AND** the disabled state persists across sessions

### Requirement: Automatic Ctrl+Enter Execution
The system SHALL automatically execute a Ctrl+Enter key command after successfully pasting text when brave mode is enabled.

#### Scenario: Brave mode text submission
- **WHEN** brave mode is enabled and user sends text
- **THEN** the system pastes the text to the active application
- **AND** after a configurable delay, automatically sends Ctrl+Enter key
- **AND** returns success status for both operations

#### Scenario: Configurable delay
- **WHEN** brave mode is active
- **THEN** the delay between paste and Ctrl+Enter is configurable
- **AND** defaults to 100ms for optimal compatibility

## MODIFIED Requirements

### Requirement: Text Input API
The system SHALL accept an optional auto_submit parameter in the text input endpoint to control automatic Ctrl+Enter execution.

#### Scenario: Text input with brave mode
- **WHEN** client sends POST /type with auto_submit: true
- **THEN** the system executes both paste and Ctrl+Enter operations
- **AND** returns response indicating both actions were attempted

#### Scenario: Text input without brave mode
- **WHEN** client sends POST /type without auto_submit or with auto_submit: false
- **THEN** the system only executes paste operation
- **AND** maintains current behavior

### Requirement: Keyboard Adapter Interface
The keyboard adapter SHALL provide a method for executing Ctrl+Enter key commands across all supported platforms.

#### Scenario: Platform-specific Ctrl+Enter simulation
- **WHEN** send_ctrl_enter() is called on any platform adapter
- **THEN** the adapter uses platform-appropriate method to send Ctrl+Enter
- **AND** returns boolean success status
- **AND** handles platform-specific key codes and mechanisms