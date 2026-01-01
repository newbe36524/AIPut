## 1. Update Platform Adapter Base Interface
- [x] 1.1 Add `keep_alive()` abstract method to `KeyboardAdapter` in `base.py`
  - Use generic method name instead of implementation-specific name
  - Each platform adapter decides how to implement keep-alive
- [x] 1.2 Add documentation for the new method

## 2. Implement keep_alive() for Linux (X11/Wayland)
- [x] 2.1 Implement `keep_alive()` in `WaylandKeyboardAdapter`
  - [x] 2.1.1 Use Scroll Lock key (press twice) for Fedora/KDE Wayland
  - [x] 2.1.2 Add xdotool support via Xwayland
  - [x] 2.1.3 Add wtype support for native Wayland
  - [x] 2.1.4 Add ydotool support as fallback
- [x] 2.2 Implement `keep_alive()` in `X11KeyboardAdapter`
  - [x] 2.2.1 Use Scroll Lock key (press twice)
  - [x] 2.2.2 Add xdotool support
  - [x] 2.2.3 Add xte support
  - [x] 2.2.4 Add xvkbd support

## 3. Implement keep_alive() for Windows
- [x] 3.1 Implement `keep_alive()` in `WindowsKeyboardAdapter`
  - [x] 3.1.1 Add stub implementation returning False (platform may not need this)
  - [x] 3.1.2 Optionally implement Scroll Lock using pyautogui/win32api

## 4. Implement keep_alive() for macOS
- [x] 4.1 Implement `keep_alive()` in `MacOSKeyboardAdapter`
  - [x] 4.1.1 Add stub implementation returning False (platform may not need this)
  - [x] 4.1.2 Optionally implement Scroll Lock using pyautogui/osascript

## 5. Implement Keep-Alive Thread in Main Server
- [x] 5.1 Create `KeepAliveThread` class in `remote_server.py`
  - [x] 5.1.1 Implement thread-safe start/stop mechanism
  - [x] 5.1.2 Add configurable interval (default: 5 minutes)
  - [x] 5.1.3 Call `keyboard_adapter.keep_alive()` periodically
- [x] 5.2 Integrate keep-alive thread with main server lifecycle
  - [x] 5.2.1 Start keep-alive thread on server startup
  - [x] 5.2.2 Stop keep-alive thread gracefully on shutdown
  - [x] 5.2.3 Add initial keep-alive trigger on startup

## 6. Add Configuration Support
- [x] 6.1 Add environment variable support for keep-alive interval
  - [x] 6.1.1 Define `AIPUT_KEEP_ALIVE_INTERVAL` environment variable
  - [x] 6.1.2 Add validation for interval values (minimum: 1 minute)
- [ ] 6.2 Add configuration file support (optional)
  - [ ] 6.2.1 Add keep-alive settings to config file schema
  - [ ] 6.2.2 Implement config loading logic

## 7. Testing and Validation
- [ ] 7.1 Test keep-alive on Linux (X11)
  - [ ] 7.1.1 Verify Scroll Lock simulation with xdotool
  - [ ] 7.1.2 Verify Scroll Lock simulation with xte (if available)
- [ ] 7.2 Test keep-alive on Linux (Wayland)
  - [ ] 7.2.1 Verify Scroll Lock simulation on KDE Wayland (xdotool via Xwayland)
  - [ ] 7.2.2 Verify Scroll Lock simulation with wtype
  - [ ] 7.2.3 Verify Scroll Lock simulation with ydotool
- [ ] 7.3 Test keep-alive on Windows (if implemented)
- [ ] 7.4 Test keep-alive on macOS (if implemented)
- [ ] 7.5 Test keep-alive thread functionality
  - [ ] 7.5.1 Verify initial trigger on startup
  - [ ] 7.5.2 Verify periodic triggers every 5 minutes
  - [ ] 7.5.3 Verify graceful shutdown
- [ ] 7.6 Test custom interval configuration
- [ ] 7.7 Verify system idle prevention on Fedora/KDE
  - [ ] 7.7.1 Run for extended period (> 15 minutes)
  - [ ] 7.7.2 Confirm no system keyboard input prompts appear

## 8. Documentation
- [ ] 8.1 Update README with keep-alive feature description
- [ ] 8.2 Document environment variable configuration
- [ ] 8.3 Add troubleshooting section for keep-alive issues
- [ ] 8.4 Document that Linux uses Scroll Lock, other platforms may have different implementations
