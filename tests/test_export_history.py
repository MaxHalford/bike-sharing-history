import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scrape"))

import export_history


class CanonicalStationSchemaTest(unittest.TestCase):
    def row(self, properties: dict, source_path: str) -> dict:
        return export_history.canonical_station_to_row(
            {
                "geometry": {"coordinates": [2.1, 48.8]},
                "properties": properties,
            },
            commit="a" * 40,
            committed_at_utc="2026-09-09T12:00:00+00:00",
            source_path=source_path,
            city=pathlib.PurePosixPath(source_path).parts[2],
            provider=pathlib.PurePosixPath(source_path).stem,
        )

    def test_gbfs_and_jcdecaux_have_the_identical_columns(self) -> None:
        gbfs = self.row(
            {
                "station_id": 42,
                "name": "GBFS station",
                "capacity": 20,
                "num_bikes_available": 3,
                "num_docks_available": 17,
                "last_reported": 1_789_000_000,
            },
            "data/stations/example/gbfs.geojson",
        )
        jcdecaux = self.row(
            {
                "number": 7,
                "name": "JCDecaux station",
                "bike_stands": 30,
                "available_bikes": 10,
                "available_bike_stands": 20,
                "last_update": 1_789_000_000_000,
            },
            "data/stations/example/jcdecaux.geojson",
        )

        expected = set(export_history.CANONICAL_STATION_COLUMNS)
        self.assertEqual(set(gbfs), expected)
        self.assertEqual(set(jcdecaux), expected)
        self.assertEqual(gbfs["station_id"], "42")
        self.assertEqual(jcdecaux["station_id"], "7")
        self.assertEqual(jcdecaux["capacity"], 30)
        self.assertEqual(jcdecaux["num_bikes_available"], 10)
        self.assertEqual(jcdecaux["num_docks_available"], 20)

    def test_only_git_observation_time_is_in_the_canonical_station_schema(self) -> None:
        row = self.row(
            {"station_id": "1", "name": "Station", "last_reported": 1_789_000_000},
            "data/stations/example/gbfs.geojson",
        )
        self.assertEqual(row["committed_at_utc"], "2026-09-09T12:00:00+00:00")
        self.assertNotIn("last_reported", row)
        self.assertNotIn("updated_at_utc", row)

    def test_until_is_an_exclusive_utc_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = pathlib.Path(temporary) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
            )
            source = repo / "data/stations/example/gbfs.geojson"
            source.parent.mkdir(parents=True)
            for timestamp in (
                "2026-01-31T23:59:00+00:00",
                "2026-02-01T00:00:00+00:00",
            ):
                source.write_text(
                    json.dumps(
                        {
                            "type": "FeatureCollection",
                            "features": [],
                            "timestamp": timestamp,
                        }
                    )
                    + "\n"
                )
                subprocess.run(["git", "add", "."], cwd=repo, check=True)
                subprocess.run(
                    ["git", "commit", "--allow-empty", "-m", timestamp],
                    cwd=repo,
                    check=True,
                    env={
                        **os.environ,
                        "GIT_AUTHOR_DATE": timestamp,
                        "GIT_COMMITTER_DATE": timestamp,
                    },
                )

            versions = list(
                export_history.iter_versions(
                    repo,
                    "HEAD",
                    "data/stations/example/gbfs.geojson",
                    None,
                    "2026-02-01",
                )
            )

        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0][1].isoformat(), "2026-01-31T23:59:00+00:00")

    def test_empty_month_still_has_the_canonical_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parquet_file = pathlib.Path(temporary) / "empty.parquet"
            export_history.write_empty_parquet(
                parquet_file, export_history.CANONICAL_STATION_COLUMNS
            )
            with export_history.duckdb.connect(":memory:") as con:
                columns = {
                    row[0]
                    for row in con.execute(
                        "DESCRIBE SELECT * FROM read_parquet(?)", [str(parquet_file)]
                    ).fetchall()
                }
                count = con.execute(
                    "SELECT count(*) FROM read_parquet(?)", [str(parquet_file)]
                ).fetchone()[0]
        self.assertEqual(columns, set(export_history.CANONICAL_STATION_COLUMNS))
        self.assertEqual(count, 0)

    def test_file_deletions_are_not_exported_as_observations(self) -> None:
        with mock.patch.object(export_history, "git", return_value="") as git:
            list(
                export_history.iter_versions(
                    pathlib.Path("."),
                    "HEAD",
                    "data/stations/example/gbfs.geojson",
                    None,
                    None,
                )
            )
        self.assertIn("--diff-filter=AMR", git.call_args.args)

    def test_successful_unchanged_scrapes_are_observations_but_failures_are_not(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = pathlib.Path(temporary) / "repo"
            output = pathlib.Path(temporary) / "output"
            source = repo / "data/stations/example/gbfs.geojson"
            metadata = repo / "data/scrapes/stations/example.json"
            source.parent.mkdir(parents=True)
            metadata.parent.mkdir(parents=True)
            subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo,
                check=True,
            )
            source_contents = json.dumps(
                {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "geometry": {"coordinates": [1.0, 2.0]},
                            "properties": {
                                "station_id": "1",
                                "name": "Station",
                                "num_bikes_available": 3,
                                "num_docks_available": 4,
                            },
                        }
                    ],
                }
            )
            source.write_text(source_contents)

            def commit(status: str, timestamp: str) -> None:
                metadata.write_text(
                    json.dumps(
                        {
                            "finished_at": timestamp,
                            "systems": [{"provider_slug": "gbfs", "status": status}],
                        }
                    )
                )
                subprocess.run(["git", "add", "."], cwd=repo, check=True)
                subprocess.run(
                    ["git", "commit", "-m", f"{status} {timestamp}"],
                    cwd=repo,
                    check=True,
                    capture_output=True,
                    env={
                        **os.environ,
                        "GIT_AUTHOR_DATE": timestamp,
                        "GIT_COMMITTER_DATE": timestamp,
                    },
                )

            commit("ok", "2026-01-01T00:00:00+00:00")
            source.write_text("invalid JSON")
            commit("ok", "2026-01-01T00:05:00+00:00")
            source.write_text(source_contents)
            commit("ok", "2026-01-01T00:15:00+00:00")
            commit("error", "2026-01-01T00:30:00+00:00")
            commit("error", "2026-02-01T00:00:00+00:00")
            commit("ok", "2026-03-01T00:00:00+00:00")
            uploaded = []
            export_history.export_history(
                repo=repo,
                source_path="data/stations/example/gbfs.geojson",
                output_dir=output,
                since=None,
                until=None,
                force=False,
                on_parquet=lambda path, year, month: uploaded.append(
                    (path, year, month)
                ),
            )
            parquet = output / "2026/Jan.parquet"
            with export_history.duckdb.connect(":memory:") as con:
                row_count, observations = con.execute(
                    """
                    SELECT count(*), count(DISTINCT committed_at_utc)
                    FROM read_parquet(?)
                    """,
                    [str(parquet)],
                ).fetchone()
                march_rows = con.execute(
                    "SELECT count(*) FROM read_parquet(?)",
                    [str(output / "2026/Mar.parquet")],
                ).fetchone()[0]
        self.assertEqual((row_count, observations), (2, 2))
        self.assertEqual(uploaded[0][1:], (2026, 1))
        self.assertEqual(march_rows, 1)
        self.assertFalse((output / "2026/Feb.parquet").exists())


class CanonicalWeatherSchemaTest(unittest.TestCase):
    def test_forecast_times_are_normalized_to_utc(self) -> None:
        rows = list(
            export_history.canonical_weather_to_rows(
                {
                    "utc_offset_seconds": 7200,
                    "hourly": {
                        "time": ["2026-09-09T14:00"],
                        "temperature_2m": [21.5],
                        "rain": [0.0],
                        "windspeed_10m": [5.0],
                    },
                },
                commit="b" * 40,
                committed_at=dt.datetime(2026, 9, 9, 12, 5, tzinfo=dt.timezone.utc),
                source_path="data/weather/example.json",
            )
        )
        self.assertEqual(set(rows[0]), set(export_history.CANONICAL_WEATHER_COLUMNS))
        self.assertEqual(rows[0]["forecast_at_utc"], "2026-09-09T12:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
