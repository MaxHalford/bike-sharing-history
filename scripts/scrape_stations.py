import concurrent.futures
import dataclasses
import functools
import json
import logging
import pathlib
import os
import typing

import requests

with open(".env") as f:
    env = dict(kv.strip().split('=') for kv in f.readlines())
    JCDECAUX_API_KEY = env["JCDECAUX_API_KEY"]

logging.basicConfig(level="INFO", format="%(levelname)s %(message)s")

@dataclasses.dataclass
class City:
    name: str
    scrape: typing.Callable

    def scrape_parse_save(self, to):
        raw_data = self.scrape()
        with open(to / f"{self.name}.json", "w") as f:
            json.dump(raw_data, f, sort_keys=True, indent=4)

cities = []

############
# JCDECAUX #
############

jcdecaux_cities = [
    "brisbane",
    "bruxelles",
    "namur",
    "santander",
    "amiens",
    "cergy-pontoise",
    "creteil",
    "lyon",
    "marseille",
    "mulhouse",
    "nancy",
    "nantes",
    "rouen",
    "toulouse",
    "dublin",
    "toyama",
    "vilnius",
    "luxembourg",
    "lillestrom",
    "besancon",
    "maribor",
    "seville",
    "valence",
    "lund",
    "stockholm",
    "ljubljana",
]

def jcdecaux_scrape(city):
    api_key = JCDECAUX_API_KEY
    url = f"https://api.jcdecaux.com/vls/v1/stations?contract={city}&apiKey={api_key}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    stations = r.json()
    for station in stations:
        del station["last_update"]
    return sorted(stations, key=lambda x: x["number"])

cities.extend(
    City(
        city,
        scrape=functools.partial(jcdecaux_scrape, city)
    )
    for city in jcdecaux_cities
)

########
# GBFS #
########

with open(pathlib.Path(__file__).parent / "gbfs_cities.json") as f:
    gbfs_cities = json.load(f)

def gbfs_scrape(info_url, status_url):
    r = requests.get(info_url)
    r.raise_for_status()
    information = {s["station_id"]: s for s in r.json()["data"]["stations"]}
    r = requests.get(status_url)
    r.raise_for_status()
    statuses = {s["station_id"]: s for s in r.json()["data"]["stations"]}
    stations = [
        {
            "information": information[station_id],
            "status": statuses[station_id],
        }
        for station_id in information
    ]
    for station in stations:
        del station["status"]["last_reported"]
    return stations

cities.extend(
    City(
        city["city"],
        scrape=functools.partial(
            gbfs_scrape,
            info_url=city["information_url"],
            status_url=city["status_url"],
        )
    )
    for city in gbfs_cities[:20]
)

cities.extend([
    City(
        "chattanooga",
        scrape=functools.partial(
            gbfs_scrape,
            info_url="https://chattanooga.publicbikesystem.net/customer/gbfs/v2/en/station_information.json",
            status_url="https://chattanooga.publicbikesystem.net/customer/gbfs/v2/en/station_status.json",
        )
    ),
    City(
        "dubai",
        scrape=functools.partial(
            gbfs_scrape,
            info_url="https://dubai.publicbikesystem.net/customer/gbfs/v2/en/station_information.json",
            status_url="https://dubai.publicbikesystem.net/customer/gbfs/v2/en/station_status.json",
        )
    ),
    City(
        "rio-de-janeiro",
        scrape=functools.partial(
            gbfs_scrape,
            info_url="https://riodejaneiro-br.publicbikesystem.net/customer/gbfs/v2/en/station_information",
            status_url="https://riodejaneiro-br.publicbikesystem.net/customer/gbfs/v2/en/station_status",
        )
    )
])


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_city = {
            executor.submit(
                city.scrape_parse_save,
                to=pathlib.Path("data/stations")
            ): city.name
            for city in cities
        }

    n_exceptions = 0
    for future in concurrent.futures.as_completed(future_to_city):
        city_name = future_to_city[future]
        try:
            future.result()
            logging.info(f"✅ {city_name}")
        except Exception as exc:
            logging.exception(f"❌ {city_name} {exc}")
            n_exceptions += 1
    if n_exceptions:
        logging.warning(f"⚠️ {n_exceptions:,d} exceptions out of {len(cities):,d}")


if __name__ == "__main__":
    main()
