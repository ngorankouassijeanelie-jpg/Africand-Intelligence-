import logging
from datetime import datetime

import feedparser

from app.modules.collectors.base import CollectedItem, Collector

logger = logging.getLogger(__name__)


class RssCollector(Collector):
    def __init__(self, feed_url: str, max_items: int = 30):
        self.feed_url = feed_url
        self.max_items = max_items

    def collect(self) -> list[CollectedItem]:
        items: list[CollectedItem] = []
        try:
            parsed = feedparser.parse(self.feed_url)
        except Exception:
            logger.exception("Echec de collecte RSS pour %s", self.feed_url)
            return items

        for entry in parsed.entries[: self.max_items]:
            published_at = None
            if getattr(entry, "published_parsed", None):
                published_at = datetime(*entry.published_parsed[:6])

            content = ""
            if hasattr(entry, "summary"):
                content = entry.summary
            elif hasattr(entry, "description"):
                content = entry.description

            items.append(
                CollectedItem(
                    title=getattr(entry, "title", ""),
                    content=content,
                    url=getattr(entry, "link", ""),
                    published_at=published_at,
                )
            )
        return items
