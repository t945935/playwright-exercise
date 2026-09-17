"""不連線外部網站的核心邏輯測試。

這些測試讓書中範例可以在沒有瀏覽器、網路或登入帳號的環境驗證。
"""

import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parents[2]
sys.path.extend([
    str(ROOT / "examples/03_data_queries"),
    str(ROOT / "examples/04_tracking"),
])

import ai_news_today  # noqa: E402
import happyebook_new_books  # noqa: E402
import stock_open_gainers  # noqa: E402
import tsmc_price_tracker  # noqa: E402


class AiNewsTests(unittest.TestCase):
    def test_parse_feed_filters_date_and_invalid_items(self):
        body = """<rss version='2.0'><channel>
          <item><title>AI 今日消息 - Example</title><link>https://example.com/a</link>
            <pubDate>Thu, 17 Sep 2026 01:00:00 GMT</pubDate><source>Example</source></item>
          <item><title>昨天消息</title><link>https://example.com/b</link>
            <pubDate>Wed, 16 Sep 2026 01:00:00 GMT</pubDate></item>
          <item><title>缺少時間</title><link>https://example.com/c</link></item>
        </channel></rss>""".encode()
        now = datetime(2026, 9, 17, 12, 0, tzinfo=ai_news_today.TAIPEI)
        records, invalid = ai_news_today.parse_feed(body, now.date(), now)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["title"], "AI 今日消息")
        self.assertEqual(invalid, 1)

    def test_deduplicate_keeps_newest_url(self):
        records = [
            {"title": "AI 報告", "source": "來源", "published_at": "2026-09-17T10:00:00+08:00", "url": "https://example.com/new"},
            {"title": " AI   報告 ", "source": "來源", "published_at": "2026-09-17T09:00:00+08:00", "url": "https://example.com/old"},
        ]
        result = ai_news_today.deduplicate(records)
        self.assertEqual([item["url"] for item in result], ["https://example.com/new"])


class TsmcTrackerTests(unittest.TestCase):
    def test_save_observation_marks_price_direction(self):
        connection = sqlite3.connect(":memory:")
        tsmc_price_tracker.init_db(connection)
        checked_at = "2026-09-17T13:30:00+08:00"
        first = tsmc_price_tracker.save_observation(connection, checked_at, tsmc_price_tracker.Decimal("100"), checked_at)
        second = tsmc_price_tracker.save_observation(connection, "2026-09-17T13:31:00+08:00", tsmc_price_tracker.Decimal("95"), checked_at)
        self.assertEqual(first["status"], "first")
        self.assertEqual(second["status"], "down")
        self.assertEqual(second["change"], "-5")
        connection.close()

    def test_parse_quote_rejects_non_today(self):
        now = datetime(2026, 9, 17, 13, 30, tzinfo=tsmc_price_tracker.TAIPEI)
        data = {"rtcode": "0000", "msgArray": [{
            "c": "2330", "ex": "tse", "d": "20260916", "t": "13:20:00",
            "z": "2400", "o": "2400", "v": "10",
        }]}
        with self.assertRaises(ValueError):
            tsmc_price_tracker.parse_quote(data, now)


class ApplicationFixtureTests(unittest.TestCase):
    def test_book_radar_finds_one_new_url(self):
        before = [{"title": "甲", "url": "https://happyebook.com/books/a.html"}]
        after = before + [{"title": "乙", "url": "https://happyebook.com/books/b.html"}]
        added, missing = happyebook_new_books.compare_books(before, after)
        self.assertEqual([book["title"] for book in added], ["乙"])
        self.assertEqual(missing, [])

    def test_stock_fixture_is_ranked_before_rounding(self):
        today = "20260917"
        records = [stock_open_gainers.opening_record({
            "c": code, "n": name, "ex": "tse", "d": today,
            "o": str(opening), "y": "100", "v": "1", "t": "09:00:01",
        }, today)[0] for code, name, opening in [("1001", "甲", 110), ("1002", "乙", 105), ("1003", "丙", 95)]]
        ranked = stock_open_gainers.rank_records(records, 2)
        self.assertEqual([row["code"] for row in ranked], ["1001", "1002"])


if __name__ == "__main__":
    unittest.main()
