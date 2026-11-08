import os
from dataclasses import dataclass

@dataclass
class Settings:
    base_weekly_budget: float = float(os.getenv("BASE_WEEKLY_BUDGET", "1000.0"))
    min_multiplier: float = 0.5
    max_multiplier: float = 2.0
    llm_gateway_url: str = os.getenv("LLM_GATEWAY_URL", "http://100.105.249.12:4000/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "sk-aa7404dc8d605ad4a4569a8865b86ac25621df436577871334c5e83ae2d79a4b")
    llm_model: str = os.getenv("LLM_MODEL", "auto")
