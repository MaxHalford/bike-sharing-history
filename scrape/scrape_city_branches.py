"""Scrape every current city and publish one commit to each city branch.

This script is intended to run from a shallow checkout of ``main``. It fetches
only the current tip of every ``city/<slug>`` branch, collects all station and
weather feeds into a temporary directory, then commits both datasets and their
request metadata together on the corresponding city branch.
"""

import argparse
import concurrent.futures
import datetime as dt
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import time

import scrape_stations
import scrape_weather
import utils
from systems import systems


def run(
    *args: str,
    cwd: pathlib.Path,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=cwd,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )


def current_city_slugs() -> list[str]:
    return sorted({utils.slugify(system.city) for system in systems})


def expected_station_files(city_slug: str) -> set[str]:
    return {
        f"{utils.slugify(system.provider)}.geojson"
        for system in systems
        if utils.slugify(system.city) == city_slug
    }


def fetch_city_tips(repo: pathlib.Path, remote: str, cities: list[str]) -> None:
    refspecs = [
        f"+refs/heads/city/{city}:refs/remotes/{remote}/city/{city}" for city in cities
    ]
    result = run(
        "git",
        "fetch",
        "--depth=1",
        remote,
        *refspecs,
        cwd=repo,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"Could not fetch all city branches:\n{result.stdout}")

    missing = [
        city
        for city in cities
        if run(
            "git",
            "rev-parse",
            "--verify",
            f"refs/remotes/{remote}/city/{city}",
            cwd=repo,
            check=False,
        ).returncode
    ]
    if missing:
        raise RuntimeError(f"Missing city branches: {', '.join(missing)}")


def scrape_all(data_root: pathlib.Path) -> None:
    # The station and weather collectors have their own bounded thread pools.
    # Running the two collectors together reduces wall time without creating a
    # thread per city.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(scrape_stations.main, data_root=data_root),
            executor.submit(scrape_weather.main, data_root=data_root),
        ]
        for future in futures:
            future.result()


def copy_if_present(source: pathlib.Path, target: pathlib.Path) -> None:
    if source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def city_observed_at(scraped_root: pathlib.Path, city_slug: str) -> str:
    """Return the latest request completion time recorded for one city."""
    finished_at = []
    stations_file = scraped_root / "data/scrapes/stations" / f"{city_slug}.json"
    weather_file = scraped_root / "data/scrapes/weather" / f"{city_slug}.json"
    if stations_file.exists():
        station_metadata = json.loads(stations_file.read_text())
        finished_at.extend(
            result["finished_at"]
            for result in station_metadata.get("systems", [])
            if result.get("finished_at")
        )
    if weather_file.exists():
        weather_metadata = json.loads(weather_file.read_text())
        if weather_metadata.get("finished_at"):
            finished_at.append(weather_metadata["finished_at"])
    return (
        max(finished_at)
        if finished_at
        else dt.datetime.now(dt.timezone.utc).isoformat()
    )


def sync_city_data(
    *,
    scraped_root: pathlib.Path,
    worktree: pathlib.Path,
    city_slug: str,
) -> None:
    source_stations = scraped_root / "data/stations" / city_slug
    target_stations = worktree / "data/stations" / city_slug
    target_stations.mkdir(parents=True, exist_ok=True)

    expected = expected_station_files(city_slug)
    for old_file in target_stations.glob("*.geojson"):
        if old_file.name not in expected:
            old_file.unlink()
    if source_stations.exists():
        for source_file in source_stations.glob("*.geojson"):
            shutil.copy2(source_file, target_stations / source_file.name)

    relative_files = [
        pathlib.Path("data/weather") / f"{city_slug}.json",
        pathlib.Path("data/scrapes/stations") / f"{city_slug}.json",
        pathlib.Path("data/scrapes/weather") / f"{city_slug}.json",
    ]
    for relative_file in relative_files:
        copy_if_present(scraped_root / relative_file, worktree / relative_file)


