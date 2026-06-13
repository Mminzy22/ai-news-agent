from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
import json
import urllib.request

from .models import Summary


def format_message(items: list[Summary]) -> str:
    today = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")
    if not items:
        return f"*오늘의 AI/개발 뉴스* ({today})\n최근 기준에 맞는 새 기사가 없습니다."

    lines = [f"*오늘의 AI/개발 뉴스* ({today})", ""]
    for index, item in enumerate(items, start=1):
        lines.extend(
            [
                f"*{index}. <{item.url}|{item.title}>*",
                f"- 출처: {item.source}",
                f"- 요약: {item.summary}",
                f"- 의미: {item.why_it_matters}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def send_message(webhook_url: str, text: str) -> None:
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL is required")

    request = urllib.request.Request(
        webhook_url,
        data=json.dumps({"text": text}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status >= 300:
            raise RuntimeError(f"Slack webhook failed with status {response.status}")
