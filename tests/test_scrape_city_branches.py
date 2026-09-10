import contextlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scrape"))

import scrape_city_branches
import scrape_stations
import scrape_weather
import utils
from systems import systems


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def write_json(path: pathlib.Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")


class ScopedScrapeTest(unittest.TestCase):
    def test_station_and_weather_scrapes_can_target_one_city(self) -> None:
        city_slug = "mexico-city"
        city_systems = [
            system for system in systems if utils.slugify(system.city) == city_slug
        ]
        station_data = {"type": "FeatureCollection", "features": []}
        weather_data = {"hourly": {"time": []}}

        with (
            tempfile.TemporaryDirectory() as temporary,
            contextlib.ExitStack() as stack,
        ):
            root = pathlib.Path(temporary)
            for system in city_systems:
                stack.enter_context(
                    mock.patch.object(system, "scrape", return_value=station_data)
                )
            stack.enter_context(
                mock.patch.object(
                    scrape_weather, "fetch_weather", return_value=weather_data
                )
            )

            scrape_stations.main(city_slug=city_slug, data_root=root)
            scrape_weather.main(city_slug=city_slug, data_root=root)

            station_files = list((root / "data/stations").glob("*/*.geojson"))
            self.assertEqual({path.parent.name for path in station_files}, {city_slug})
            self.assertEqual(
                json.loads((root / "data/weather/mexico-city.json").read_text()),
                weather_data,
            )
            self.assertTrue((root / "data/scrapes/stations/mexico-city.json").exists())
            self.assertTrue((root / "data/scrapes/weather/mexico-city.json").exists())


class PublishCityTest(unittest.TestCase):
    def test_station_weather_and_metadata_are_committed_together(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            remote = root / "remote.git"
            seed = root / "seed"
            runner = root / "runner"
            scraped = root / "scraped"
            worktrees = root / "worktrees"

            remote.mkdir()
            git("init", "--bare", cwd=remote)
            seed.mkdir()
            git("init", cwd=seed)
            git("config", "user.name", "Test", cwd=seed)
            git("config", "user.email", "test@example.com", cwd=seed)
            write_json(
                seed / "data/stations/mexico-city/ecobici.geojson", {"old": True}
            )
            write_json(
                seed / "data/stations/mexico-city/obsolete.geojson",
                {"obsolete": True},
            )
            write_json(seed / "data/weather/mexico-city.json", {"old": True})
            git("add", "data", cwd=seed)
            git("commit", "-m", "seed", cwd=seed)
            git("branch", "-M", "city/mexico-city", cwd=seed)
            git("remote", "add", "origin", str(remote), cwd=seed)
            git("push", "origin", "city/mexico-city", cwd=seed)

            git(
                "clone",
                "--single-branch",
                "--branch",
                "city/mexico-city",
                str(remote),
                str(runner),
                cwd=root,
            )
            write_json(
                scraped / "data/stations/mexico-city/ecobici.geojson",
                {"fresh": True},
            )
            write_json(scraped / "data/weather/mexico-city.json", {"weather": "fresh"})
            write_json(
                scraped / "data/scrapes/stations/mexico-city.json", {"status": "ok"}
            )
            write_json(
                scraped / "data/scrapes/weather/mexico-city.json", {"status": "ok"}
            )

            scrape_city_branches.fetch_city_tips(runner, "origin", ["mexico-city"])
            git("config", "user.name", "Test", cwd=runner)
            git("config", "user.email", "test@example.com", cwd=runner)
            commit = scrape_city_branches.prepare_city(
                repo=runner,
                remote="origin",
                scraped_root=scraped,
                worktrees_root=worktrees,
                city_slug="mexico-city",
                timestamp="2026-09-09T12:00:00+00:00",
            )
            self.assertIsNotNone(commit)
            scrape_city_branches.push_city_updates(
                runner, "origin", {"mexico-city": commit}
            )

            check = root / "check"
            git(
                "clone",
                "--single-branch",
                "--branch",
                "city/mexico-city",
                str(remote),
                str(check),
                cwd=root,
            )
            self.assertEqual(
                json.loads(
                    (check / "data/stations/mexico-city/ecobici.geojson").read_text()
                ),
                {"fresh": True},
            )
            self.assertFalse(
                (check / "data/stations/mexico-city/obsolete.geojson").exists()
            )
            self.assertEqual(
                json.loads((check / "data/weather/mexico-city.json").read_text()),
                {"weather": "fresh"},
            )
            changed_paths = set(
                git("show", "--format=", "--name-only", cwd=check).splitlines()
            )
            self.assertEqual(
                changed_paths,
                {
                    "data/scrapes/stations/mexico-city.json",
                    "data/scrapes/weather/mexico-city.json",
                    "data/stations/mexico-city/ecobici.geojson",
                    "data/stations/mexico-city/obsolete.geojson",
                    "data/weather/mexico-city.json",
                },
            )
            self.assertEqual(
                git("show", "-s", "--format=%cI", cwd=check),
                "2026-09-09T12:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
