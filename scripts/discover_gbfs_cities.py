import csv
import json
import statistics
import requests
from slugify import slugify
from tqdm import tqdm


def main():
    gbfs_cities = []
    with open("gbfs/systems.csv") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        for row in tqdm(rows):
            try:
                city, country = row["Location"].split(",")
            except ValueError:
                continue
            city = slugify(city.strip())
            country = slugify(country.strip())
            try:
                r = requests.get(row["Auto-Discovery URL"], timeout=5)
            except Exception:
                continue
            try:
                feeds = r.json()["data"].get("en", {}).get("feeds", [])
            except Exception:
                continue
            feeds = {f["name"]: f["url"] for f in feeds}
            if "station_information" in feeds and "station_status" in feeds:
                try:
                    information = requests.get(
                        feeds["station_information"], timeout=5
                    ).json()
                except Exception:
                    continue
                if not information.get("data", {}).get("stations", []):
                    continue
                if not all(
                    isinstance(s["lat"], float) and isinstance(s["lon"], float)
                    for s in information["data"]["stations"]
                ):
                    continue
                latitude = statistics.mean(
                    [s["lat"] for s in information["data"]["stations"]]
                )
                longitude = statistics.mean(
                    [s["lon"] for s in information["data"]["stations"]]
                )
                try:
                    statuses = requests.get(feeds["station_status"], timeout=5).json()
                except Exception:
                    continue
                if len(statuses["data"]["stations"]) != len(
                    information["data"]["stations"]
                ):
                    continue
                gbfs_cities.append(
                    {
                        "city": city,
                        "country": country,
                        "latitude": latitude,
                        "longitude": longitude,
                        "information_url": feeds["station_information"],
                        "status_url": feeds["station_status"],
                    }
                )

    with open("scripts/gbfs_cities.json", "w") as f:
        json.dump(gbfs_cities, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    main()
