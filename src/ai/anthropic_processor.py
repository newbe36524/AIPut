import os
import asyncio
from typing import Optional
import aiohttp
import json
from .processor import AIProcessor


class AnthropicProcessor(AIProcessor):
    """Anthropic Claude processor implementation"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize Anthropic processor

        Args:
            api_key: Anthropic API key (if None, will try to get from environment)
            model: Model name to use (if None, will try to get from environment)
            base_url: API base URL (if None, will try to get from environment)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.base_url = base_url or os.getenv("ANTHROPIC_API_BASE_URL", "https://api.anthropic.com/v1/messages")
        self.timeout = int(os.getenv("AI_PROCESSING_TIMEOUT", "30"))
        self.max_tokens = 4000  # Claude's max tokens limit

    def is_configured(self) -> bool:
        """Check if processor has valid API key"""
        return bool(self.api_key)

    async def process_text(self, text: str, prompt: str) -> Optional[str]:
        """
        Process text using Anthropic API

        Args:
            text: Input text to process
            prompt: Processing prompt

        Returns:
            Processed text or None if failed
        """
        if not self.is_configured():
            raise ValueError("Anthropic API key not configured")

        if not prompt:
            # If no prompt, return text as-is
            return text

        try:
            # Prepare the full message
            user_message = prompt.replace("{user_input}", f"<user_input>\n{text}\n</user_input>")

            # Prepare request payload for Claude API
            payload = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.7
            }

            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }

            # Make async request with retries
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                        async with session.post(self.base_url, json=payload, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()

                                # Extract processed text from Claude response
                                if "content" in data and data["content"]:
                                    if data["content"][0]["type"] == "text":
                                        processed_text = data["content"][0]["text"]
                                        if processed_text and processed_text.strip():
                                            return processed_text.strip()
                                        else:
                                            print("[Anthropic Error] Empty response from API")
                                            return None
                                    else:
                                        print("[Anthropic Error] Unexpected content type")
                                        return None
                                else:
                                    print("[Anthropic Error] No content in response")
                                    print(f"Response: {json.dumps(data, indent=2)}")
                                    return None
                            elif response.status == 429:
                                # Rate limited, wait and retry
                                if attempt < max_retries:
                                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                    continue
                                print("[Anthropic Error] Rate limit exceeded")
                                return None
                            elif response.status == 401:
                                # Invalid API key
                                error_data = await response.json()
                                print(f"[Anthropic Error] Invalid API key: {error_data.get('error', {}).get('message', 'Unknown error')}")
                                return None
                            elif response.status == 400:
                                # Bad request
                                error_data = await response.json()
                                print(f"[Anthropic Error] Bad request: {error_data.get('error', {}).get('message', 'Unknown error')}")
                                return None
                            else:
                                error_text = await response.text()
                                print(f"[Anthropic Error] HTTP {response.status}: {error_text}")
                                if attempt < max_retries:
                                    await asyncio.sleep(1)
                                    continue
                                return None

                except asyncio.TimeoutError:
                    if attempt < max_retries:
                        print(f"[Anthropic Error] Request timed out, retrying... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(1)
                        continue
                    print("[Anthropic Error] Request timed out after retries")
                    return None

        except Exception as e:
            print(f"[Anthropic Error] Processing failed: {str(e)}")
            return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        pass