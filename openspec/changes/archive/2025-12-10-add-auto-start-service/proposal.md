# Change: Add Automatic Service Startup

## Why
Users currently need to manually click the "启动服务" button to start the service after launching the application. This is an unnecessary step that creates friction in the user experience.

## What Changes
- Add automatic service startup capability that starts the service when the application launches
- Keep the start/stop button for manual control when users need to restart or temporarily stop the service
- Add a user preference setting to enable/disable auto-start behavior (default: enabled)
- Preserve current error handling and validation behavior

## Impact
- Affected specs:
  - ADD: `service-management` - New capability for automatic startup behavior
- Affected code:
  - `src/remote_server.py:287-324` - Modify toggle_server method and ServerApp initialization
  - `src/remote_server.py:258-259` - Update initialization to support auto-start