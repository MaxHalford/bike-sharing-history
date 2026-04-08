import calendar
import collections
import csv
import datetime as dt
import json
import os
import pathlib
import re
import time

import dotenv
import duckdb
import git
from google.cloud import storage

dotenv.load_dotenv()

# Part 1: listing existing archives

# The first thing we do is list the blobs in the bucket. This way, we know which data has already
# been archived, and which data we need to archive.

service_account_info = json.loads(os.environ["GCP_SERVICE_ACCOUNT_JSON"], strict=False)
client = storage.Client.from_service_account_info(
    service_account_info, project="bike-sharing"
)

# Parse blob names like paris/smovengo/2023/Nov.parquet
existing_parquet_keys = {
    (
        "bike-sharing",
        *re.match(r"([\w\-]+)/([\w\-]+)/(\d+)/(\w+)\.parquet", blob.name).groups(),
    )
    for blob in client.get_bucket("bike-sharing-history").list_blobs()
} | {
    (
        "weather-forecast",
        *re.match(r"([\w\-]+)/(\d+)/(\w+)\.parquet", blob.name).groups(),
    )
    for blob in client.get_bucket("weather-forecast-history").list_blobs()
}
print(f"[1/3] Found {len(existing_parquet_keys):,d} existing parquet files in GCS")

# Deepen the shallow clone to only fetch the history we need.
# We find the latest archived month and fetch from one month before that,
# so we have enough history for deduplication without cloning the entire repo.
month_abbrevs = {m: i for i, m in enumerate(calendar.month_abbr) if m}
latest_archived = None
for key in existing_parquet_keys:
    try:
        year, month = key[-2], key[-1]
        month_num = month_abbrevs.get(month)
        if month_num and year.isdigit():
            d = dt.date(int(year), month_num, 1)
            if latest_archived is None or d > latest_archived:
                latest_archived = d
    except (ValueError, IndexError):
        continue

repo = git.Repo(".")
if latest_archived:
    # One month buffer before the latest archived month for deduplication state
    buffer_date = (latest_archived.replace(day=1) - dt.timedelta(days=1)).replace(day=1)
    # Use --deepen=N instead of --shallow-since, which breaks on shallow clones
    # in git 2.53+. The scrape job runs 4x/hour = 96 commits/day.
    days_needed = (dt.date.today() - buffer_date).days
    depth = days_needed * 96 + 500  # generous buffer
    print(f"[1/3] Deepening clone by {depth} commits (back to ~{buffer_date.isoformat()})...")
    repo.git.fetch(f"--deepen={depth}")
else:
    print("[1/3] No existing archives found, fetching full history...")
    repo.git.fetch("--unshallow")

print(f"[1/3] Done")

# Part 2: archiving the data into local CSV files


def jcdecaux_scrub(geojson):
    for station in geojson["features"]:
        yield {
            "station": station["properties"]["name"],
            "longitude": station["geometry"]["coordinates"][0],
            "latitude": station["geometry"]["coordinates"][1],
            "bikes": station["properties"]["available_bikes"],
            "stands": station["properties"]["available_bike_stands"],
        }


def gbfs_scrub(geojson):
    for station in geojson["features"]:
        yield {
            "station": station["properties"]["name"],
            "longitude": station["geometry"]["coordinates"][0],
            "latitude": station["geometry"]["coordinates"][1],
            "bikes": station["properties"]["num_bikes_available"],
            "stands": station["properties"]["num_docks_available"],
        }


# List the existing (city, provider) pairs
systems = [
    (city.stem, provider.stem)
    for city in (pathlib.Path("data") / "stations").iterdir()
    for provider in city.iterdir()
    if provider.stem not in {"lime"}
]

# We limit ourselves to the latest full month, because we don't want to archive partial months.
# We also start from buffer_date (if we have existing archives) to avoid re-processing the
# entire history — the existing_parquet_keys check would skip them anyway, but iterating
# through thousands of old commits is slow.
end_of_last_month = dt.datetime.now(dt.timezone.utc).replace(
    day=1, hour=23, minute=59, second=59
) - dt.timedelta(days=1)
commit_kwargs = {"reverse": True, "until": end_of_last_month}
if latest_archived:
    commit_kwargs["since"] = buffer_date.isoformat()
