import os
import asyncio
from typing import Optional
import aiohttp
import json
from .processor import AIProcessor


class ZAIProcessor(AIProcessor):
    """ZAI (智谱AI) processor implementation using Anthropic-compatible protocol"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize ZAI processor

        Args:
            api_key: ZAI API key (if None, will try to get from environment)
            model: Model name to use (if None, will try to get from environment)
            base_url: API base URL (if None, will try to get from environment)
        """
        self.api_key = api_key or os.getenv("ZAI_API_KEY")
        self.model = model or os.getenv("ZAI_MODEL", "glm-4")
        # Get base URL and ensure it ends with /v1/messages
        base = base_url or os.getenv("ZAI_API_BASE_URL", "https://open.bigmodel.cn/api/anthropic")
        # Auto-append /v1/messages if not already present
        if not base.endswith("/v1/messages"):
            base = base.rstrip("/") + "/v1/messages"
        self.base_url = base
        self.timeout = int(os.getenv("AI_PROCESSING_TIMEOUT", "30"))
        self.max_tokens = 4000

    def is_configured(self) -> bool:
        """Check if processor has valid API key"""
        return bool(self.api_key)

    async def process_text(self, text: str, prompt: str) -> Optional[str]:
        """
        Process text using ZAI API with Anthropic-compatible protocol

        Args:
            text: Input text to process
            prompt: Processing prompt

        Returns:
            Processed text or None if failed
        """
        if not self.is_configured():
            raise ValueError("ZAI API key not configured")

        if not prompt:
            # If no prompt, return text as-is
            return text

        try:
            # Prepare the full message
            user_message = prompt.replace("{user_input}", f"<user_input>\n{text}\n</user_input>")

            # Prepare request payload using Anthropic-compatible format
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
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }

            # Make async request with retries
            max_retries = 2
            for attempt in range(max_retries + 1):
                # Debug: log request info (only first attempt to avoid spam)
                debug_request = (attempt == 0 and os.getenv("ZAI_DEBUG", "false").lower() == "true")
                try:
                    if debug_request:
                        print(f"\n[ZAI Debug] ===== REQUEST DEBUG =====")
                        print(f"URL: {self.base_url}")
                        print(f"Model: {self.model}")
                        print(f"Headers: {{'Authorization': 'Bearer ***', 'Content-Type': 'application/json'}}")
                        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
                        print("=" * 40)

                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                        async with session.post(self.base_url, json=payload, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()

                                # Debug: log the response structure
                                print(f"[ZAI Debug] Response status: 200")
                                print(f"[ZAI Debug] Response keys: {list(data.keys())}")

                                # Extract processed text from response
                                # Try Anthropic format first
                                if "content" in data and data["content"]:
                                    print(f"[ZAI Debug] Found 'content' field with {len(data['content'])} items")
                                    if data["content"][0]["type"] == "text":
                                        processed_text = data["content"][0]["text"]
                                        if processed_text and processed_text.strip():
                                            print(f"[ZAI Debug] Successfully extracted text (length: {len(processed_text)})")
                                            return processed_text.strip()
                                        else:
                                            print("[ZAI Error] Extracted text is empty")
                                    else:
                                        print(f"[ZAI Error] Unexpected content type: {data['content'][0]['type']}")
                                else:
                                    print("[ZAI Debug] No 'content' field found")

                                # Fallback to OpenAI format
                                if "choices" in data and data["choices"]:
                                    print(f"[ZAI Debug] Found 'choices' field with {len(data['choices'])} items")
                                    if data["choices"][0].get("message") and data["choices"][0]["message"].get("content"):
                                        processed_text = data["choices"][0]["message"]["content"]
                                        if processed_text and processed_text.strip():
                                            print(f"[ZAI Debug] Successfully extracted text from OpenAI format (length: {len(processed_text)})")
                                            return processed_text.strip()
                                        else:
                                            print("[ZAI Error] OpenAI format text is empty")
                                    else:
                                        print("[ZAI Error] Invalid OpenAI format structure")
                                else:
                                    print("[ZAI Debug] No 'choices' field found")

                                # If we get here, the response format is unexpected
                                print("\n[ZAI Error] ===== UNEXPECTED RESPONSE FORMAT =====")
                                print("Status Code:", response.status)
                                print("Response Headers:", dict(response.headers))
                                print("\nFull Response:")
                                print(json.dumps(data, indent=2, ensure_ascii=False))
                                print("=" * 50)
                                return None
                            elif response.status == 429:
                                # Rate limited, wait and retry
                                if attempt < max_retries:
                                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                    continue
                                print("[ZAI Error] Rate limit exceeded")
                                return None
                            elif response.status == 401:
                                # Invalid API key
                                error_data = await response.text()
                                print(f"\n[ZAI Error] ===== AUTHENTICATION ERROR =====")
                                print("Status Code: 401 Unauthorized")
                                print("Response Headers:", dict(response.headers))
                                print("\nError Response:")
                                try:
                                    error_json = await response.json()
                                    print(json.dumps(error_json, indent=2, ensure_ascii=False))
                                except:
                                    print(error_data)
                                print("=" * 50)
                                return None
                            else:
                                error_text = await response.text()
                                print(f"\n[ZAI Error] ===== HTTP ERROR =====")
                                print(f"Status Code: {response.status}")
                                print("Response Headers:", dict(response.headers))
                                print("\nError Response:")
                                try:
                                    error_json = await response.json()
                                    print(json.dumps(error_json, indent=2, ensure_ascii=False))
                                except:
                                    print(error_text)
                                print("=" * 50)
                                if attempt < max_retries:
                                    await asyncio.sleep(1)
                                    continue
                                return None

                except asyncio.TimeoutError:
                    if attempt < max_retries:
                        print(f"[ZAI Error] Request timed out, retrying... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(1)
                        continue
                    print("[ZAI Error] Request timed out after retries")
                    return None

        except Exception as e:
            print(f"\n[ZAI Error] ===== UNEXPECTED ERROR =====")
            print(f"Error: {str(e)}")
            print(f"Attempt: {attempt}/{max_retries + 1}")
            print(f"URL: {self.base_url}")
            print("=" * 50)
            import traceback
            traceback.print_exc()
            return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        pass