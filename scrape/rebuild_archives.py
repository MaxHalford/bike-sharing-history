# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "duckdb>=1.4",
#   "google-cloud-storage>=3.0",
# ]
# ///
"""Build monthly Parquet archives from a city branch's Git history.

For bounded runner disk usage, each monthly file can be uploaded and removed
before the next month is built.
"""

import argparse
import calendar
import json
import os
import pathlib
import subprocess
from collections.abc import Sequence

import utils
from export_history import export_history
from google.cloud import storage

STATION_BUCKET = "bike-sharing-history"
WEATHER_BUCKET = "weather-forecast-history"


def git_paths(repo: pathlib.Path, ref: str) -> list[str]:
    output = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "log",
            ref,
            "--name-only",
            "--format=",
            "--",
            "data/stations",
            "data/weather",
        ],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout
    paths = set()
    for path in output.splitlines():
        parts = pathlib.PurePosixPath(path).parts
        is_station = (
            len(parts) == 4
            and parts[:2] == ("data", "stations")
            and parts[3].endswith(".geojson")
        )
        is_weather = (
            len(parts) == 3
            and parts[:2] == ("data", "weather")
            and parts[2].endswith(".json")
        )
        if is_station or is_weather:
            paths.add(path)
    return sorted(paths)


def local_directory(root: pathlib.Path, source_path: str) -> pathlib.Path:
    parts = pathlib.PurePosixPath(source_path).parts
    if parts[1] == "stations":
        return root / "stations" / parts[2] / pathlib.PurePosixPath(parts[3]).stem
    return root / "weather" / pathlib.PurePosixPath(parts[2]).stem


def object_name(source_path: str, year: int, month: int) -> tuple[str, str]:
    parts = pathlib.PurePosixPath(source_path).parts
    month_name = calendar.month_abbr[month]
    if parts[1] == "stations":
        city = utils.canonical_city_slug(parts[2])
        provider = pathlib.PurePosixPath(parts[3]).stem
        return STATION_BUCKET, f"{city}/{provider}/{year}/{month_name}.parquet"
    city = utils.canonical_city_slug(pathlib.PurePosixPath(parts[2]).stem)
    return WEATHER_BUCKET, f"{city}/{year}/{month_name}.parquet"


class Uploader:
    def __init__(self, force: bool):
        info = json.loads(os.environ["GCP_SERVICE_ACCOUNT_JSON"], strict=False)
        self.client = storage.Client.from_service_account_info(info)
        self.force = force
        self.source_path = ""

    def should_export(self, year: int, month: int) -> bool:
        bucket_name, name = object_name(self.source_path, year, month)
        exists = self.client.bucket(bucket_name).blob(name).exists()
        if exists and not self.force:
            print(f"Skipped existing gs://{bucket_name}/{name}")
            return False
        return True

    def upload(self, parquet_file: pathlib.Path, year: int, month: int) -> None:
        bucket_name, name = object_name(self.source_path, year, month)
        blob = self.client.bucket(bucket_name).blob(name)
        if blob.exists() and not self.force:
            print(f"Skipped existing gs://{bucket_name}/{name}")
            return
        blob.metadata = {"schema_version": "2", "source_path": self.source_path}
        blob.upload_from_filename(str(parquet_file), timeout=60 * 10)
        print(f"Uploaded gs://{bucket_name}/{name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--path", action="append", dest="paths")
    parser.add_argument("--since", help="Inclusive ISO-8601 UTC start time")
    parser.add_argument("--until", help="Exclusive ISO-8601 UTC end time")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument(
        "--delete-after-upload",
        action="store_true",
        help="Bound local disk use by deleting each successfully uploaded month",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    repo = args.repo.resolve()
    available_paths = git_paths(repo, args.ref)
    paths: Sequence[str] = args.paths or available_paths
    unknown = sorted(set(paths) - set(available_paths))
    if unknown:
        raise ValueError(f"Paths not found in {args.ref}: {', '.join(unknown)}")

    uploader = Uploader(args.force) if args.upload else None

    for index, source_path in enumerate(paths, start=1):
        print(f"[{index}/{len(paths)}] Rebuilding {source_path}")
        if uploader:
            uploader.source_path = source_path
        export_history(
            repo=repo,
            ref=args.ref,
            source_path=source_path,
            output_dir=local_directory(args.output_dir.resolve(), source_path),
            since=args.since,
            until=args.until,
            force=args.force,
            on_parquet=uploader.upload if uploader else None,
            delete_after_callback=args.delete_after_upload,
            include_month=uploader.should_export if uploader else None,
        )


if __name__ == "__main__":
    main()
