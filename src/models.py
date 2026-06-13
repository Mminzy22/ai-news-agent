from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Article:
    source: str
    title: str
    url: str
    published_at: datetime | None
    summary_text: str
    language: str
    score: float = 0.0


@dataclass(frozen=True)
class Summary:
    source: str
    title: str
    url: str
    summary: str
    why_it_matters: str
