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
            station_metadata = json.loads(
                (root / "data/scrapes/stations/mexico-city.json").read_text()
            )
            self.assertEqual(
                {result["gbfs_system_id"] for result in station_metadata["systems"]},
                {system.gbfs_system_id for system in city_systems},
            )

    def test_station_only_scrape_skips_weather(self) -> None:
        with (
            mock.patch.object(scrape_city_branches.scrape_stations, "main") as stations,
            mock.patch.object(scrape_city_branches.scrape_weather, "main") as weather,
        ):
            scrape_city_branches.scrape_all(
                pathlib.Path("/tmp/scraped"), include_weather=False
            )

        stations.assert_called_once_with(data_root=pathlib.Path("/tmp/scraped"))
        weather.assert_not_called()


class PublishCityTest(unittest.TestCase):
    def test_city_tips_are_fetched_in_bounded_batches(self) -> None:
        cities = [f"city-{index:03d}" for index in range(105)]
        remote_heads = "\n".join(
            f"commit-{index:03d}\trefs/heads/city/city-{index:03d}"
            for index in range(105)
        )
        success = subprocess.CompletedProcess([], returncode=0, stdout="")

        with mock.patch.object(
            scrape_city_branches,
            "run",
            side_effect=[
                subprocess.CompletedProcess([], returncode=0, stdout=remote_heads),
                success,
                success,
                success,
            ],
        ) as run:
            scrape_city_branches.fetch_city_tips(
                pathlib.Path("/repo"), "origin", cities, batch_size=50
            )

        self.assertEqual(run.call_count, 4)
        fetched_refspecs = []
        for call in run.call_args_list[1:]:
            self.assertEqual(call.args[:4], ("git", "fetch", "--depth=1", "origin"))
            self.assertLessEqual(len(call.args[4:]), 50)
            self.assertEqual(call.kwargs, {"cwd": pathlib.Path("/repo"), "check": False})
            fetched_refspecs.extend(call.args[4:])
        self.assertEqual(
            fetched_refspecs,
            [
                f"+refs/heads/city/city-{index:03d}:"
                f"refs/remotes/origin/city/city-{index:03d}"
                for index in range(105)
            ],
        )

    def test_city_updates_are_pushed_in_bounded_atomic_batches(self) -> None:
        updates = {
            f"city-{index:03d}": f"commit-{index:03d}" for index in range(105)
        }
        success = subprocess.CompletedProcess([], returncode=0, stdout="")

        with mock.patch.object(
            scrape_city_branches, "run", return_value=success
        ) as run:
            scrape_city_branches.push_city_updates(
                pathlib.Path("/repo"), "origin", updates, batch_size=50
            )

        self.assertEqual(run.call_count, 3)
        pushed_refspecs = []
        for call in run.call_args_list:
            self.assertEqual(call.args[:4], ("git", "push", "--atomic", "origin"))
            self.assertLessEqual(len(call.args[4:]), 50)
            self.assertEqual(call.kwargs, {"cwd": pathlib.Path("/repo"), "check": False})
            pushed_refspecs.extend(call.args[4:])
        self.assertEqual(
            pushed_refspecs,
            [
                f"commit-{index:03d}:refs/heads/city/city-{index:03d}"
                for index in range(105)
            ],
        )

    def test_failed_batch_does_not_prevent_later_batches(self) -> None:
        failure = subprocess.CompletedProcess([], returncode=1, stdout="rejected")
        success = subprocess.CompletedProcess([], returncode=0, stdout="")

        with (
            mock.patch.object(
                scrape_city_branches,
                "run",
                side_effect=[failure, success],
            ) as run,
            self.assertRaisesRegex(RuntimeError, "Batch 1/2"),
        ):
            scrape_city_branches.push_city_updates(
                pathlib.Path("/repo"),
                "origin",
                {"a": "commit-a", "b": "commit-b"},
                attempts=1,
                batch_size=1,
            )

        self.assertEqual(run.call_count, 2)

    def test_push_batch_size_must_be_positive(self) -> None:
        with self.assertRaisesRegex(ValueError, "batch_size must be at least 1"):
            scrape_city_branches.push_city_updates(
                pathlib.Path("/repo"), "origin", {"a": "commit-a"}, batch_size=0
            )

    def test_push_attempts_must_be_positive(self) -> None:
        with self.assertRaisesRegex(ValueError, "attempts must be at least 1"):
            scrape_city_branches.push_city_updates(
                pathlib.Path("/repo"), "origin", {"a": "commit-a"}, attempts=0
            )

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

    def test_missing_city_branch_is_created_from_main(self) -> None:
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
            (seed / "README.md").write_text("main\n")
            git("add", "README.md", cwd=seed)
            git("commit", "-m", "seed main", cwd=seed)
            git("branch", "-M", "main", cwd=seed)
            git("remote", "add", "origin", str(remote), cwd=seed)
            git("push", "origin", "main", cwd=seed)

            git("clone", "--branch", "main", str(remote), str(runner), cwd=root)
            write_json(
                scraped / "data/stations/rosario/mibicitubici.geojson",
                {"fresh": True},
            )
            write_json(
                scraped / "data/scrapes/stations/rosario.json", {"status": "ok"}
            )

            scrape_city_branches.fetch_city_tips(runner, "origin", ["rosario"])
            git("config", "user.name", "Test", cwd=runner)
            git("config", "user.email", "test@example.com", cwd=runner)
            commit = scrape_city_branches.prepare_city(
                repo=runner,
                remote="origin",
                scraped_root=scraped,
                worktrees_root=worktrees,
                city_slug="rosario",
                timestamp="2026-09-10T12:00:00+00:00",
            )
            self.assertIsNotNone(commit)
            scrape_city_branches.push_city_updates(runner, "origin", {"rosario": commit})

            check = root / "check"
            git(
                "clone",
                "--single-branch",
                "--branch",
                "city/rosario",
                str(remote),
                str(check),
                cwd=root,
            )
            self.assertEqual(
                json.loads(
                    (check / "data/stations/rosario/mibicitubici.geojson").read_text()
                ),
                {"fresh": True},
            )


if __name__ == "__main__":
    unittest.main()
