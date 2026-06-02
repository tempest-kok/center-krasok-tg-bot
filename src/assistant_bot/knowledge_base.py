from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


TOKEN_RE = re.compile(r"[a-zа-я0-9]+", re.IGNORECASE)
STOP_WORDS = {
    "а",
    "в",
    "где",
    "для",
    "и",
    "или",
    "как",
    "какие",
    "какой",
    "компания",
    "на",
    "о",
    "об",
    "по",
    "с",
    "у",
    "ты",
    "что",
    "чем",
    "это",
}

QUERY_EXPANSIONS = {
    "адрес": ("контакты", "офис", "салон", "алматы", "астана"),
    "адреса": ("адрес", "контакты", "офис", "салон"),
    "контакт": ("контакты", "телефон", "email"),
    "контакты": ("телефон", "email", "адрес"),
    "доставка": ("курьер", "служба", "заказ", "двери"),
    "доставить": ("доставка", "курьер", "заказ"),
    "цена": ("стоимость", "прайс", "наличие"),
    "цены": ("цена", "стоимость", "прайс", "наличие"),
    "стоимость": ("цена", "прайс", "наличие"),
    "бренд": ("марка", "dulux", "marshall", "pinotex"),
    "бренды": ("бренд", "марка", "dulux", "marshall", "pinotex"),
    "вакансия": ("работа", "карьера", "hh"),
    "вакансии": ("вакансия", "работа", "карьера", "hh"),
    "дизайнер": ("партнер", "проект", "лояльность"),
    "дизайнеры": ("дизайнер", "партнер", "проект", "лояльность"),
    "дизайнерам": ("дизайнер", "дизайнеры", "партнер", "проект"),
    "строитель": ("бригада", "партнер", "объект"),
    "строители": ("строитель", "бригада", "партнер", "объект"),
    "строителям": ("строитель", "бригада", "партнер", "объект"),
}


@dataclass(frozen=True)
class KnowledgeItem:
    id: str
    title: str
    text: str
    tags: tuple[str, ...]
    score: int = 0


class KnowledgeBase:
    def __init__(self, path: Path) -> None:
        self.path = path
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.company = payload["company"]
        self.sources = payload["sources"]
        self.items = [
            KnowledgeItem(
                id=item["id"],
                title=item["title"],
                text=item["text"],
                tags=tuple(item.get("tags", [])),
            )
            for item in payload["facts"]
        ]

    def search(self, query: str, limit: int = 4) -> list[KnowledgeItem]:
        query_tokens = expanded_tokens(query)
        if not query_tokens:
            return []

        ranked: list[KnowledgeItem] = []
        for item in self.items:
            haystack = set(tokenize(" ".join([item.title, item.text, " ".join(item.tags)])))
            tag_tokens = set(tokenize(" ".join(item.tags)))
            score = len(query_tokens & haystack) + 2 * len(query_tokens & tag_tokens)
            if score > 0:
                ranked.append(
                    KnowledgeItem(
                        id=item.id,
                        title=item.title,
                        text=item.text,
                        tags=item.tags,
                        score=score,
                    )
                )

        return sorted(ranked, key=lambda item: item.score, reverse=True)[:limit]

    def build_context(self, query: str, limit: int = 4) -> str:
        matches = self.search(query, limit=limit)
        return self.format_items(matches)

    @staticmethod
    def format_items(matches: list[KnowledgeItem]) -> str:
        blocks = [
            f"[{index}] {item.title}\n{item.text}"
            for index, item in enumerate(matches, start=1)
        ]
        return "\n\n".join(blocks) if blocks else "Релевантные факты не найдены."

    def fallback_answer(self, query: str) -> str:
        matches = self.search(query, limit=3)
        if not matches:
            return (
                "Я отвечаю только по информации о Центр Красок #1. "
                "В базе знаний нет точных данных по этому вопросу, лучше уточнить у менеджеров "
                "по телефону +7 778 061 5000 или на сайте https://centr-krasok.kz/."
            )

        facts = "\n".join(f"- {item.text}" for item in matches)
        return (
            "Сейчас AI API не подключен, поэтому отвечаю по найденным фрагментам базы знаний:\n"
            f"{facts}"
        )


def tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_RE.findall(text)
        if len(token) > 2 and token.lower() not in STOP_WORDS
    ]


def expanded_tokens(text: str) -> set[str]:
    tokens = set(tokenize(text))
    for token in tuple(tokens):
        tokens.update(QUERY_EXPANSIONS.get(token, ()))
    return tokens
