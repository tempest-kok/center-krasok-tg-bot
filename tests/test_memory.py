from unittest import TestCase

from src.assistant_bot.memory import InMemoryDialogStore


class InMemoryDialogStoreTest(TestCase):
    def test_keeps_only_configured_number_of_messages(self) -> None:
        store = InMemoryDialogStore(max_messages=2)

        store.append_pair(1, "первый вопрос", "первый ответ")
        store.append_pair(1, "второй вопрос", "второй ответ")

        self.assertEqual(
            store.get(1),
            (
                {"role": "user", "content": "второй вопрос"},
                {"role": "assistant", "content": "второй ответ"},
            ),
        )
