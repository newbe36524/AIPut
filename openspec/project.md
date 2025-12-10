# Project Context

## Purpose

AIPut is a wireless voice input tool that enables users to input text into their computers using their smartphone's voice input capabilities. It bridges the gap between superior mobile voice recognition and desktop applications by creating a local web interface that receives voice input from mobile devices and transfers it to the desktop via clipboard and keyboard automation.

Key goals:
- Leverage high-quality mobile voice recognition (e.g., mobile phone's built-in voice input)
- Provide seamless wireless text input to desktop applications
- Support cross-platform desktop environments (X11/Wayland)
- Maintain simplicity and reliability with minimal dependencies

## Tech Stack

- **Python 3.8+** - Primary programming language
- **Flask** - Web framework for HTTP server
- **Tkinter** - GUI framework for desktop application
- **HTML/CSS/JavaScript** - Mobile web interface
- **pyautogui/pyperclip** - Clipboard and keyboard automation
- **qrcode/pillow** - QR code generation
- **pystray** - System tray integration

## Project Structure

```
qaa-airtype/
├── src/                          # Source code directory
│   ├── remote_server.py         # Main application entry point
│   ├── platform_detection/      # Platform detection module
│   │   ├── detector.py          # Detects OS and display environment
│   │   └── capabilities.py      # Defines platform capabilities
│   ├── platform_adapters/       # Platform-specific input adapters
│   │   ├── base.py              # Base adapter interface
│   │   ├── factory.py           # Adapter factory
│   │   ├── linux/               # Linux adapters
│   │   │   ├── adapter.py       # Linux main adapter
│   │   │   ├── x11.py           # X11 specific implementation
│   │   │   └── wayland.py       # Wayland specific implementation
│   │   ├── windows/             # Windows adapters (placeholder)
│   │   └── macos/               # macOS adapters (placeholder)
│   └── generate_icon.py         # Icon generation utility
├── site/                        # Mobile web interface
│   ├── index.html               # Main HTML page
│   ├── app.js                   # Client-side JavaScript
│   └── style.css                # Mobile-optimized CSS
├── openspec/                    # OpenSpec documentation
├── scripts/                     # Installation and setup scripts
├── aiput-env/                   # Python virtual environment
└── pyproject.toml               # Python project configuration
```

## Current Features

### Core Functionality
- **Remote Text Input**: Send text from mobile device to desktop
- **Wireless Connection**: Local WiFi/LAN communication without internet dependency
- **Cross-Platform Support**: Currently supports Linux with X11/Wayland
- **Mobile Web Interface**: Responsive design optimized for mobile browsers
- **Gesture Support**: Swipe up to send, swipe down to clear
- **Input History**: Maintains last 10 inputs in browser localStorage
- **System Tray Integration**: Minimize to system tray on desktop

### Platform Abstraction
- **Modular Architecture**: Platform-specific adapters for different OS environments
- **Automatic Detection**: Detects display server (X11/Wayland) and available tools
- **Fallback Chain**: Multiple automation tools with graceful degradation
- **Tool Detection**: Checks for availability of system tools (xdotool, wtype, ydotool, etc.)

### User Experience
- **QR Code Setup**: Display QR code for easy mobile connection
- **Auto IP Detection**: Automatically detects and displays local IP address
- **Visual Feedback**: Status indicators for sent/failed operations
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for new line
- **Focus Management**: Automatic focus management for better typing experience

## Project Conventions

### Code Style

- **PEP 8** compliant Python code
- **CamelCase** for class names (e.g., `RemoteServerGUI`)
- **snake_case** for functions and variables
- **Constants in UPPER_CASE** for configuration values
- **Minimal dependencies** - prefer built-in Python modules
- **Modular architecture** with platform-specific adapters

### Architecture Patterns

- **Modular adapter architecture** - Platform adapters for different OS environments
- **Thread-based concurrency** - Separate threads for Flask server and Tkinter GUI
- **Platform abstraction** - Unified interface with platform-specific implementations
- **Fallback chain pattern** - Multiple automation tools with graceful degradation
- **Environment detection** - Auto-detect X11/Wayland display server and available tools
- **Resource cleanup** - Proper cleanup on application exit
- **Factory pattern** - For creating appropriate platform adapters

### Testing Strategy

- **Manual testing** - Test across different platforms and applications
- **Integration testing** - Verify mobile-to-desktop workflow
- **Error scenario testing** - Test failure modes and fallbacks
- **No automated test suite** - Pragmatic approach for single-file utility

### Git Workflow

- **Feature branches** - Use descriptive feature branch names (e.g., `feature/voice-input-enhancement`)
- **Squash commits** - Clean commit history with meaningful messages
- **Chinese commit messages** - Primary language for commit descriptions
- **Version tags** - Tag releases for easy reference

## Domain Context

AIPut operates in the accessibility and productivity domain, specifically:

- **Voice input accessibility** - Helps users who prefer voice typing
- **Cross-platform compatibility** - Works across Linux desktop environments
- **Local network communication** - No internet dependency, operates over WiFi/LAN
- **Input method bridging** - Bridges mobile IME capabilities to desktop

Key concepts:
- **X11/Wayland** - Linux display server protocols
- **Clipboard automation** - Programmatic clipboard manipulation
- **Keyboard simulation** - Virtual keyboard input injection
- **HTTP server patterns** - Local REST API design
- **Platform detection** - Runtime detection of OS and display environment
- **Tool availability checking** - Verifying presence of system automation tools

## Important Constraints

- **Local network only** - Server binds to localhost or local network, no internet exposure
- **No persistent storage** - History limited to session memory (last 10 inputs)
- **Single user application** - Designed for individual use, not multi-user
- **Platform-specific automation** - Relies on system tools (xdotool, wtype, ydotool)
- **Python version compatibility** - Must support Python 3.8+ for wider compatibility
- **No authentication** - Trusted local network environment assumed

## External Dependencies

### System Dependencies (Linux)
- **xdotool** - X11 keyboard automation tool
- **wtype** - Wayland keyboard automation tool
- **ydotool** - Alternative keyboard automation tool
- **xclip/xsel** - X11 clipboard utilities
- **wl-copy** - Wayland clipboard utility

### Python Libraries
- **flask>=3.0.0** - HTTP web framework
- **qrcode[pil]>=7.4.2** - QR code generation
- **pystray>=0.19.0** - System tray integration
- **Pillow>=10.0.0** - Image processing for QR codes
- **pyperclip>=1.8.2** - Cross-platform clipboard access
- **pyautogui>=0.9.54** - Cross-platform GUI automation

### Development Dependencies (Optional)
- **pyinstaller>=6.0.0** - For creating standalone executables

### Platform APIs
- **Tkinter** - Standard Python GUI toolkit
- **threading** - Python threading module
- **subprocess** - System command execution
- **socket** - Network communication

## Known Limitations

### Current Limitations
- **Linux Only** - Currently only supports Linux with X11/Wayland
- **No AI Integration** - Despite the name "AIPut", currently no AI features are implemented
- **No Voice Recognition** - Relies on mobile device's voice input capabilities
- **Single Language Interface** - Mobile interface only in Chinese

### Future Planned Features
- **Windows/macOS Support** - Adapters are in place but need implementation
- **AI Text Enhancement** - Chat and Agent modes for text processing
- **Multi-language Support** - Internationalization for mobile interface
- **Persistent History** - Option to save input history across sessions
- **Custom Shortcuts** - Configurable keyboard shortcuts
- **Direct Paste Mode** - Option to paste directly without typing simulation
