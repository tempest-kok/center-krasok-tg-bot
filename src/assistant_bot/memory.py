from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Sequence


MessageHistory = tuple[dict[str, str], ...]


class InMemoryDialogStore:
    """Stores short per-chat history for polling MVP deployments."""

    def __init__(self, max_messages: int) -> None:
        self._items: dict[int, deque[dict[str, str]]] = defaultdict(
            lambda: deque(maxlen=max_messages)
        )

    def get(self, chat_id: int) -> MessageHistory:
        return tuple(self._items[chat_id])

    def append_pair(self, chat_id: int, user_text: str, assistant_text: str) -> None:
        self._items[chat_id].append({"role": "user", "content": user_text})
        self._items[chat_id].append({"role": "assistant", "content": assistant_text})

    def seed(self, chat_id: int, messages: Sequence[dict[str, str]]) -> None:
        self._items[chat_id].clear()
        self._items[chat_id].extend(messages)
