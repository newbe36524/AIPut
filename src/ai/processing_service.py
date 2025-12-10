import os
import asyncio
from typing import Optional, Dict, Type
from .processor import AIProcessor
from .zai_processor import ZAIProcessor
from .anthropic_processor import AnthropicProcessor


class ProcessingService:
    """Service for managing AI text processing"""

    def __init__(self):
        """Initialize processing service with available processors"""
        self.processors: Dict[str, Type[AIProcessor]] = {}
        self._instances: Dict[str, AIProcessor] = {}
        self.default_provider = os.getenv("AI_PROCESSOR_DEFAULT", "anthropic")
        self.timeout = int(os.getenv("AI_PROCESSING_TIMEOUT", "30"))

        # Register built-in processors
        self.register_processor("anthropic", AnthropicProcessor)
        self.register_processor("zai", ZAIProcessor)

    def register_processor(self, name: str, processor_class: Type[AIProcessor]):
        """
        Register a new AI processor

        Args:
            name: Processor name
            processor_class: Processor class
        """
        self.processors[name] = processor_class

    def get_processor(self, provider: str) -> Optional[AIProcessor]:
        """
        Get or create processor instance

        Args:
            provider: Provider name

        Returns:
            Processor instance or None if not found
        """
        # Return cached instance if available
        if provider in self._instances:
            return self._instances[provider]

        # Create new instance
        processor_class = self.processors.get(provider)
        if not processor_class:
            return None

        try:
            # Initialize processor
            if provider == "zai":
                instance = processor_class()
            else:
                # For future processors, might need different initialization
                instance = processor_class()

            # Cache instance
            self._instances[provider] = instance
            return instance

        except Exception as e:
            print(f"[ProcessingService] Failed to initialize {provider}: {str(e)}")
            return None

    async def process(self, text: str, prompt: str, provider: Optional[str] = None, mode: Optional[str] = None) -> Optional[str]:
        """
        Process text with AI

        Args:
            text: Input text
            prompt: Processing prompt
            provider: AI provider (uses default if None)
            mode: Processing mode (for logging)

        Returns:
            Processed text or None if failed
        """
        # Log the mode for analytics/debugging purposes
        if mode:
            print(f"[AI Processing] Using mode: {mode}")

        # Use default provider if not specified
        provider = provider or self.default_provider

        # If no prompt, return text as-is
        if not prompt or not prompt.strip():
            print("[AI Processing] No prompt provided, returning original text")
            return text

        # Get processor
        processor = self.get_processor(provider)
        if not processor:
            print(f"[AI Processing] Unknown provider: {provider}")
            return None

        # Check if processor is configured
        if not processor.is_configured():
            print(f"[AI Processing] Provider {provider} not configured")
            return None

        try:
            # Process with timeout
            result = await asyncio.wait_for(
                processor.process_text(text, prompt),
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            print(f"[AI Processing] Processing timed out after {self.timeout} seconds")
            return None
        except Exception as e:
            print(f"[AI Processing] Error during processing: {str(e)}")
            return None

    def list_providers(self) -> list:
        """List available providers"""
        return list(self.processors.keys())

    def is_provider_configured(self, provider: Optional[str] = None) -> bool:
        """
        Check if a provider is configured

        Args:
            provider: Provider name (uses default if None)

        Returns:
            True if provider is configured
        """
        provider = provider or self.default_provider
        processor = self.get_processor(provider)
        return processor.is_configured() if processor else False