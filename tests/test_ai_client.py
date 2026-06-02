from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from src.assistant_bot.ai_client import AIClient, trim_answer
from src.assistant_bot.config import Settings
from src.assistant_bot.knowledge_base import KnowledgeBase
from src.assistant_bot.prompts import OUT_OF_SCOPE_ANSWER


ROOT = Path(__file__).resolve().parents[1]


class AIClientTest(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.settings = Settings(
            telegram_bot_token="test-token",
            openai_api_key=None,
            openai_model="gpt-4o-mini",
            openai_base_url=None,
            knowledge_path=ROOT / "data" / "company_knowledge.json",
            max_history_messages=8,
            top_k_facts=5,
            max_answer_chars=3500,
        )
        self.client = AIClient(
            self.settings,
            KnowledgeBase(self.settings.knowledge_path),
        )

    async def test_returns_refusal_when_no_company_facts_found(self) -> None:
        answer = await self.client.answer("Кто президент США?", history=())
        self.assertEqual(answer, OUT_OF_SCOPE_ANSWER)

    async def test_local_fallback_uses_knowledge_base_when_api_key_missing(self) -> None:
        answer = await self.client.answer("Какие бренды есть?", history=())
        self.assertIn("AI API не подключен", answer)
        self.assertIn("Dulux", answer)


class TrimAnswerTest(IsolatedAsyncioTestCase):
    async def test_trim_answer_keeps_short_text(self) -> None:
        self.assertEqual(trim_answer("коротко", 20), "коротко")

    async def test_trim_answer_shortens_long_text(self) -> None:
        self.assertEqual(trim_answer("abcdef", 4), "abc…")
