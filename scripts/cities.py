import dataclasses
import functools
import typing

import requests
import conf


@dataclasses.dataclass
class City:
    name: str
    country: str
    latitude: float
    longitude: float
    scrape: typing.Callable

cities = []

############
# JCDECAUX #
############

def jcdecaux_scrape(city):
    api_key = conf.env["JCDECAUX_API_KEY"]
    url = f"https://api.jcdecaux.com/vls/v1/stations?contract={city}&apiKey={api_key}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    stations = r.json()
    for station in stations:
        del station["last_update"]
    return sorted(stations, key=lambda x: x["number"])

def jcdecaux_city(**kwargs):
    return City(
        scrape=functools.partial(jcdecaux_scrape, city=kwargs["name"]),
        **kwargs,
    )

cities.extend([
    jcdecaux_city(
        name="brisbane",
        country="🇦🇺",
        latitude=-27.470125,
        longitude=153.021072
    ),
    jcdecaux_city(
        name="bruxelles",
        country="🇧🇪",
        latitude=50.850346,
        longitude=4.351721
    ),
    jcdecaux_city(
        name="namur",
        country="🇧🇪",
        latitude=50.466667,
        longitude=4.866667
    ),
    jcdecaux_city(
        name="santander",
        country="🇪🇸",
        latitude=43.462306,
        longitude=-3.809980
    ),
    jcdecaux_city(
        name="amiens",
        country="🇫🇷",
        latitude=49.894171,
        longitude=2.295695
    ),
    jcdecaux_city(
        name="cergy-pontoise",
        country="🇫🇷",
        latitude=49.036890,
        longitude=2.075053
    ),
    jcdecaux_city(
        name="creteil",
        country="🇫🇷",
        latitude=48.783333,
        longitude=2.466667
    ),
    jcdecaux_city(
        name="lyon",
        country="🇫🇷",
        latitude=45.764043,
        longitude=4.835659
    ),
    jcdecaux_city(
        name="marseille",
        country="🇫🇷",
        latitude=43.296482,
        longitude=5.369780
    ),
    jcdecaux_city(
        name="mulhouse",
        country="🇫🇷",
        latitude=47.750839,
        longitude=7.335888
    ),
    jcdecaux_city(
        name="nancy",
        country="🇫🇷",
        latitude=48.692054,
        longitude=6.184417
    ),
    jcdecaux_city(
        name="nantes",
        country="🇫🇷",
        latitude=47.218371,
        longitude=-1.553621
    ),
    jcdecaux_city(
        name="rouen",
        country="🇫🇷",
        latitude=49.443232,
        longitude=1.099971
    ),
    jcdecaux_city(
        name="toulouse",
        country="🇫🇷",
        latitude=43.604652,
        longitude=1.444209
    ),
    jcdecaux_city(
        name="dublin",
        country="🇮🇪",
        latitude=53.349805,
        longitude=-6.260310
    ),
    jcdecaux_city(
        name="toyama",
        country="🇯🇵",
        latitude=36.695951,
        longitude=137.213676
    ),
    jcdecaux_city(
        name="vilnius",
        country="🇱🇹",
        latitude=54.687157,
        longitude=25.279652
    ),
    jcdecaux_city(
        name="luxembourg",
        country="🇱🇺",
        latitude=49.611621,
        longitude=6.131935
    ),
    jcdecaux_city(
        name="lillestrom",
        country="🇳🇴",
        latitude=59.955200,
        longitude=11.050600
    ),
    jcdecaux_city(
        name="besancon",
        country="🇫🇷",
        latitude=47.237829,
        longitude=6.024054
    ),
    jcdecaux_city(
        name="maribor",
        country="🇸🇮",
        latitude=46.554650,
        longitude=15.645881
    ),
    jcdecaux_city(
        name="seville",
        country="🇪🇸",
        latitude=37.389092,
        longitude=-5.984459
    ),
    jcdecaux_city(
        name="valence",
        country="🇪🇸",
        latitude=39.469907,
        longitude=-0.376288
    ),
    jcdecaux_city(
        name="lund",
        country="🇸🇪",
        latitude=55.704660,
        longitude=13.191007
    ),
    jcdecaux_city(
        name="stockholm",
        country="🇸🇪",
        latitude=59.329323,
        longitude=18.068581
    ),
    jcdecaux_city(
        name="ljubljana",
        country="🇸🇮",
        latitude=46.056947,
        longitude=14.505751
    )
])

########
# GBFS #
########

def gbfs_scrape(info_url, status_url):
    r = requests.get(info_url)
    r.raise_for_status()
    information = {s["station_id"]: s for s in r.json()["data"]["stations"]}
    r = requests.get(status_url)
    r.raise_for_status()
    statuses = {s["station_id"]: s for s in r.json()["data"]["stations"]}
    stations = [
        {
            "information": {
                k: v
                for k, v in information[station_id].items()
                if not k.startswith("_")
            },
            "status": statuses[station_id],
        }
        for station_id in information
    ]
    for station in stations:
        del station["status"]["last_reported"]
    return stations

cities.extend([
    City(
        name="boulder",
        country="🇺🇸",
        latitude=40.014984,
        longitude=-105.270546,
        scrape=functools.partial(
            gbfs_scrape,
            info_url="https://gbfs.bcycle.com/bcycle_boulder/station_information.json",
            status_url="https://gbfs.bcycle.com/bcycle_boulder/station_status.json",
        )
    ),
    City(
        name="chattanooga",
        country="🇺🇸",
        latitude=35.045630,
        longitude=-85.309680,
        scrape=functools.partial(
            gbfs_scrape,
            info_url="https://chattanooga.publicbikesystem.net/customer/gbfs/v2/en/station_information.json",
            status_url="https://chattanooga.publicbikesystem.net/customer/gbfs/v2/en/station_status.json",
        )
    ),
    City(
        name="dubai",
        country="🇦🇪",
        latitude=25.204849,
        longitude=55.270783,
        scrape=functools.partial(
            gbfs_scrape,
            info_url="https://dubai.publicbikesystem.net/customer/gbfs/v2/en/station_information.json",
            status_url="https://dubai.publicbikesystem.net/customer/gbfs/v2/en/station_status.json",
        )
    ),
    City(
        name="rio-de-janeiro",
        country="🇧🇷",
        latitude=-22.906847,
        longitude=-43.172896,
        scrape=functools.partial(
            gbfs_scrape,
            info_url="https://riodejaneiro-br.publicbikesystem.net/customer/gbfs/v2/en/station_information",
            status_url="https://riodejaneiro-br.publicbikesystem.net/customer/gbfs/v2/en/station_status",
        )
    )
])
