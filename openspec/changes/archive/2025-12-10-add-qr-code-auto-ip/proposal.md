# Change: Add QR Code Display with Independent IP Selection

## Why
The QR code display functionality that users relied on for easy mobile connection is missing from the current implementation. Users need a convenient way to connect their mobile devices without manually typing IP addresses. The current design where binding and QR code share the same IP selection is confusing - binding should default to all interfaces (0.0.0.0) while QR code needs a specific IP for scanning.

## What Changes
- Add a separate IP selection dropdown below the binding IP dropdown for QR code display
- The binding dropdown remains as-is with 0.0.0.0 as default option
- The QR code dropdown excludes 0.0.0.0 and defaults to the first valid IP address
- Add QR code generation and display functionality that updates based on QR code dropdown selection
- Add a "显示二维码" button next to the QR code dropdown
- QR code displays in a popup window containing the selected IP + port URL

## Impact
- Affected specs: mobile-ui
- Affected code: src/remote_server.py (main GUI application)
- UI Changes: Add new dropdown and button for QR code IP selection
- New dependencies: qrcode (already installed), PIL/Pillow (already installed)
- User experience: Clear separation between server binding and mobile connection URL