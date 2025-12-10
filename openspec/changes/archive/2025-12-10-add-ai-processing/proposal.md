# Add AI Language Processing Proposal

## Summary

This proposal introduces AI language processing capabilities to the AIPut wireless voice input tool. Users will be able to select processing modes (e.g., "Agent Task") from a dropdown in the header, which will apply predefined prompts to their input text using ZAI's API before sending it to the desktop.

## Problem Statement

Currently, AIPut only supports direct text input from mobile to desktop. Users need AI-powered text processing capabilities (such as organizing thoughts into structured requirements) while maintaining the simplicity of the existing workflow.

## Proposed Solution

### Frontend Changes
1. Add a mode selector dropdown in the header next to Send/Clear buttons
2. Create a JSON configuration file for processing prompts
3. Modify the send flow to include selected mode and prompt

### Backend Changes
1. Create an abstract AI processor interface
2. Implement ZAI processor as the first provider
3. Extend the existing `/type` endpoint to support AI processing

### Architecture
- **Abstract Processor Interface**: Allows future extension to other AI providers
- **JSON-based Prompt Configuration**: Easy to add new processing modes
- **Mode-aware Processing**: Backend receives both text and processing instructions

## Impact Analysis

### Benefits
- Enhanced productivity with AI-assisted text processing
- Extensible architecture for multiple AI providers
- Simple user experience integrated into existing flow
- Flexible prompt management through JSON configuration

### Costs
- Additional dependency on ZAI Python SDK
- Requires API key configuration
- Increased response time due to AI processing
- Potential costs from ZAI API usage

### Risks
- API service availability dependency
- Processing latency affecting user experience
- Potential sensitive data exposure to third-party API

## Alternatives Considered

1. **Client-side processing**: Would require exposing API keys to the client - rejected for security reasons
2. **Separate processing endpoint**: Adds complexity to the flow - rejected in favor of integrated approach
3. **Hard-coded prompts**: Less flexible for future enhancements - rejected in favor of JSON configuration

## Relationship to Existing Specs

This change extends the `mobile-ui` spec by:
- Adding a mode selector to the header
- Modifying the send flow to support AI processing
- Maintaining the existing input-focused design

## Future Enhancements

- Support for additional AI providers (OpenAI, Claude, local models)
- User-defined custom prompts
- Processing history and usage tracking
- Batch processing of multiple inputs

## Success Criteria

1. Users can select "Agent Task" mode from dropdown
2. Selected mode applies appropriate prompt transformation
3. Processed text replaces input and can be sent normally
4. Processing completes within acceptable time (<5 seconds)
5. System gracefully handles API failures