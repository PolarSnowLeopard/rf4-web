from typing import Any

import litellm
from litellm import completion, acompletion

from services.llm.config import get_llm_settings
from services.llm.exceptions import LlmUpstreamError, LlmTimeoutError, LlmInvalidResponseError

litellm.drop_params = True


def chat_completion(
    *,
    messages: list[dict],
    model: str | None = None,
    response_format: dict | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = None,
    timeout: float = 60.0,
    **kwargs: Any,
) -> str:
    """Synchronous LLM call. Returns message.content string."""
    settings = get_llm_settings()
    model = model or settings.default_llm_model

    call_kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "timeout": timeout,
        "api_key": settings.openrouter_api_key,
        "api_base": settings.openrouter_base_url,
    }
    if response_format is not None:
        call_kwargs["response_format"] = response_format
    if max_tokens is not None:
        call_kwargs["max_tokens"] = max_tokens
    call_kwargs.update(kwargs)

    try:
        resp = completion(**call_kwargs)
    except litellm.Timeout as e:
        raise LlmTimeoutError(f"LLM call timed out: {e}") from e
    except Exception as e:
        raise LlmUpstreamError(f"LLM upstream call failed: {e}") from e

    try:
        return resp.choices[0].message.content
    except (AttributeError, IndexError) as e:
        raise LlmInvalidResponseError(f"Invalid LLM response shape: {resp}") from e


async def achat_completion(
    *,
    messages: list[dict],
    model: str | None = None,
    response_format: dict | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = None,
    timeout: float = 60.0,
    **kwargs: Any,
) -> str:
    """Async LLM call. Returns message.content string."""
    settings = get_llm_settings()
    model = model or settings.default_llm_model

    call_kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "timeout": timeout,
        "api_key": settings.openrouter_api_key,
        "api_base": settings.openrouter_base_url,
    }
    if response_format is not None:
        call_kwargs["response_format"] = response_format
    if max_tokens is not None:
        call_kwargs["max_tokens"] = max_tokens
    call_kwargs.update(kwargs)

    try:
        resp = await acompletion(**call_kwargs)
    except litellm.Timeout as e:
        raise LlmTimeoutError(f"LLM call timed out: {e}") from e
    except Exception as e:
        raise LlmUpstreamError(f"LLM upstream call failed: {e}") from e

    try:
        return resp.choices[0].message.content
    except (AttributeError, IndexError) as e:
        raise LlmInvalidResponseError(f"Invalid LLM response shape: {resp}") from e
