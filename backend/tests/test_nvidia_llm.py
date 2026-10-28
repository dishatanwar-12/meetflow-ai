import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from backend.app.services.nvidia_llm import NvidiaLLMService, NvidiaLLMError

@pytest.mark.asyncio
async def test_nvidia_llm_unconfigured():
    svc = NvidiaLLMService(api_key=None)
    with pytest.raises(NvidiaLLMError) as exc_info:
        await svc.generate_chat_completion(messages=[{"role": "user", "content": "hi"}])
    assert "NVIDIA API Key is not configured" in str(exc_info.value)
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_nvidia_llm_mocked_success():
    svc = NvidiaLLMService(api_key="nvapi-test-key-mock")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "chatcmpl-123",
        "choices": [{
            "message": {"role": "assistant", "content": '{"meeting_summary": "Good meeting"}'}
        }],
        "usage": {"prompt_tokens": 50, "completion_tokens": 20}
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await svc.generate_chat_completion(messages=[{"role": "user", "content": "hello"}])
        assert res["id"] == "chatcmpl-123"
        assert res["usage"]["prompt_tokens"] == 50

@pytest.mark.asyncio
async def test_nvidia_llm_mocked_invalid_key():
    svc = NvidiaLLMService(api_key="nvapi-invalid-key")

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        with pytest.raises(NvidiaLLMError) as exc_info:
            await svc.generate_chat_completion(messages=[{"role": "user", "content": "hello"}])
        assert exc_info.value.status_code == 401
        assert "Invalid or unauthorized" in str(exc_info.value)