print(f"[2/3] Archiving commits {'since ' + buffer_date.isoformat() + ' ' if latest_archived else ''}up to {end_of_last_month.strftime('%Y-%m-%d')}")
weather_cities = {city for city, _ in systems}
print(f"[2/3] {len(systems)} city/provider pairs, {len(weather_cities)} cities for weather")
commits = repo.iter_commits("--all", **commit_kwargs)
archive_dir = pathlib.Path("archive")
t0 = time.monotonic()

# We keep track of the latest update for each station, so that we can skip updates which don't
# change anything. We also keep track of the number of skipped updates, so that we can record
# this information in the CSV file.
latest_update_by_station = collections.defaultdict()
skipped_updates_by_station = collections.defaultdict(int)
last_written_month_by_station = {}

# Track blob SHAs to skip JSON parsing when a file hasn't changed between commits.
# Reset at month boundaries so the first commit of a new month always writes.
prev_blob_shas = {}
prev_commit_month = None

# Keep file handles and writers open to avoid opening/closing per commit
open_files = {}
csv_writers = {}

STATION_FIELDS = ["station", "longitude", "latitude", "commit_at", "skipped_updates", "bikes", "stands"]
WEATHER_FIELDS = ["commit_at", "forecast_at", "temperature", "rain", "wind_speed"]


def get_writer(csv_file, fieldnames):
    if csv_file not in csv_writers:
        csv_file.parent.mkdir(parents=True, exist_ok=True)
        f = open(csv_file, "a")
        open_files[csv_file] = f
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if csv_file.stat().st_size == 0:
            writer.writeheader()
        csv_writers[csv_file] = writer
    return csv_writers[csv_file]


for i, commit in enumerate(commits):
    commit_at = commit.committed_datetime.astimezone(dt.timezone.utc)
    year = commit_at.strftime("%Y")
    month = commit_at.strftime("%h")

    # Reset blob SHA cache at month boundaries so the first commit of a new month
    # always processes all files (needed to start new CSV files).
    current_month = (year, month)
    if current_month != prev_commit_month:
        prev_blob_shas.clear()
        prev_commit_month = current_month

    if i % 1_000 == 0:
        elapsed = time.monotonic() - t0
        rate = i / elapsed if elapsed > 0 else 0
        print(f"[2/3] Commit {i:,d} ({commit_at.strftime('%Y-%m-%d')}) — {rate:.0f} commits/s, {len(csv_writers)} CSV files open")

    # Cache shared tree lookups for this commit
    try:
        data_tree = commit.tree / "data"
        stations_tree = data_tree / "stations"
    except KeyError:
        continue

    # This loop is responsible for archiving the bike station updates. The next loop will archive
    # the weather updates.
    city_trees = {}
    for city, provider in systems:
        # Skip if the data has already been stored
        if ("bike-sharing", city, provider, str(year), month) in existing_parquet_keys:
            continue

        # Cache city-level tree lookups within this commit
        if city not in city_trees:
            try:
                city_trees[city] = stations_tree / city
            except KeyError:
                city_trees[city] = None
        if city_trees[city] is None:
            continue

        try:
            blob = city_trees[city] / f"{provider}.geojson"
        except KeyError:
            continue

        # Skip JSON parsing if blob unchanged since last commit
        blob_key = (city, provider)
        if blob.hexsha == prev_blob_shas.get(blob_key):
            continue
        prev_blob_shas[blob_key] = blob.hexsha

        # The data has been scrapped and stored as is. This is where we normalize it to a single
        # format.
        scrub = {
            "jcdecaux": jcdecaux_scrub,
        }.get(provider, gbfs_scrub)

        csv_file = archive_dir / "stations" / city / provider / year / f"{month}.csv"
        writer = get_writer(csv_file, STATION_FIELDS)

        for update in scrub(geojson=json.load(blob.data_stream)):
            station_key = (city, provider, update["station"])

            # We don't write anything if the data hasn't changed
            if (
                (latest_update := latest_update_by_station.get(station_key))
                and latest_update["bikes"] == update["bikes"]
                and latest_update["stands"] == update["stands"]
            ):
                skipped_updates_by_station[station_key] += 1
                continue

            # Reset skip counter at month boundaries so we don't carry over
            # counts from the previous month into the new CSV file
            if last_written_month_by_station.get(station_key) != current_month:
                skipped_updates_by_station[station_key] = 0
                last_written_month_by_station[station_key] = current_month

            update["commit_at"] = commit_at.isoformat()
            update["skipped_updates"] = skipped_updates_by_station[station_key]
            writer.writerow(update)
            latest_update_by_station[station_key] = update
            skipped_updates_by_station[station_key] = 0

    # This loop is responsible for archiving the weather updates.
    try:
        weather_tree = data_tree / "weather"
    except KeyError:
        continue

    for city in weather_cities:
        # Skip if the data has already been stored
        if ("weather-forecast", city, str(year), month) in existing_parquet_keys:
            continue

        try:
            blob = weather_tree / f"{city}.json"
        except KeyError:
            continue

        # Skip JSON parsing if blob unchanged since last commit
        blob_key = ("w", city)
        if blob.hexsha == prev_blob_shas.get(blob_key):
            continue
        prev_blob_shas[blob_key] = blob.hexsha

        csv_file = archive_dir / "weather" / city / year / f"{month}.csv"
        writer = get_writer(csv_file, WEATHER_FIELDS)

        # There is one row per forecast time step to write
        try:
            forecast = json.load(blob.data_stream)
        except json.JSONDecodeError:
            print(f"Error decoding {blob}")
            continue
        for forecast_at, temperature, rain, wind_speed in zip(
            forecast["hourly"]["time"],
            forecast["hourly"]["temperature_2m"],
            forecast["hourly"]["rain"],
            forecast["hourly"]["windspeed_10m"],
        ):
            writer.writerow(
                {
                    "commit_at": commit_at.isoformat(),
                    "forecast_at": forecast_at,
                    "temperature": temperature,
                    "rain": rain,
                    "wind_speed": wind_speed,
                }
            )

