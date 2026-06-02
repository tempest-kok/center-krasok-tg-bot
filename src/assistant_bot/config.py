from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - exercised only without deps installed.
    def load_dotenv() -> bool:
        return False


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    openai_api_key: str | None
    openai_model: str
    openai_base_url: str | None
    knowledge_path: Path
    max_history_messages: int
    top_k_facts: int
    max_answer_chars: int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is required. Add it to .env.")

        knowledge_path = Path(os.getenv("KNOWLEDGE_PATH", "data/company_knowledge.json"))
        if not knowledge_path.is_absolute():
            knowledge_path = PROJECT_ROOT / knowledge_path

        return cls(
            telegram_bot_token=token,
            openai_api_key=os.getenv("OPENAI_API_KEY", "").strip() or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
            openai_base_url=os.getenv("OPENAI_BASE_URL", "").strip() or None,
            knowledge_path=knowledge_path,
            max_history_messages=int(os.getenv("MAX_HISTORY_MESSAGES", "8")),
            top_k_facts=int(os.getenv("TOP_K_FACTS", "5")),
            max_answer_chars=int(os.getenv("MAX_ANSWER_CHARS", "3500")),
        )
