from abc import ABC, abstractmethod
from typing import Optional


class AIProcessor(ABC):
    """Abstract base class for AI text processors"""

    @abstractmethod
    async def process_text(self, text: str, prompt: str) -> Optional[str]:
        """
        Process text using AI with given prompt

        Args:
            text: The input text to process
            prompt: The prompt to guide processing

        Returns:
            Processed text or None if processing fails
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """
        Check if processor is properly configured

        Returns:
            True if processor has valid configuration
        """
        pass