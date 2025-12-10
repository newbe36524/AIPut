## ADDED Requirements

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