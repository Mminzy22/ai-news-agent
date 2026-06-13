from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import ROOT


ARCHIVE_DIR = ROOT / "뉴스 요약"


def save_digest(message: str, archive_dir: Path = ARCHIVE_DIR) -> Path:
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    path = archive_dir / f"{now:%Y-%m-%d}.md"
    archive_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(message + "\n", encoding="utf-8")
    return path
