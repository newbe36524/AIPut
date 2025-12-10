# Change: Add Async Processing with Loading States for Text Submission

## Why
The current text submission feature lacks proper user feedback during AI processing, leading to uncertainty about operation status and potential duplicate submissions. Users need clear visual indicators when AI processing is taking place, especially for longer operations.

## What Changes
- Add loading state UI components that display during text submission and AI processing
- Implement backend API pattern analysis to determine synchronous vs asynchronous processing
- Enhance frontend state management to handle loading states and prevent duplicate submissions
- Add visual loading indicators in the text input area
- Disable submit button and input during processing to prevent duplicate submissions

## Impact
- Affected specs: mobile-ui
- Affected code:
  - Frontend: `site/app.js` (submission logic), `site/index.html` (UI elements), `site/style.css` (loading styles)
  - Backend: `src/remote_server.py` (API endpoint analysis)
  - Configuration: `site/config/prompts.json` (prompt metadata)