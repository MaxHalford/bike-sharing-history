# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "duckdb>=1.4",
# ]
# ///
"""Export one station or weather file's Git history to monthly Parquet files."""

import argparse
import datetime as dt
import gzip
import json
import pathlib
import subprocess
import tempfile
import types
from collections.abc import Callable, Iterator
from typing import Any, Self

import duckdb

UTC = dt.timezone.utc
TEMPORARY_GZIP_LEVEL = 1
encode_json = json.JSONEncoder(ensure_ascii=False, separators=(",", ":")).encode

CANONICAL_STATION_COLUMNS = {
    "city": "VARCHAR",
    "provider": "VARCHAR",
    "station_id": "VARCHAR",
    "name": "VARCHAR",
    "short_name": "VARCHAR",
    "external_id": "VARCHAR",
    "longitude": "DOUBLE",
    "latitude": "DOUBLE",
    "capacity": "BIGINT",
    "num_bikes_available": "BIGINT",
    "num_bikes_disabled": "BIGINT",
    "num_docks_available": "BIGINT",
    "num_docks_disabled": "BIGINT",
    "is_installed": "BOOLEAN",
    "is_renting": "BOOLEAN",
    "is_returning": "BOOLEAN",
    "status": "VARCHAR",
    "committed_at_utc": "TIMESTAMPTZ",
    "git_commit": "VARCHAR",
    "source_path": "VARCHAR",
}

CANONICAL_WEATHER_COLUMNS = {
    "city": "VARCHAR",
    "forecast_at_utc": "TIMESTAMPTZ",
    "temperature": "DOUBLE",
    "rain": "DOUBLE",
    "wind_speed": "DOUBLE",
    "committed_at_utc": "TIMESTAMPTZ",
    "git_commit": "VARCHAR",
    "source_path": "VARCHAR",
}


def git(*args: str, repo: pathlib.Path) -> str:
    """Run Git in *repo* and return its standard output."""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout


