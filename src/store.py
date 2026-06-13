from __future__ import annotations

from pathlib import Path
import json

from .config import ROOT


SEEN_PATH = ROOT / "data" / "seen.json"


def load_seen(path: Path = SEEN_PATH) -> set[str]:
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return set(data if isinstance(data, list) else [])


def save_seen(ids: set[str], path: Path = SEEN_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(ids), ensure_ascii=False, indent=2), encoding="utf-8")
