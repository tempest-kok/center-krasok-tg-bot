from pathlib import Path
from unittest import TestCase

from src.assistant_bot.knowledge_base import KnowledgeBase, expanded_tokens, tokenize


ROOT = Path(__file__).resolve().parents[1]


class KnowledgeBaseTest(TestCase):
    def setUp(self) -> None:
        self.knowledge_base = KnowledgeBase(ROOT / "data" / "company_knowledge.json")

    def test_tokenize_removes_short_words_and_stop_words(self) -> None:
        self.assertEqual(tokenize("Где офис и какие бренды?"), ["офис", "бренды"])

    def test_search_finds_contacts(self) -> None:
        result = self.knowledge_base.search("Где находится офис в Алматы?", limit=2)
        self.assertTrue(result)
        self.assertEqual(result[0].id, "locations")

    def test_search_finds_vacancies(self) -> None:
        result = self.knowledge_base.search("Какие есть вакансии?", limit=2)
        self.assertTrue(result)
        self.assertEqual(result[0].id, "vacancies")

    def test_search_finds_designers(self) -> None:
        result = self.knowledge_base.search("Что вы предлагаете дизайнерам?", limit=2)
        self.assertTrue(result)
        self.assertEqual(result[0].id, "designers")

    def test_query_expansion_adds_related_terms(self) -> None:
        tokens = expanded_tokens("Какая доставка?")
        self.assertIn("курьер", tokens)

    def test_context_contains_company_fact(self) -> None:
        context = self.knowledge_base.build_context("Чем занимается компания?")
        self.assertIn("Центр Красок #1", context)
