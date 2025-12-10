## ADDED Requirements

### Requirement: Automatic Service Startup
The system SHALL provide automatic service startup capability when the application launches.

#### Scenario: Auto-start enabled on launch
- **WHEN** the application starts with auto-start enabled (default)
- **THEN** the service automatically starts without user interaction
- **AND** the UI displays the service as running immediately

#### Scenario: Auto-start with invalid configuration
- **WHEN** auto-start is enabled but port/IP configuration is invalid
- **THEN** the application displays an error message
- **AND** the service remains stopped
- **AND** the user can manually fix configuration and start

### Requirement: Manual Service Control
The system SHALL preserve manual service start/stop functionality even with auto-start enabled.

#### Scenario: Manual stop after auto-start
- **WHEN** user clicks stop button after auto-start
- **THEN** the service stops immediately
- **AND** the button changes to start state

#### Scenario: Manual restart
- **WHEN** user clicks start button when service is stopped
- **THEN** the service restarts with current configuration
- **AND** error handling works as before

### Requirement: Auto-start Configuration
The system SHALL provide a user preference to enable/disable auto-start behavior.

#### Scenario: Disable auto-start
- **WHEN** user disables auto-start preference
- **THEN** application launches with service stopped
- **AND** user must manually start service

#### Scenario: Reset to default
- **WHEN** preferences are reset to defaults
- **THEN** auto-start is enabled by default