# AI Processing Architecture Design

## Overview

This design outlines the architecture for adding AI language processing capabilities to AIPut while maintaining extensibility for future AI providers.

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │     │    Backend      │     │   AI Provider   │
│                 │     │                 │     │                 │
│ ┌─────────────┐ │     │ ┌─────────────┐ │     │ ┌─────────────┐ │
│ │ Mode Picker │ │     │ │     /type    │ │     │ │   ZAI API    │ │
│ │ (Dropdown)  │◄┼─────┼│   Endpoint  │◄┼─────┼│             │ │
│ └─────────────┘ │     │ └─────────────┘ │     │ └─────────────┘ │
│                 │     │        │        │     │                 │
│ ┌─────────────┐ │     │ ┌─────────────┐ │     │ ┌─────────────┐ │
│ │ Prompts.json│ │     │ │AI Processor │ │     │ │ Future AI   │ │
│ │ (Config)    │◄┼─────┼│  Interface  ││     │ │ Providers  │ │
│ └─────────────┘ │     │ └─────────────┘ │     │ └─────────────┘ │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Component Design

### 1. Frontend Components

#### Mode Selector
- Location: Header, between title and action buttons
- Type: Dropdown/select element
- Default: "Normal" (no processing)
- Options: Loaded from `prompts.json`

#### Prompts Configuration
- File: `site/config/prompts.json`
- Structure:
```json
{
  "modes": [
    {
      "id": "normal",
      "name": "普通模式",
      "description": "直接输入，不进行处理",
      "prompt": ""
    },
    {
      "id": "agent-task",
      "name": "Agent Task",
      "description": "将文本整理为条理清晰的任务要求",
      "prompt": "请将以下文本内容整理成条理清晰、结构化的任务要求列表..."
    }
  ]
}
```

### 2. Backend Components

#### Abstract AI Processor Interface
```python
from abc import ABC, abstractmethod
from typing import Optional

class AIProcessor(ABC):
    @abstractmethod
    async def process_text(self, text: str, prompt: str) -> Optional[str]:
        """Process text using AI with given prompt"""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if processor is properly configured"""
        pass
```

#### ZAI Processor Implementation
```python
class ZAIProcessor(AIProcessor):
    def __init__(self, api_key: str, model: str = "glm-4.6"):
        self.client = ZAI(api_key=api_key)
        self.model = model

    async def process_text(self, text: str, prompt: str) -> Optional[str]:
        # Implementation using ZAI API
        pass
```

#### Processing Service
```python
class ProcessingService:
    def __init__(self):
        self.processors = {}
        self.register_processor("zai", ZAIProcessor)

    def register_processor(self, name: str, processor_class: type):
        self.processors[name] = processor_class

    async def process(self, text: str, prompt: str, provider: str = "zai", mode: str = None):
        # Log the mode for analytics/debugging purposes
        if mode:
            print(f"[AI Processing] Using mode: {mode}")

        processor = self.processors.get(provider)
        if not processor:
            raise ValueError(f"Unknown provider: {provider}")
        return await processor.process_text(text, prompt)
```

## API Design

### Modified Endpoint: `/type`

The existing `/type` endpoint will be enhanced to support AI processing while maintaining backward compatibility.

**Standard Request (without AI processing):**
```json
{
  "text": "要输入的文本"
}
```

**AI Processing Request:**
```json
{
  "text": "用户输入的文本",
  "prompt": "请将以下文本内容整理成条理清晰、结构化的任务要求列表...",
  "mode": "agent-task",
  "provider": "zai"
}
```

**Success Response:**
```json
{
  "success": true
}
```

**Error Response (when AI processing fails):**
```json
{
  "success": false,
  "error": "API key未配置或无效"
}
```

## Data Flow

### Processing Flow
1. User selects mode from dropdown
2. Frontend loads the corresponding prompt from prompts.json
3. User inputs text
4. User clicks "Send" button
   - If mode is "Normal": Frontend sends request with just `text`
   - If mode is AI-enabled: Frontend sends request with `text`, `prompt`, and `mode`
5. Backend processes the text
   - For normal mode: Sends text directly to desktop
   - For AI mode: Uses prompt to process text, then sends result to desktop
6. Backend returns success status

### Error Handling
- Network failures: Show retry option
- API errors: Display specific error message
- Configuration errors: Guide user to setup
- Fallback: Allow sending unprocessed text

## Configuration Management

### Environment Variables
```
OPENAI_API_KEY=sk-...
AI_PROCESSOR_DEFAULT=openai
AI_PROCESSING_TIMEOUT=30
```

### Runtime Configuration
- Provider selection
- Model configuration
- Timeout settings
- Rate limiting

## Security Considerations

1. **API Key Protection**: Never expose API keys to frontend
2. **Input Sanitization**: Validate and sanitize all inputs
3. **Rate Limiting**: Prevent API abuse
4. **Logging**: Don't log sensitive text content
5. **HTTPS**: Use HTTPS in production

## Performance Considerations

1. **Async Processing**: Non-blocking AI API calls
2. **Timeout Handling**: Configurable timeouts for AI calls
3. **Caching**: Optional result caching for repeated inputs
4. **Streaming**: Future support for streaming responses

## Extension Points

### Adding New AI Providers
1. Implement `AIProcessor` interface
2. Register in `ProcessingService`
3. Add configuration options
4. Update documentation

### Custom Prompt Management
1. User-defined prompts
2. Prompt templates with variables
3. A/B testing for prompts
4. Prompt versioning

## Monitoring and Observability

1. **Metrics**: Processing time, success rate, API usage
2. **Logging**: Structured logs for debugging
3. **Health Checks**: Provider availability checks
4. **User Feedback**: Option to rate processing quality