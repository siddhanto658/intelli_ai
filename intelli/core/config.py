import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


@dataclass
class Settings:
    wolfram_alpha_api_key: str = ""
    news_api_key: str = ""
    hugchat_cookie_path: str = "cookies.json"
    gemini_api_key: str = ""
    use_local_llm: bool = False
    local_llm_url: str = "http://localhost:11434/api/generate"
    local_llm_model: str = "llama3"


_SETTINGS_CACHE: Optional[Settings] = None


def load_environment(env_file: str = ".env") -> None:
    """Load .env values if python-dotenv is available."""
    if load_dotenv is None:
        return
    env_path = Path(env_file)
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


def get_settings(refresh: bool = False) -> Settings:
    """Return cached settings from environment variables."""
    global _SETTINGS_CACHE
    if _SETTINGS_CACHE is None or refresh:
        _SETTINGS_CACHE = Settings(
            wolfram_alpha_api_key=os.getenv("WOLFRAM_ALPHA_API_KEY", "").strip(),
            news_api_key=os.getenv("NEWS_API_KEY", "").strip(),
            hugchat_cookie_path=os.getenv("HUGCHAT_COOKIE_PATH", "cookies.json").strip() or "cookies.json",
            gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
            use_local_llm=os.getenv("USE_LOCAL_LLM", "false").strip().lower() in ("true", "1", "t"),
            local_llm_url=os.getenv("LOCAL_LLM_URL", "http://localhost:11434/api/generate").strip(),
            local_llm_model=os.getenv("LOCAL_LLM_MODEL", "llama3").strip(),
        )
    return _SETTINGS_CACHE

