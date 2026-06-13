from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

from .models import Article, Summary


def summarize_articles(articles: list[Article], api_key: str, model: str) -> list[Summary]:
    if not articles:
        return []
    if not api_key:
        return [_fallback_summary(article) for article in articles]

    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": (
                    "You summarize AI and software development news for a Korean Slack digest. "
                    "Return concise Korean JSON only."
                ),
            },
            {
                "role": "user",
                "content": _prompt(articles),
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "news_digest",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "title": {"type": "string"},
                                    "source": {"type": "string"},
                                    "url": {"type": "string"},
                                    "summary": {"type": "string"},
                                    "why_it_matters": {"type": "string"},
                                },
                                "required": ["title", "source", "url", "summary", "why_it_matters"],
                            },
                        }
                    },
                    "required": ["items"],
                },
                "strict": True,
            }
        },
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"warning: OpenAI API failed: HTTP {exc.code} {detail[:500]}", file=sys.stderr)
        return [_fallback_summary(article) for article in articles]
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"warning: OpenAI API failed: {exc}", file=sys.stderr)
        return [_fallback_summary(article) for article in articles]

    text = _extract_output_text(data)
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"warning: OpenAI response was not valid JSON: {exc}", file=sys.stderr)
        return [_fallback_summary(article) for article in articles]

    return [
        Summary(
            source=item["source"],
            title=item["title"],
            url=item["url"],
            summary=item["summary"],
            why_it_matters=item["why_it_matters"],
        )
        for item in decoded.get("items", [])
    ]


def _prompt(articles: list[Article]) -> str:
    lines = [
        "다음 기사들을 한국어 Slack 뉴스 다이제스트로 요약해줘.",
        "각 항목은 1문장 요약과 1문장 중요성으로 작성해.",
        "과장하지 말고 제목/본문에 있는 정보만 사용해.",
        "",
    ]
    for index, article in enumerate(articles, start=1):
        lines.extend(
            [
                f"[{index}]",
                f"source: {article.source}",
                f"title: {article.title}",
                f"url: {article.url}",
                f"content: {article.summary_text[:1200]}",
                "",
            ]
        )
    return "\n".join(lines)


def _extract_output_text(data: dict) -> str:
    chunks: list[str] = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                chunks.append(content.get("text", ""))
    return "\n".join(chunks).strip()


def _fallback_summary(article: Article) -> Summary:
    text = article.summary_text or article.title
    return Summary(
        source=article.source,
        title=article.title,
        url=article.url,
        summary=text[:180],
        why_it_matters="AI/개발 관련 키워드와 최근성을 기준으로 선별된 기사입니다.",
    )
