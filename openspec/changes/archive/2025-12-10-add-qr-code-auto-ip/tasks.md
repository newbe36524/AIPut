## 1. Implementation
- [x] 1.1 Create QR code generation function that accepts IP and port
- [x] 1.2 Create QR code display window (Toplevel) with image display
- [x] 1.3 Add second IP dropdown for QR code selection (exclude 0.0.0.0)
- [x] 1.4 Add "显示二维码" button next to QR code dropdown
- [x] 1.5 Set default value for QR code dropdown to first valid IP
- [x] 1.6 Integrate QR code display with button click event
- [x] 1.7 Add close button to QR code window
- [x] 1.8 Update UI layout to accommodate new dropdown and button

## 2. Validation
- [ ] 2.1 Verify QR code displays correct URL format from selected IP
- [ ] 2.2 Test QR code scannability on mobile devices
- [ ] 2.3 Confirm service binding dropdown works independently
- [ ] 2.4 Test with different IP configurations (multiple NICs)
- [ ] 2.5 Verify QR code updates when QR IP dropdown changes
- [ ] 2.6 Test that service can be stopped and IP binding changed while QR code is visible