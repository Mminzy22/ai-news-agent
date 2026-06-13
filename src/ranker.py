from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import re

from .models import Article


KEYWORDS = {
    "ai": 3,
    "artificial intelligence": 3,
    "llm": 3,
    "openai": 4,
    "anthropic": 4,
    "claude": 3,
    "chatgpt": 3,
    "gemini": 3,
    "agent": 2,
    "coding": 2,
    "developer": 2,
    "github": 2,
    "security": 2,
    "cloud": 1,
    "kubernetes": 2,
    "model": 1,
    "인공지능": 3,
    "생성형": 3,
    "에이전트": 3,
    "오픈ai": 4,
    "앤트로픽": 4,
    "클로드": 3,
    "제미나이": 3,
    "개발자": 2,
    "코딩": 2,
    "보안": 2,
    "클라우드": 1,
    "모델": 1,
}


def select_articles(articles: list[Article], max_articles: int, lookback_hours: int) -> list[Article]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    seen_urls: set[str] = set()
    candidates: list[Article] = []

    for article in articles:
        if article.url in seen_urls:
            continue
        if article.published_at and article.published_at < cutoff:
            continue
        seen_urls.add(article.url)
        scored = _score(article)
        if scored.score > 0:
            candidates.append(scored)

    selected: list[Article] = []
    for article in sorted(candidates, key=lambda item: item.score, reverse=True):
        if any(_is_similar_title(article.title, existing.title) for existing in selected):
            continue
        selected.append(article)
        if len(selected) >= max_articles:
            break

    return selected


def article_id(article: Article) -> str:
    return hashlib.sha256(article.url.encode("utf-8")).hexdigest()[:16]


def _score(article: Article) -> Article:
    haystack = f"{article.title}\n{article.summary_text}".lower()
    score = article.score
    for keyword, weight in KEYWORDS.items():
        if keyword.lower() in haystack:
            score += weight
    return Article(
        source=article.source,
        title=article.title,
        url=article.url,
        published_at=article.published_at,
        summary_text=article.summary_text,
        language=article.language,
        score=score,
    )


def _is_similar_title(left: str, right: str) -> bool:
    left_tokens = _title_tokens(left)
    right_tokens = _title_tokens(right)
    if not left_tokens or not right_tokens:
        return False

    overlap = left_tokens & right_tokens
    smaller_ratio = len(overlap) / min(len(left_tokens), len(right_tokens))
    jaccard = len(overlap) / len(left_tokens | right_tokens)
    return smaller_ratio >= 0.55 or jaccard >= 0.42


def _title_tokens(title: str) -> set[str]:
    normalized = title.lower()
    normalized = normalized.replace("오픈소스", "open source")
    normalized = normalized.replace("오픈ai", "openai")
    normalized = normalized.replace("앤트로픽", "anthropic")
    normalized = normalized.replace("클로드", "claude")
    normalized = normalized.replace("키미", "kimi")
    normalized = normalized.replace("문샷", "moonshot")
    tokens = set(re.findall(r"[0-9a-z]+|[가-힣]+", normalized))
    return {token for token in tokens if len(token) >= 2 and token not in _TITLE_STOPWORDS}


_TITLE_STOPWORDS = {
    "ai",
    "및",
    "위한",
    "공개",
    "출시",
    "발표",
    "기반",
    "관련",
    "news",
    "show",
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "code",
}
