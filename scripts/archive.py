import collections
import csv
import datetime as dt
import json
import os
import pathlib
import re

import dotenv
import duckdb
import git
from google.cloud import storage

dotenv.load_dotenv()

# Part 1: listing existing archives

# The first thing we do is list the blobs in the bucket. This way, we know which data has already
# been archived, and which data we need to archive.

service_account_info = json.loads(os.environ['GCP_SERVICE_ACCOUNT_JSON'], strict=False)
client = storage.Client.from_service_account_info(
    service_account_info,
    project='bike-sharing'
)

# Parse blob names like paris/smovengo/2023/Nov.parquet
existing_parquet_keys = {
    ('bike-sharing', *re.match(r'([\w\-]+)/([\w\-]+)/(\d+)/(\w+)\.parquet', blob.name).groups())
    for blob in client.get_bucket('bike-sharing-history').list_blobs()
} | {
    ('weather-forecast', *re.match(r'([\w\-]+)/(\d+)/(\w+)\.parquet', blob.name).groups())
    for blob in client.get_bucket('weather-forecast-history').list_blobs()
}
print(f'{len(existing_parquet_keys):,d} existing parquet files')

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
    for city in (pathlib.Path('data') / 'stations').iterdir()
    for provider in city.iterdir()
    if provider.stem not in {
        "lime"
    }
]

# We're going to loop over all the commits since the start of time. It's ok to do this, because
# most commits will be skipped. Indeed, we can skip all commits which pertain to a month which
# has already been archived.
# We do however limit ourselves to the latest full month, because we don't want to archive partial
# months.
end_of_last_month = (
    dt.datetime.now(dt.timezone.utc).replace(day=1, hour=23, minute=59, second=59) -
    dt.timedelta(days=1)
)
commits = (
    git.Repo('.').iter_commits(
        '--all',
        reverse=True,
        until=end_of_last_month
    )
)
archive_dir = pathlib.Path('archive')

# We keep track of the latest update for each station, so that we can skip updates which don't
# change anything. We also keep track of the number of skipped updates, so that we can record
# this information in the CSV file.
latest_update_by_station = collections.defaultdict()
skipped_updates_by_station = collections.defaultdict(int)

for i, commit in enumerate(commits):
    commit_at = commit.committed_datetime.astimezone(dt.timezone.utc)
    year = commit_at.strftime("%Y")
    month = commit_at.strftime("%h")

    if i % 1_000 == 0:
        print(f"Processing commit {i} ({commit_at.isoformat()})")

    # This loop is responsible for archiving the bike station updates. The next loop will archive
    # the weather updates.
    for city, provider in systems:

        # Skip if the data has already been stored
        if ('bike-sharing', city, provider, str(year), month) in existing_parquet_keys:
            continue

        try:
            blob = commit.tree / 'data' / 'stations' / city / f'{provider}.geojson'
        except KeyError:
            continue

        # The data has been scrapped and stored as is. This is where we normalize it to a single
        # format.
        scrub = {
            'jcdecaux': jcdecaux_scrub,
        }.get(provider, gbfs_scrub)

        # We store the data in a CSV file per month
        csv_file = archive_dir / 'stations' / city / provider / year / f"{month}.csv"
        csv_file.parent.mkdir(parents=True, exist_ok=True)

        with open(csv_file, "a") as f:
            writer = csv.DictWriter(f, fieldnames=[
                'station',
                'longitude',
                'latitude',
                'commit_at',
                'skipped_updates',
                'bikes',
                'stands',
            ])

            # Write the header if the file is empty
            if csv_file.stat().st_size == 0:
                writer.writeheader()

            for update in scrub(geojson=json.load(blob.data_stream)):
                station_key = (city, provider, update['station'])

                # We don't write anything if the data hasn't changed
                if (
                    (latest_update := latest_update_by_station.get(station_key))
                    and latest_update["bikes"] == update["bikes"]
                    and latest_update["stands"] == update["stands"]
                ):
                    skipped_updates_by_station[key] += 1
                    continue

                update['commit_at'] = commit_at.isoformat()
                update['skipped_updates'] = skipped_updates_by_station[station_key]
                writer.writerow(update)
                latest_update_by_station[station_key] = update
                skipped_updates_by_station[station_key] = 0

    # This loop is responsible for archiving the weather updates.
    for city in {city for city, _ in systems}:

        # Skip if the data has already been stored
        if ('weather-forecast', city, str(year), month) in existing_parquet_keys:
            continue

        try:
            blob = commit.tree / 'data' / 'weather' / f'{city}.json'
        except KeyError:
            continue

        # We store the data in a CSV file per month
        csv_file = archive_dir / 'weather' / city / year / f"{month}.csv"
        csv_file.parent.mkdir(parents=True, exist_ok=True)

        with open(csv_file, "a") as f:
            writer = csv.DictWriter(f, fieldnames=[
                'commit_at',
                'forecast_at',
                'temperature',
                'rain',
                'wind_speed'
            ])

            # Write the header if the file is empty
            if csv_file.stat().st_size == 0:
                writer.writeheader()

            # There is one row per forecast time step to write
            forecast = json.load(blob.data_stream)
            for forecast_at, temperature, rain, wind_speed in zip(
                forecast['hourly']['time'],
                forecast['hourly']['temperature_2m'],
                forecast['hourly']['rain'],
                forecast['hourly']['windspeed_10m'],
            ):
                writer.writerow({
                    'commit_at': commit_at.isoformat(),
                    'forecast_at': forecast_at,
                    'temperature': temperature,
                    'rain': rain,
                    'wind_speed': wind_speed,
                })

# Part 3: uploading the CSV files to GCS after converting them to Parquet

for csv_file in archive_dir.rglob('stations/**/*.csv'):
    parquet_file = csv_file.with_suffix('.parquet')

    # Skip if the data has already been stored
    key = ('bike-sharing', *re.match(r'archive/stations/([\w\-]+)/([\w\-]+)/(\d+)/(\w+).csv', str(csv_file)).groups())
    if key in existing_parquet_keys:
        print('Skipping', '/'.join(key))
        continue

    duckdb.connect(':memory:').execute(f"""
    COPY (
        SELECT *
        FROM read_csv('{csv_file}', AUTO_DETECT=TRUE)
    )
    TO '{parquet_file}' (FORMAT 'PARQUET', CODEC 'ZSTD');
    """)

    bucket = client.get_bucket('bike-sharing-history')
    blob = bucket.blob(str(parquet_file.relative_to(archive_dir / 'stations')))
    blob.upload_from_filename(
        str(parquet_file),
        timeout=60 * 10
    )
    print(f"Uploaded {parquet_file} to {blob.name}")

for csv_file in archive_dir.rglob('weather/**/*.csv'):
    parquet_file = csv_file.with_suffix('.parquet')

    # Skip if the data has already been stored
    key = ('weather-forecast', *re.match(r'archive/weather/([\w\-]+)/(\d+)/(\w+).csv', str(csv_file)).groups())
    if key in existing_parquet_keys:
        print('Skipping', '/'.join(key))
        continue

    duckdb.connect(':memory:').execute(f"""
    COPY (
        SELECT *
        FROM read_csv('{csv_file}', AUTO_DETECT=TRUE)
    )
    TO '{parquet_file}' (FORMAT 'PARQUET', CODEC 'ZSTD');
    """)

    bucket = client.get_bucket('weather-forecast-history')
    blob = bucket.blob(str(parquet_file.relative_to(archive_dir / 'weather')))
    blob.upload_from_filename(
        str(parquet_file),
        timeout=60 * 10
    )
    print(f"Uploaded {parquet_file} to {blob.name}")
