from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatAction
from aiogram.types import Message

from .ai_client import AIClient
from .config import Settings
from .knowledge_base import KnowledgeBase
from .memory import InMemoryDialogStore
from .prompts import NON_TEXT_ANSWER


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    settings = Settings.from_env()
    knowledge_base = KnowledgeBase(settings.knowledge_path)
    ai_client = AIClient(settings, knowledge_base)

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()
    histories = InMemoryDialogStore(settings.max_history_messages)

    @dispatcher.message(F.text)
    async def handle_text(message: Message) -> None:
        if not message.text:
            return

        chat_id = message.chat.id
        user_text = message.text.strip()
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        try:
            answer = await ai_client.answer(user_text, histories.get(chat_id))
        except Exception:
            logger.exception("Failed to process message from chat %s", chat_id)
            answer = (
                "Не смог обработать вопрос из-за технической ошибки. "
                "Попробуйте еще раз чуть позже."
            )

        histories.append_pair(chat_id, user_text, answer)
        await message.answer(answer)

    @dispatcher.message()
    async def handle_other(message: Message) -> None:
        await message.answer(NON_TEXT_ANSWER)

    logger.info("Bot started")
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
