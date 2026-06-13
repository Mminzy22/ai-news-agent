from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from .config import Source
from .models import Article


class _HTMLStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)

    def text(self) -> str:
        return " ".join(self.parts)


def fetch_articles(sources: list[Source], timeout: int = 20) -> list[Article]:
    articles: list[Article] = []
    for source in sources:
        try:
            with urllib.request.urlopen(source.url, timeout=timeout) as response:
                body = response.read()
            articles.extend(parse_feed(body, source))
        except (ET.ParseError, TimeoutError, urllib.error.URLError) as exc:
            print(f"warning: failed to fetch {source.name}: {exc}", file=sys.stderr)
    return articles


def parse_feed(body: bytes, source: Source) -> list[Article]:
    root = ET.fromstring(body)
    if root.tag.endswith("rss"):
        return _parse_rss(root, source)
    if root.tag.endswith("feed"):
        return _parse_atom(root, source)
    return []


def _parse_rss(root: ET.Element, source: Source) -> list[Article]:
    items: list[Article] = []
    for item in root.findall("./channel/item"):
        title = _text(item, "title")
        url = _text(item, "link")
        description = _clean_html(_text(item, "description"))
        published = _parse_date(_text(item, "pubDate"))
        if title and url:
            items.append(
                Article(
                    source=source.name,
                    title=unescape(title),
                    url=url,
                    published_at=published,
                    summary_text=description,
                    language=source.language,
                    score=source.weight,
                )
            )
    return items


def _parse_atom(root: ET.Element, source: Source) -> list[Article]:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items: list[Article] = []
    for entry in root.findall("a:entry", ns):
        title = _text_ns(entry, "a:title", ns)
        link_node = entry.find("a:link[@rel='alternate']", ns) or entry.find("a:link", ns)
        url = link_node.attrib.get("href", "") if link_node is not None else ""
        content = _clean_html(_text_ns(entry, "a:content", ns) or _text_ns(entry, "a:summary", ns))
        published = _parse_iso(_text_ns(entry, "a:published", ns) or _text_ns(entry, "a:updated", ns))
        if title and url:
            items.append(
                Article(
                    source=source.name,
                    title=unescape(title),
                    url=url,
                    published_at=published,
                    summary_text=content,
                    language=source.language,
                    score=source.weight,
                )
            )
    return items


def _text(node: ET.Element, child: str) -> str:
    found = node.find(child)
    return found.text.strip() if found is not None and found.text else ""


def _text_ns(node: ET.Element, child: str, ns: dict[str, str]) -> str:
    found = node.find(child, ns)
    return found.text.strip() if found is not None and found.text else ""


def _clean_html(value: str) -> str:
    stripper = _HTMLStripper()
    stripper.feed(unescape(value))
    return stripper.text()


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None