# Close all open file handles
for f in open_files.values():
    f.close()

elapsed = time.monotonic() - t0
print(f"[2/3] Done — processed {i + 1:,d} commits in {elapsed:.0f}s, wrote {len(csv_writers)} CSV files")

# Part 3: uploading the CSV files to GCS after converting them to Parquet
print("[3/3] Converting to Parquet and uploading to GCS...")
n_uploaded = 0

for csv_file in archive_dir.rglob("stations/**/*.csv"):
    # Let's skip the files which are empty, ignoring the header
    with open(csv_file) as f:
        for i, _ in enumerate(f):
            if i > 0:
                break
        else:
            continue

    # Skip if the data has already been stored
    key = (
        "bike-sharing",
        *re.match(
            r"archive/stations/([\w\-]+)/([\w\-]+)/(\d+)/(\w+).csv", str(csv_file)
        ).groups(),
    )
    if key in existing_parquet_keys:
        print("Skipping", "/".join(key))
        continue

    parquet_file = csv_file.with_suffix(".parquet")
    duckdb.connect(":memory:").execute(f"""
    COPY (
        SELECT *
        FROM read_csv('{csv_file}', header=true, quote='"')
    )
    TO '{parquet_file}' (FORMAT 'PARQUET', CODEC 'ZSTD');
    """)

    bucket = client.get_bucket("bike-sharing-history")
    blob = bucket.blob(str(parquet_file.relative_to(archive_dir / "stations")))
    blob.upload_from_filename(str(parquet_file), timeout=60 * 10)
    n_uploaded += 1
    print(f"[3/3] Uploaded {blob.name}")

for csv_file in archive_dir.rglob("weather/**/*.csv"):
    parquet_file = csv_file.with_suffix(".parquet")

    # Skip if the data has already been stored
    key = (
        "weather-forecast",
        *re.match(r"archive/weather/([\w\-]+)/(\d+)/(\w+).csv", str(csv_file)).groups(),
    )
    if key in existing_parquet_keys:
        print("Skipping", "/".join(key))
        continue

    duckdb.connect(":memory:").execute(f"""
    COPY (
        SELECT *
        FROM read_csv('{csv_file}', header=true, quote='"')
    )
    TO '{parquet_file}' (FORMAT 'PARQUET', CODEC 'ZSTD');
    """)

    bucket = client.get_bucket("weather-forecast-history")
    blob = bucket.blob(str(parquet_file.relative_to(archive_dir / "weather")))
    blob.upload_from_filename(str(parquet_file), timeout=60 * 10)
    n_uploaded += 1
    print(f"[3/3] Uploaded {blob.name}")

print(f"[3/3] Done — uploaded {n_uploaded} parquet files")
