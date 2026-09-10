import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scrape"))

import rebuild_archives
import update_archive_summary


class ArchivePathsTest(unittest.TestCase):
    def test_station_and_weather_use_canonical_bucket_paths(self) -> None:
        self.assertEqual(
            rebuild_archives.object_name(
                "data/stations/mexico-city/ecobici.geojson", 2025, 10
            ),
            ("bike-sharing-history", "mexico-city/ecobici/2025/Oct.parquet"),
        )
        self.assertEqual(
            rebuild_archives.object_name("data/weather/mexico-city.json", 2025, 10),
            ("weather-forecast-history", "mexico-city/2025/Oct.parquet"),
        )

    def test_historical_city_names_use_current_bucket_paths(self) -> None:
        self.assertEqual(
            rebuild_archives.object_name(
                "data/stations/bruxelles/jcdecaux.geojson", 2023, 8
            ),
            ("bike-sharing-history", "brussels/jcdecaux/2023/Aug.parquet"),
        )
        self.assertEqual(
            rebuild_archives.object_name("data/weather/seville.json", 2023, 7),
            ("weather-forecast-history", "sevilla/2023/Jul.parquet"),
        )


class ArchiveSummaryTest(unittest.TestCase):
    def test_current_system_without_an_archive_is_still_listed(self) -> None:
        archive = update_archive_summary.Archive(
            city="old-city",
            provider="old-provider",
            month="2026-08",
            row_count=123,
            url="https://example.test/archive.parquet",
        )
        with mock.patch.object(
            update_archive_summary,
            "system_names",
            return_value={("new-city", "new-provider"): "New City — New Provider"},
        ):
            table = update_archive_summary.render_table([archive])

        self.assertIn("#### Current systems", table)
        self.assertIn("#### Historical systems", table)
        self.assertEqual(table.count("| System | 2026-08 |"), 2)
        self.assertIn("| New City — New Provider | — |", table)
        self.assertIn("| Old City — Old Provider |", table)
        self.assertIn("[123](https://example.test/archive.parquet)", table)

    def test_historical_names_reuse_current_slug_spelling(self) -> None:
        names = {("creteil", "jcdecaux"): "Créteil — JCDecaux"}

        self.assertEqual(
            update_archive_summary.display_name("creteil", "jcdecaux-old", names),
            "Créteil — Jcdecaux Old",
        )
        self.assertEqual(
            update_archive_summary.display_name("old-city", "jcdecaux", names),
            "Old City — JCDecaux",
        )


if __name__ == "__main__":
    unittest.main()
