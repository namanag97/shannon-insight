from __future__ import annotations

import datetime as dt
import unittest
from unittest.mock import patch

import daily_research

NOW = dt.datetime(2026, 8, 11, 12, tzinfo=dt.timezone.utc)
SOURCE = {
    "id": "test-feed",
    "name": "Test Feed",
    "url": "https://example.com/feed.xml",
    "kind": "rss",
    "tier": 1,
    "beats": ["query-engines-and-databases"],
}


class DailyResearchTest(unittest.TestCase):
    def test_parses_recent_rss_item(self) -> None:
        feed = b"""<?xml version="1.0"?>
        <rss><channel><item>
          <title>New query engine benchmark</title>
          <link>https://example.com/post?utm_source=test</link>
          <pubDate>Tue, 11 Aug 2026 10:00:00 GMT</pubDate>
          <description>SQL throughput and latency results.</description>
        </item></channel></rss>"""
        with patch.object(daily_research, "fetch", return_value=feed):
            items = daily_research.parse_feed(
                SOURCE,
                NOW,
                NOW - dt.timedelta(hours=24),
                include_undated=False,
            )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "New query engine benchmark")
        self.assertGreaterEqual(items[0].score, 10)

    def test_excludes_old_items(self) -> None:
        feed = b"""<rss><channel><item>
          <title>Old database post</title><link>https://example.com/old</link>
          <pubDate>Tue, 4 Aug 2026 10:00:00 GMT</pubDate>
        </item></channel></rss>"""
        with patch.object(daily_research, "fetch", return_value=feed):
            items = daily_research.parse_feed(
                SOURCE,
                NOW,
                NOW - dt.timedelta(hours=24),
                include_undated=False,
            )
        self.assertEqual(items, [])

    def test_parses_atom_link_and_iso_date(self) -> None:
        feed = b"""<feed xmlns="http://www.w3.org/2005/Atom">
        <entry>
          <title>Warehouse engine 2.0</title>
          <link rel="alternate" href="https://example.com/v2" />
          <updated>2026-08-11T09:00:00Z</updated>
          <summary>New storage architecture and SQL optimizer.</summary>
        </entry></feed>"""
        with patch.object(daily_research, "fetch", return_value=feed):
            items = daily_research.parse_feed(
                SOURCE,
                NOW,
                NOW - dt.timedelta(hours=24),
                include_undated=False,
            )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].url, "https://example.com/v2")
        self.assertEqual(items[0].published, "2026-08-11T09:00:00+00:00")

    def test_strips_tracking_parameters(self) -> None:
        url = "https://Example.com/post/?utm_source=x&ref=home#fragment"
        self.assertEqual(
            daily_research.canonical_url(url),
            "https://example.com/post?ref=home",
        )

    def test_downranks_nightly_and_marketing_items(self) -> None:
        useful = daily_research.score_item(
            "Database engine benchmark",
            "New query execution architecture",
            1,
            NOW,
            NOW,
        )
        noisy = daily_research.score_item(
            "3.8.3.dev1 Nightly Development Release",
            "Join our summit keynote",
            1,
            NOW,
            NOW,
        )
        self.assertGreater(useful, noisy)
        self.assertGreater(
            useful,
            daily_research.score_item("v1.6.0rc3", "Release", 1, NOW, NOW),
        )
        self.assertGreater(
            useful,
            daily_research.score_item("providers-google/22.3.0", "Release", 1, NOW, NOW),
        )


if __name__ == "__main__":
    unittest.main()
