# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "duckdb>=1.4",
#   "requests>=2.32",
# ]
# ///
"""Update README archive row counts from public Parquet footers in GCS."""

import argparse
import calendar
import dataclasses
import json
import pathlib
import urllib.parse
import urllib.request
from collections.abc import Iterator

import duckdb
import utils
from systems import systems

BUCKET = "bike-sharing-history"
START_MARKER = "<!-- archive-summary-start -->"
END_MARKER = "<!-- archive-summary-end -->"


@dataclasses.dataclass(frozen=True)
class Archive:
    city: str
    provider: str
    month: str
    row_count: int
    url: str


def list_objects(prefix: str) -> Iterator[dict]:
    page_token = None
    while True:
        query = {
            "maxResults": 1000,
            "fields": "nextPageToken,items(name)",
        }
        if prefix:
            query["prefix"] = f"{prefix}/"
        if page_token:
            query["pageToken"] = page_token
        url = (
            f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o?"
            + urllib.parse.urlencode(query)
        )
        with urllib.request.urlopen(url) as response:
            page = json.load(response)
        yield from page.get("items", [])
        page_token = page.get("nextPageToken")
        if not page_token:
            return


def read_row_counts(urls: list[str], batch_size: int = 128) -> dict[str, int]:
    """Read row counts from Parquet footers without downloading table data."""
    counts = {}
    with duckdb.connect(":memory:") as con:
        for start in range(0, len(urls), batch_size):
            batch = urls[start : start + batch_size]
            rows = con.execute(
                "SELECT file_name, num_rows FROM parquet_file_metadata(?)", [batch]
            ).fetchall()
            counts.update((name, int(row_count)) for name, row_count in rows)
    missing = set(urls) - counts.keys()
    if missing:
        raise ValueError(f"Could not read {len(missing):,} Parquet footer(s)")
    return counts


def read_archives(prefix: str) -> list[Archive]:
    path_prefix = f"{prefix}/" if prefix else ""
    objects = []
    for item in list_objects(prefix):
        name = item["name"]
        if prefix and not name.startswith(path_prefix):
            continue
        logical_name = name.removeprefix(path_prefix)
        parts = logical_name.split("/")
        if len(parts) != 4 or not parts[-1].endswith(".parquet"):
            continue
        city, provider, year, filename = parts
        month_name = filename.removesuffix(".parquet")
        try:
            month_number = list(calendar.month_abbr).index(month_name)
            month = f"{int(year):04d}-{month_number:02d}"
        except ValueError as exc:
            raise ValueError(f"Invalid archive path gs://{BUCKET}/{name}") from exc
        raw_url = (
            f"https://storage.googleapis.com/{BUCKET}/"
            f"{urllib.parse.quote(name, safe='/')}"
        )
        details_url = (
            "https://console.cloud.google.com/storage/browser/_details/"
            f"{BUCKET}/{urllib.parse.quote(name, safe='/')}"
        )
        objects.append((city, provider, month, raw_url, details_url))

    counts = read_row_counts([raw_url for *_, raw_url, _ in objects])
    return [
        Archive(
            city=city,
            provider=provider,
            month=month,
            row_count=counts[raw_url],
            url=details_url,
        )
        for city, provider, month, raw_url, details_url in objects
    ]


def system_names() -> dict[tuple[str, str], str]:
    return {
        (utils.slugify(system.city), utils.slugify(system.provider)): (
            f"{system.city} — {system.provider}"
        )
        for system in systems
    }


def humanize(slug: str) -> str:
    return slug.replace("-", " ").title()


def display_name(
    city: str,
    provider: str,
    current_names: dict[tuple[str, str], str],
) -> str:
    """Resolve spelling and capitalization through the current slug registry."""
    if current := current_names.get((city, provider)):
        return current

    city_names = {}
    provider_names = {}
    for (city_slug, provider_slug), name in current_names.items():
        city_name, provider_name = name.split(" — ", maxsplit=1)
        city_names.setdefault(city_slug, city_name)
        provider_names.setdefault(provider_slug, provider_name)
    return (
        f"{city_names.get(city, humanize(city))} — "
        f"{provider_names.get(provider, humanize(provider))}"
    )


def render_system_table(
    identities: list[tuple[str, str]],
    months: list[str],
    values: dict[tuple[str, str, str], Archive],
    names: dict[tuple[str, str], str],
) -> str:
    lines = [
        "| System | " + " | ".join(months) + " |",
        "|---|" + "---:|" * len(months),
    ]
    for city, provider in identities:
        label = display_name(city, provider, names)
        cells = []
        for month in months:
            archive = values.get((city, provider, month))
            cells.append(f"[{archive.row_count:,}]({archive.url})" if archive else "—")
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_table(archives: list[Archive]) -> str:
    months = sorted({archive.month for archive in archives}, reverse=True)
    values = {
        (archive.city, archive.provider, archive.month): archive for archive in archives
    }
    names = system_names()
    archived_identities = {(archive.city, archive.provider) for archive in archives}
    current_identities = sorted(names)
    historical_identities = sorted(archived_identities - names.keys())
    current = render_system_table(current_identities, months, values, names)
    historical = render_system_table(historical_identities, months, values, names)
    return (
        f"#### Current systems\n\n{current}\n\n#### Historical systems\n\n{historical}"
    )


def update_readme(readme: pathlib.Path, table: str) -> None:
    contents = readme.read_text()
    start = contents.find(START_MARKER)
    end = contents.find(END_MARKER)
    if start < 0 or end < 0 or end < start:
        raise ValueError("Archive summary markers are missing from the README")
    replacement = f"{START_MARKER}\n\n{table}\n\n"
    readme.write_text(contents[:start] + replacement + contents[end:])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", default="")
    parser.add_argument(
        "--readme", type=pathlib.Path, default=pathlib.Path("README.md")
    )
    args = parser.parse_args()

    prefix = args.prefix.strip("/")
    archives = read_archives(prefix)
    if not archives:
        raise ValueError(f"No archives found under prefix {prefix!r}")
    update_readme(args.readme, render_table(archives))
    print(
        f"Updated {args.readme} from {len(archives):,} station archives "
        f"under {prefix or 'canonical root'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
