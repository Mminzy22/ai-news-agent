from __future__ import annotations

from datetime import datetime, timezone
import unittest

from src.models import Article
from src.ranker import select_articles


class RankingTests(unittest.TestCase):
    def test_selects_ai_related_articles(self) -> None:
        articles = [
            Article("HN", "OpenAI releases coding agent", "https://a.example", datetime.now(timezone.utc), "", "en"),
            Article("HN", "A recipe for bread", "https://b.example", datetime.now(timezone.utc), "", "en"),
        ]

        selected = select_articles(articles, max_articles=5, lookback_hours=24)

        self.assertEqual([item.url for item in selected], ["https://a.example"])

    def test_deduplicates_similar_titles(self) -> None:
        articles = [
            Article(
                "AI Times",
                "문샷 AI, 코딩 성능 개선 및 추론 비용 30% 절감한 키미 K2.7-코드 공개",
                "https://a.example",
                datetime.now(timezone.utc),
                "문샷 AI Kimi K2.7 Code 코딩 모델",
                "ko",
                1.1,
            ),
            Article(
                "GeekNews",
                "Moonshot AI가 Kimi K2.7-Code를 출시했습니다.",
                "https://b.example",
                datetime.now(timezone.utc),
                "Moonshot AI Kimi K2.7 Code 코딩 모델",
                "ko",
                1.3,
            ),
        ]

        selected = select_articles(articles, max_articles=5, lookback_hours=24)

        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].url, "https://b.example")

    def test_keeps_different_articles_with_shared_ai_keyword(self) -> None:
        articles = [
            Article("A", "OpenAI releases coding agent", "https://a.example", datetime.now(timezone.utc), "", "en"),
            Article("B", "Google studies LLM hallucination", "https://b.example", datetime.now(timezone.utc), "", "en"),
        ]

        selected = select_articles(articles, max_articles=5, lookback_hours=24)

        self.assertEqual(len(selected), 2)


if __name__ == "__main__":
    unittest.main()
