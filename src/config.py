from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    type: str
    language: str
    weight: float = 1.0


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    slack_webhook_url: str
    openai_model: str
    max_articles: int
    lookback_hours: int
    dry_run: bool = False


def load_dotenv(path: Path = ROOT / ".env") -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_settings(dry_run: bool = False) -> Settings:
    load_dotenv()
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5"),
        max_articles=int(os.getenv("MAX_ARTICLES", "8")),
        lookback_hours=int(os.getenv("LOOKBACK_HOURS", "24")),
        dry_run=dry_run,
    )


def load_sources(path: Path = ROOT / "config" / "sources.yml") -> list[Source]:
    # Tiny YAML reader for the simple list shape in config/sources.yml.
    sources: list[Source] = []
    current: dict[str, str] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        stripped = raw_line.strip()
        if stripped == "sources:":
            continue
        if stripped.startswith("- "):
            if current:
                sources.append(_source_from_dict(current))
            current = {}
            stripped = stripped[2:]
        if ":" in stripped and current is not None:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip()

    if current:
        sources.append(_source_from_dict(current))
    return sources


def _source_from_dict(data: dict[str, str]) -> Source:
    return Source(
        name=data["name"],
        url=data["url"],
        type=data.get("type", "rss"),
        language=data.get("language", "en"),
        weight=float(data.get("weight", "1.0")),
    )
