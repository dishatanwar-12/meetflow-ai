import json
import logging
import asyncio
from typing import Dict, Any, Optional
import httpx
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class NvidiaLLMError(Exception):
    """Custom exception raised when NVIDIA NIM inference fails."""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

_DEFAULT_UNSET = object()

class NvidiaLLMService:
    def __init__(self, api_key: Any = _DEFAULT_UNSET, base_url: Optional[str] = None, model: Optional[str] = None):
        if api_key is _DEFAULT_UNSET:
            self.api_key = settings.NVIDIA_API_KEY
        else:
            self.api_key = api_key
        self.base_url = (base_url or settings.NVIDIA_BASE_URL).rstrip("/")
        self.model = model or settings.NVIDIA_MODEL
        self.timeout = settings.NVIDIA_TIMEOUT_SECONDS
        self.max_retries = settings.NVIDIA_MAX_RETRIES

    def is_configured(self) -> bool:
        """Checks if a valid-looking NVIDIA API key is configured."""
        if not self.api_key:
            return False
        key = str(self.api_key).strip()
        if len(key) <= 5 or key.startswith("your_real_nvidia_nim"):
            return False
        return True

    async def generate_chat_completion(
        self,
        messages: list,
        temperature: float = 0.1,
        response_format: Optional[Dict[str, str]] = None,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """
        Sends an OpenAI-compatible chat completion request to the real NVIDIA NIM endpoint.
        Handles timeouts, rate limits (HTTP 429), and safe retries with exponential backoff.
        """
        if not self.is_configured():
            raise NvidiaLLMError(
                "NVIDIA API Key is not configured. Please set the NVIDIA_API_KEY environment variable.",
                status_code=401
            )

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            payload["response_format"] = response_format

        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    logger.info(f"Dispatching NVIDIA NIM request (Attempt {attempt}/{self.max_retries}) to {endpoint}")
                    response = await client.post(endpoint, headers=headers, json=payload)

                    if response.status_code == 200:
                        data = response.json()
                        return data
                    elif response.status_code == 429:
                        # Rate limit reached
                        retry_after = int(response.headers.get("Retry-After", 2 * attempt))
                        logger.warning(f"NVIDIA NIM rate limit (429) hit. Waiting {retry_after}s before retry.")
                        if attempt == self.max_retries:
                            raise NvidiaLLMError(
                                "NVIDIA NIM rate limit exceeded. Please wait a moment and try again.",
                                status_code=429
                            )
                        await asyncio.sleep(retry_after)
                        continue
                    elif response.status_code == 401 or response.status_code == 403:
                        raise NvidiaLLMError(
                            "Invalid or unauthorized NVIDIA API key. Please check your credentials at build.nvidia.com.",
                            status_code=response.status_code,
                            details=response.text
                        )
                    elif response.status_code >= 500:
                        logger.warning(f"NVIDIA NIM server error ({response.status_code}): {response.text}")
                        if attempt == self.max_retries:
                            raise NvidiaLLMError(
                                f"NVIDIA NIM service currently unavailable (HTTP {response.status_code}). Please retry later.",
                                status_code=response.status_code,
                                details=response.text
                            )
                        await asyncio.sleep(1.5 * attempt)
                        continue
                    else:
                        raise NvidiaLLMError(
                            f"NVIDIA NIM API request failed with status {response.status_code}: {response.text}",
                            status_code=response.status_code,
                            details=response.text
                        )

            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning(f"Timeout calling NVIDIA NIM (Attempt {attempt}/{self.max_retries})")
                if attempt == self.max_retries:
                    raise NvidiaLLMError(
                        f"Request to NVIDIA NIM timed out after {self.timeout} seconds.",
                        status_code=504
                    )
                await asyncio.sleep(2 * attempt)
            except httpx.RequestError as exc:
                last_error = exc
                logger.warning(f"Network error calling NVIDIA NIM: {str(exc)}")
                if attempt == self.max_retries:
                    raise NvidiaLLMError(
                        f"Network connectivity error reaching NVIDIA NIM: {str(exc)}",
                        status_code=502
                    )
                await asyncio.sleep(2 * attempt)

        raise NvidiaLLMError(f"Failed to communicate with NVIDIA NIM: {str(last_error)}")

    async def test_connectivity(self) -> Dict[str, Any]:
        """Performs a lightweight sanity check to verify NVIDIA NIM credentials."""
        if not self.is_configured():
            return {
                "configured": False,
                "model": self.model,
                "message": "NVIDIA_API_KEY is not set."
            }

        try:
            res = await self.generate_chat_completion(
                messages=[{"role": "user", "content": "Respond with the single word 'READY'."}],
                max_tokens=10,
                temperature=0.0
            )
            content = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return {
                "configured": True,
                "connected": True,
                "model": self.model,
                "response": content,
                "usage": res.get("usage", {})
            }
        except NvidiaLLMError as e:
            return {
                "configured": True,
                "connected": False,
                "model": self.model,
                "error": e.message,
                "status_code": e.status_code
            }