class GitObjectReader:
    """Read many ``<commit>:<path>`` blobs through one Git process."""

    def __init__(self, repo: pathlib.Path):
        self.process = subprocess.Popen(
            ["git", "-C", str(repo), "cat-file", "--batch"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    def __enter__(self) -> Self:
        return self

    def read(self, object_name: str) -> str:
        if self.process.stdin is None or self.process.stdout is None:
            raise RuntimeError("Git object reader is closed")
        self.process.stdin.write(f"{object_name}\n".encode())
        self.process.stdin.flush()
        header = self.process.stdout.readline().decode().rstrip("\n")
        if header.endswith(" missing"):
            raise FileNotFoundError(object_name)
        try:
            _, object_type, size = header.split()
        except ValueError as exc:
            raise RuntimeError(f"Unexpected git cat-file response: {header!r}") from exc
        if object_type != "blob":
            raise RuntimeError(f"Expected a blob for {object_name}, got {object_type}")
        content = self.process.stdout.read(int(size))
        separator = self.process.stdout.read(1)
        if separator != b"\n":
            raise RuntimeError(f"Malformed git cat-file response for {object_name}")
        return content.decode()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        if self.process.stdin is not None:
            self.process.stdin.close()
        return_code = self.process.wait()
        if self.process.stdout is not None:
            self.process.stdout.close()
        if return_code and exc_type is None:
            raise subprocess.CalledProcessError(return_code, self.process.args)


def iter_versions(
    repo: pathlib.Path,
    ref: str,
    source_path: str,
    since: str | None,
    until: str | None,
) -> Iterator[tuple[str, dt.datetime, set[str]]]:
    """Yield source or scrape-metadata changes in a UTC half-open interval."""
    since_utc = parse_time_boundary(since) if since else None
    until_utc = parse_time_boundary(until) if until else None
    metadata_path = scrape_metadata_path(source_path)
    args = [
        "log",
        ref,
        "--reverse",
        "--diff-filter=AMR",
        "--format=@@%H%x09%cI",
        "--name-only",
    ]
    if since:
        args.append(f"--since={since}")
    if until:
        args.append(f"--until={until}")
    args.extend(["--", source_path, metadata_path])

    current: tuple[str, dt.datetime] | None = None
    changed_paths: set[str] = set()
    for line in git(*args, repo=repo).splitlines():
        if line.startswith("@@"):
            if current is not None and timestamp_in_range(
                current[1], since_utc, until_utc
            ):
                yield *current, changed_paths
            commit, committed_at = line[2:].split("\t", maxsplit=1)
            current = (
                commit,
                dt.datetime.fromisoformat(committed_at).astimezone(UTC),
            )
            changed_paths = set()
        elif line:
            changed_paths.add(line)
    if current is not None and timestamp_in_range(current[1], since_utc, until_utc):
        yield *current, changed_paths


def parse_time_boundary(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def timestamp_in_range(
    timestamp: dt.datetime,
    since: dt.datetime | None,
    until: dt.datetime | None,
) -> bool:
    return (since is None or timestamp >= since) and (
        until is None or timestamp < until
    )


def scrape_metadata_path(source_path: str) -> str:
    parts = pathlib.PurePosixPath(source_path).parts
    if parts[:2] == ("data", "stations"):
        return f"data/scrapes/stations/{parts[2]}.json"
    if parts[:2] == ("data", "weather"):
        return f"data/scrapes/weather/{pathlib.PurePosixPath(parts[2]).stem}.json"
    raise ValueError(f"Unsupported source path: {source_path}")


def scrape_succeeded(metadata: dict[str, Any], source_path: str) -> bool:
    """Return whether metadata records a successful fetch for *source_path*."""
    parts = pathlib.PurePosixPath(source_path).parts
    if parts[:2] == ("data", "weather"):
        return metadata.get("status") == "ok"
    provider_slug = pathlib.PurePosixPath(parts[3]).stem
    return any(
        result.get("provider_slug") == provider_slug and result.get("status") == "ok"
        for result in metadata.get("systems", [])
    )


def first(properties: dict[str, Any], *names: str) -> Any:
    for name in names:
        value = properties.get(name)
        if value is not None:
            return value
    return None


def as_string(value: Any) -> str | None:
    return None if value is None else str(value)


def as_integer(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def as_boolean(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value in {0, "0", "false", "False"}:
        return False
    if value in {1, "1", "true", "True"}:
        return True
    return None


def forecast_timestamp_utc(snapshot: dict[str, Any], value: str) -> str:
    offset = int(snapshot.get("utc_offset_seconds", 0))
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone(dt.timedelta(seconds=offset)))
    return parsed.astimezone(UTC).isoformat()


def canonical_station_to_row(
    feature: dict[str, Any],
    *,
    commit: str,
    committed_at_utc: str,
    source_path: str,
    city: str,
    provider: str,
) -> dict[str, Any]:
    """Map GBFS and known provider variants to one nullable public schema."""
    properties = feature.get("properties", {})
    coordinates = feature.get("geometry", {}).get("coordinates", [None, None])
    return {
        "city": city,
        "provider": provider,
        "station_id": as_string(
            first(properties, "station_id", "number", "stationCode")
        ),
        "name": as_string(properties.get("name")),
        "short_name": as_string(first(properties, "short_name", "stationCode")),
        "external_id": as_string(properties.get("external_id")),
        "longitude": coordinates[0] if len(coordinates) > 0 else None,
        "latitude": coordinates[1] if len(coordinates) > 1 else None,
        "capacity": as_integer(first(properties, "capacity", "bike_stands")),
        "num_bikes_available": as_integer(
            first(
                properties,
                "num_bikes_available",
                "available_bikes",
                "numBikesAvailable",
            )
        ),
        "num_bikes_disabled": as_integer(properties.get("num_bikes_disabled")),
        "num_docks_available": as_integer(
            first(
                properties,
                "num_docks_available",
                "available_bike_stands",
                "numDocksAvailable",
            )
        ),
        "num_docks_disabled": as_integer(properties.get("num_docks_disabled")),
        "is_installed": as_boolean(properties.get("is_installed")),
        "is_renting": as_boolean(properties.get("is_renting")),
        "is_returning": as_boolean(properties.get("is_returning")),
        "status": as_string(properties.get("status")),
        "committed_at_utc": committed_at_utc,
        "git_commit": commit,
        "source_path": source_path,
    }


def canonical_weather_to_rows(
    snapshot: dict[str, Any],
    *,
    commit: str,
    committed_at: dt.datetime,
    source_path: str,
) -> Iterator[dict[str, Any]]:
    hourly = snapshot.get("hourly", {})
    parts = pathlib.PurePosixPath(source_path).parts
    forecast_times = hourly.get("time", [])
    for index, forecast_at in enumerate(forecast_times):

        def value(*names: str, row_index: int = index) -> Any:
            values = first(hourly, *names)
            return (
                values[row_index]
                if isinstance(values, list) and row_index < len(values)
                else None
            )

        yield {
            "city": pathlib.PurePosixPath(parts[2]).stem,
            "forecast_at_utc": forecast_timestamp_utc(snapshot, forecast_at),
            "temperature": value("temperature_2m", "temperature"),
            "rain": value("rain"),
            "wind_speed": value("wind_speed_10m", "windspeed_10m", "wind_speed"),
            "committed_at_utc": committed_at.isoformat(),
            "git_commit": commit,
            "source_path": source_path,
        }


def write_parquet(
    ndjson_file: pathlib.Path,
    parquet_file: pathlib.Path,
    columns: dict[str, str] | None = None,
) -> None:
    """Convert a compressed newline-delimited JSON file to Parquet."""
    source = str(ndjson_file).replace("'", "''")
    destination = str(parquet_file).replace("'", "''")
    projection = "*"
    if columns:
        projection = ",\n".join(
            f'CAST("{name}" AS {data_type}) AS "{name}"'
            for name, data_type in columns.items()
        )
    with duckdb.connect(":memory:") as con:
        con.execute("SET TimeZone='UTC'")
        con.execute(f"""
            COPY (
                SELECT {projection}
                FROM read_ndjson_auto(
                    '{source}',
                    union_by_name = true,
                    sample_size = -1,
                    maximum_object_size = 16777216
                )
            ) TO '{destination}' (
                FORMAT PARQUET,
                COMPRESSION ZSTD
            )
        """)


def write_empty_parquet(parquet_file: pathlib.Path, columns: dict[str, str]) -> None:
    """Write a zero-row Parquet file with an explicit canonical schema."""
    destination = str(parquet_file).replace("'", "''")
    projection = ",\n".join(
        f'CAST(NULL AS {data_type}) AS "{name}"' for name, data_type in columns.items()
    )
    with duckdb.connect(":memory:") as con:
        con.execute("SET TimeZone='UTC'")
        con.execute(f"""
            COPY (
                SELECT {projection}
                WHERE FALSE
            ) TO '{destination}' (
                FORMAT PARQUET,
                COMPRESSION ZSTD
            )
        """)


def export_history(
    *,
    repo: pathlib.Path,
    ref: str = "HEAD",
    source_path: str,
    output_dir: pathlib.Path,
    since: str | None,
    until: str | None,
    force: bool,
    on_parquet: Callable[[pathlib.Path, int, int], None] | None = None,
    delete_after_callback: bool = False,
    include_month: Callable[[int, int], bool] | None = None,
) -> None:
    """Export history, using one bounded-size temporary file per month."""
    if not (repo / ".git").exists() and not (
        (repo / "HEAD").is_file() and (repo / "objects").is_dir()
    ):
        raise ValueError(f"Not a Git repository: {repo}")

    existing = list(output_dir.glob("*/*.parquet")) if output_dir.exists() else []
    if existing and not force:
        raise FileExistsError(
            f"{output_dir} already contains Parquet files; use --force to replace them"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    current_month: tuple[int, int] | None = None
    skip_current_month = False
    compressed_json = None
    temporary_path: pathlib.Path | None = None
    rows_in_month = 0
    versions = 0
    source_parts = pathlib.PurePosixPath(source_path).parts
    canonical_city = pathlib.PurePosixPath(source_parts[2]).stem
    canonical_provider = (
        pathlib.PurePosixPath(source_parts[3]).stem
        if source_path.startswith("data/stations/")
        else ""
    )

    def finish_month() -> None:
        nonlocal compressed_json, temporary_path, rows_in_month
        if compressed_json is None or temporary_path is None or current_month is None:
            return
        compressed_json.close()
        year, month = current_month
        destination = output_dir / str(year) / f"{dt.date(year, month, 1):%b}.parquet"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and force:
            destination.unlink()
        columns = (
            CANONICAL_WEATHER_COLUMNS
            if source_path.startswith("data/weather/")
            else CANONICAL_STATION_COLUMNS
        )
        if rows_in_month == 0:
            write_empty_parquet(destination, columns)
        else:
            write_parquet(temporary_path, destination, columns)
        temporary_path.unlink()
        print(f"Wrote {rows_in_month:,} rows to {destination}")
        if on_parquet is not None:
            on_parquet(destination, year, month)
            if delete_after_callback:
                destination.unlink()
        compressed_json = None
        temporary_path = None
        rows_in_month = 0

    try:
        with GitObjectReader(repo) as objects:
            for commit, committed_at, changed_paths in iter_versions(
                repo, ref, source_path, since, until
            ):
                month = (committed_at.year, committed_at.month)
                if current_month != month:
                    finish_month()
                    current_month = month
                    skip_current_month = (
                        include_month is not None and not include_month(*month)
                    )
                if skip_current_month:
                    continue

                metadata_path = scrape_metadata_path(source_path)
                if metadata_path in changed_paths:
                    try:
                        scrape_metadata = json.loads(
                            objects.read(f"{commit}:{metadata_path}")
                        )
                    except (FileNotFoundError, json.JSONDecodeError):
                        scrape_metadata = None
                    if scrape_metadata is not None and not scrape_succeeded(
                        scrape_metadata, source_path
                    ):
                        continue

                try:
                    snapshot = json.loads(objects.read(f"{commit}:{source_path}"))
                except (FileNotFoundError, json.JSONDecodeError) as exc:
                    print(f"Skipped {commit}:{source_path} ({type(exc).__name__})")
                    continue

                if compressed_json is None:
                    with tempfile.NamedTemporaryFile(
                        prefix="bike-sharing-history-",
                        suffix=".ndjson.gz",
                        dir=output_dir,
                        delete=False,
                    ) as temporary:
                        temporary_path = pathlib.Path(temporary.name)
                    compressed_json = gzip.open(  # noqa: SIM115 - spans a whole month
                        temporary_path,
                        mode="wt",
                        encoding="utf-8",
                        compresslevel=TEMPORARY_GZIP_LEVEL,
                    )

                if source_path.startswith("data/weather/"):
                    rows = canonical_weather_to_rows(
                        snapshot,
                        commit=commit,
                        committed_at=committed_at,
                        source_path=source_path,
                    )
                else:
                    committed_at_utc = committed_at.isoformat()
                    rows = (
                        canonical_station_to_row(
                            feature,
                            commit=commit,
                            committed_at_utc=committed_at_utc,
                            source_path=source_path,
                            city=canonical_city,
                            provider=canonical_provider,
                        )
                        for feature in snapshot.get("features", [])
                    )

                for row in rows:
                    compressed_json.write(encode_json(row) + "\n")
                    rows_in_month += 1

                versions += 1
                if versions % 100 == 0:
                    print(
                        f"Processed {versions:,} file versions through "
                        f"{committed_at:%Y-%m-%d}"
                    )

            finish_month()
    finally:
        if compressed_json is not None:
            compressed_json.close()
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    print(f"Done: processed {versions:,} versions of {source_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source_path",
        help="Repository-relative GeoJSON path, for example data/stations/mexico-city/ecobici.geojson",
    )
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--since", help="Inclusive ISO-8601 UTC start time")
    parser.add_argument("--until", help="Exclusive ISO-8601 UTC end time")
    parser.add_argument(
        "--force", action="store_true", help="Replace existing output files"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    export_history(
        repo=args.repo.resolve(),
        ref=args.ref,
        source_path=args.source_path,
        output_dir=args.output_dir.resolve(),
        since=args.since,
        until=args.until,
        force=args.force,
    )
