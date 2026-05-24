import os
from dataclasses import dataclass

import dotenv
dotenv.load_dotenv()


@dataclass(frozen=True)
class LlmSettings:
    openrouter_api_key: str
    openrouter_base_url: str
    default_llm_model: str
    default_vlm_model: str


def get_llm_settings() -> LlmSettings:
    return LlmSettings(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        default_llm_model=os.getenv("DEFAULT_LLM_MODEL", "openrouter/google/gemini-3.5-flash"),
        default_vlm_model=os.getenv("DEFAULT_VLM_MODEL", "openrouter/google/gemini-3.5-flash"),
    )
