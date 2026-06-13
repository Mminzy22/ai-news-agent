from __future__ import annotations

import argparse

from .config import get_settings, load_sources
from .fetchers import fetch_articles
from .ranker import article_id, select_articles
from .slack import format_message, send_message
from .store import load_seen, save_seen
from .summarizer import summarize_articles


def main() -> None:
    parser = argparse.ArgumentParser(description="Send an AI/developer news digest to Slack.")
    parser.add_argument("--dry-run", action="store_true", help="Print the Slack message without sending it.")
    parser.add_argument("--include-seen", action="store_true", help="Include articles already sent before.")
    args = parser.parse_args()

    settings = get_settings(dry_run=args.dry_run)
    sources = load_sources()
    articles = fetch_articles(sources)
    selected = select_articles(articles, settings.max_articles, settings.lookback_hours)

    seen = load_seen()
    if not args.include_seen:
        selected = [article for article in selected if article_id(article) not in seen]

    summaries = summarize_articles(selected, settings.openai_api_key, settings.openai_model)
    message = format_message(summaries)

    if settings.dry_run:
        print(message)
        return

    send_message(settings.slack_webhook_url, message)
    seen.update(article_id(article) for article in selected)
    save_seen(seen)


if __name__ == "__main__":
    main()