def prepare_city(
    *,
    repo: pathlib.Path,
    remote: str,
    scraped_root: pathlib.Path,
    worktrees_root: pathlib.Path,
    city_slug: str,
    timestamp: str,
) -> str | None:
    worktree = worktrees_root / city_slug
    branch = f"city/{city_slug}"
    run(
        "git",
        "worktree",
        "add",
        "--detach",
        str(worktree),
        f"refs/remotes/{remote}/{branch}",
        cwd=repo,
    )
    try:
        sync_city_data(
            scraped_root=scraped_root,
            worktree=worktree,
            city_slug=city_slug,
        )
        paths = [
            f"data/stations/{city_slug}",
            f"data/weather/{city_slug}.json",
            f"data/scrapes/stations/{city_slug}.json",
            f"data/scrapes/weather/{city_slug}.json",
        ]
        run("git", "add", "--all", "--", *paths, cwd=worktree)
        unchanged = (
            run(
                "git", "diff", "--cached", "--quiet", cwd=worktree, check=False
            ).returncode
            == 0
        )
        if unchanged:
            return None
        run(
            "git",
            "commit",
            "-m",
            f"Latest {city_slug} data: {timestamp}",
            cwd=worktree,
            env={
                **os.environ,
                "GIT_AUTHOR_DATE": timestamp,
                "GIT_COMMITTER_DATE": timestamp,
            },
        )
        return run("git", "rev-parse", "HEAD", cwd=worktree).stdout.strip()
    finally:
        run(
            "git",
            "worktree",
            "remove",
            "--force",
            str(worktree),
            cwd=repo,
            check=False,
        )


def push_city_updates(
    repo: pathlib.Path,
    remote: str,
    updates: dict[str, str],
    attempts: int = 5,
) -> None:
    refspecs = [
        f"{commit}:refs/heads/city/{city}" for city, commit in sorted(updates.items())
    ]
    for attempt in range(1, attempts + 1):
        result = run(
            "git",
            "push",
            "--atomic",
            remote,
            *refspecs,
            cwd=repo,
            check=False,
        )
        if result.returncode == 0:
            return
        if attempt == attempts:
            raise RuntimeError(f"Could not publish city branches:\n{result.stdout}")
        delay = 5 * 2 ** (attempt - 1)
        print(result.stdout.rstrip())
        print(f"Atomic push failed; retrying in {delay} seconds ({attempt}/{attempts})")
        time.sleep(delay)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--remote", default="origin")
    parser.add_argument(
        "--city-slug",
        action="append",
        help="Publish only this city; repeat as needed (default: every current city)",
    )
    parser.add_argument(
        "--list-cities",
        action="store_true",
        help="Print the selected city slugs as JSON and exit",
    )
    args = parser.parse_args()

    repo = args.repo.resolve()
    requested = args.city_slug or current_city_slugs()
    known = set(current_city_slugs())
    unknown = sorted(set(requested) - known)
    if unknown:
        raise ValueError(f"Unknown city slugs: {', '.join(unknown)}")
    cities = sorted(set(requested))
    if args.list_cities:
        print(json.dumps(cities))
        return 0

    fetch_city_tips(repo, args.remote, cities)
    run("git", "config", "user.name", "Automated", cwd=repo)
    run(
        "git",
        "config",
        "user.email",
        "actions@users.noreply.github.com",
        cwd=repo,
    )

    failures = []
    updates = {}
    with tempfile.TemporaryDirectory(prefix="bike-sharing-scrape-") as temporary:
        temporary_root = pathlib.Path(temporary)
        scraped_root = temporary_root / "scraped"
        worktrees_root = temporary_root / "worktrees"
        scrape_all(scraped_root)

        for city in cities:
            try:
                commit = prepare_city(
                    repo=repo,
                    remote=args.remote,
                    scraped_root=scraped_root,
                    worktrees_root=worktrees_root,
                    city_slug=city,
                    timestamp=city_observed_at(scraped_root, city),
                )
                if commit:
                    updates[city] = commit
                    print(f"{city}: prepared")
                else:
                    print(f"{city}: unchanged")
            except Exception as exc:  # noqa: BLE001 - continue publishing other cities
                failures.append(city)
                print(f"{city}: failed ({type(exc).__name__}: {exc})")

    if failures:
        print(f"Failed cities: {', '.join(failures)}")
        return 1
    if updates:
        push_city_updates(repo, args.remote, updates)
        for city in updates:
            print(f"{city}: pushed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
