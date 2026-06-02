from __future__ import annotations

from collections.abc import Sequence

from .config import Settings
from .knowledge_base import KnowledgeBase
from .prompts import OUT_OF_SCOPE_ANSWER, SYSTEM_PROMPT, build_company_context

try:
    from openai import AsyncOpenAI
except ModuleNotFoundError:  # pragma: no cover - exercised only without deps installed.
    AsyncOpenAI = None  # type: ignore[assignment]


class AIClient:
    def __init__(self, settings: Settings, knowledge_base: KnowledgeBase) -> None:
        self.settings = settings
        self.knowledge_base = knowledge_base
        if settings.openai_api_key and AsyncOpenAI is None:
            raise RuntimeError(
                "Package 'openai' is required when OPENAI_API_KEY is configured. "
                "Install dependencies from requirements.txt."
            )
        self.client = (
            AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
            if settings.openai_api_key
            else None
        )

    async def answer(self, user_message: str, history: Sequence[dict[str, str]]) -> str:
        matches = self.knowledge_base.search(
            user_message,
            limit=self.settings.top_k_facts,
        )
        if not matches:
            return OUT_OF_SCOPE_ANSWER

        if self.client is None:
            return self.knowledge_base.fallback_answer(user_message)

        context = self.knowledge_base.format_items(matches)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": build_company_context(context)},
            *history,
            {"role": "user", "content": user_message},
        ]

        response = await self.client.chat.completions.create(
            model=self.settings.openai_model,
            messages=messages,
            temperature=0.2,
            max_tokens=650,
        )
        answer = response.choices[0].message.content
        answer = (answer or "").strip()
        if not answer:
            return "Не удалось сформировать ответ. Попробуйте переформулировать вопрос."
        return trim_answer(answer, self.settings.max_answer_chars)


def trim_answer(answer: str, max_chars: int) -> str:
    if len(answer) <= max_chars:
        return answer
    return answer[: max_chars - 1].rstrip() + "…"
