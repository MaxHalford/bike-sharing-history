import dataclasses
import functools
import typing

import requests
import utils


@dataclasses.dataclass
class System:
    provider: str
    city: str
    country: str
    latitude: float
    longitude: float
    scrape: typing.Callable


systems = []

############
# JCDECAUX #
############


def jcdecaux_scrape(city):
    api_key = utils.env["JCDECAUX_API_KEY"]
    url = f"https://api.jcdecaux.com/vls/v1/stations?contract={city}&apiKey={api_key}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    stations = r.json()
    for station in stations:
        del station["last_update"]
    stations = sorted(stations, key=lambda x: x["number"])
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        station["position"]["lng"],
                        station["position"]["lat"],
                    ],
                },
                "properties": {
                    k: v for k, v in station.items() if k not in ["position", "number"]
                },
            }
            for station in stations
        ],
    }


def jcdecaux_city(**kwargs):

    city_name = kwargs["city"]
    jcdecaux_city_name = {
        "Créteil": "creteil",
        "Brussels": "bruxelles",
        "Lillestrøm": "lillestrom",
        "Besançon": "besancon",
        "Sevilla": "seville",
        "Valencia": "valence",
    }.get(city_name, city_name.lower())

    return System(
        provider="JCDecaux",
        scrape=functools.partial(jcdecaux_scrape, city=jcdecaux_city_name),
        **kwargs,
    )

systems.extend(
    [
        jcdecaux_city(
            city="Brisbane", country="🇦🇺", latitude=-27.470125, longitude=153.021072
        ),
        jcdecaux_city(
            city="Brussels", country="🇧🇪", latitude=50.850346, longitude=4.351721
        ),
        jcdecaux_city(
            city="Namur", country="🇧🇪", latitude=50.466667, longitude=4.866667
        ),
        jcdecaux_city(
            city="Santander", country="🇪🇸", latitude=43.462306, longitude=-3.809980
        ),
        jcdecaux_city(
            city="Amiens", country="🇫🇷", latitude=49.894171, longitude=2.295695
        ),
        jcdecaux_city(
            city="Cergy-Pontoise", country="🇫🇷", latitude=49.036890, longitude=2.075053
        ),
        jcdecaux_city(
            city="Créteil", country="🇫🇷", latitude=48.783333, longitude=2.466667
        ),
        jcdecaux_city(
            city="Lyon", country="🇫🇷", latitude=45.764043, longitude=4.835659
        ),
        jcdecaux_city(
            city="Marseille", country="🇫🇷", latitude=43.296482, longitude=5.369780
        ),
        jcdecaux_city(
            city="Mulhouse", country="🇫🇷", latitude=47.750839, longitude=7.335888
        ),
        jcdecaux_city(
            city="Nancy", country="🇫🇷", latitude=48.692054, longitude=6.184417
        ),
        jcdecaux_city(
            city="Nantes", country="🇫🇷", latitude=47.218371, longitude=-1.553621
        ),
        jcdecaux_city(
            city="Rouen", country="🇫🇷", latitude=49.443232, longitude=1.099971
        ),
        jcdecaux_city(
            city="Toulouse", country="🇫🇷", latitude=43.604652, longitude=1.444209
        ),
        jcdecaux_city(
            city="Dublin", country="🇮🇪", latitude=53.349805, longitude=-6.260310
        ),
        jcdecaux_city(
            city="Toyama", country="🇯🇵", latitude=36.695951, longitude=137.213676
        ),
        jcdecaux_city(
            city="Vilnius", country="🇱🇹", latitude=54.687157, longitude=25.279652
        ),
        jcdecaux_city(
            city="Luxembourg", country="🇱🇺", latitude=49.611621, longitude=6.131935
        ),
        jcdecaux_city(
            city="Lillestrøm", country="🇳🇴", latitude=59.955200, longitude=11.050600
        ),
        jcdecaux_city(
            city="Besançon", country="🇫🇷", latitude=47.237829, longitude=6.024054
        ),
        jcdecaux_city(
            city="Maribor", country="🇸🇮", latitude=46.554650, longitude=15.645881
        ),
        jcdecaux_city(
            city="Sevilla", country="🇪🇸", latitude=37.389092, longitude=-5.984459
        ),
        jcdecaux_city(
            city="Valencia", country="🇪🇸", latitude=39.469907, longitude=-0.376288
        ),
        jcdecaux_city(
            city="Lund", country="🇸🇪", latitude=55.704660, longitude=13.191007
        ),
        jcdecaux_city(
            city="Stockholm", country="🇸🇪", latitude=59.329323, longitude=18.068581
        ),
        jcdecaux_city(
            city="Ljubljana", country="🇸🇮", latitude=46.056947, longitude=14.505751
        ),
    ]
)

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

    def get_coordinates(x):
        pos = x.get("position", x)
        return pos["lon"], pos["lat"]

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": get_coordinates(information[station_id]),
                },
                "properties": {
                    **{
                        k: v
                        for k, v in information[station_id].items()
                        if not k.startswith("_") and k not in {"position", "lat", "lon"}
                    },
                    **{
                        k: v
                        for k, v in statuses[station_id].items()
                        if not k.startswith("_")
                    },
                },
            }
            for station_id in sorted(information)
        ],
    }


systems.extend(
    [
        System(
            provider="BCycle",
            city="Boulder",
            country="🇺🇸",
            latitude=40.014984,
            longitude=-105.270546,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.bcycle.com/bcycle_boulder/station_information.json",
                status_url="https://gbfs.bcycle.com/bcycle_boulder/station_status.json",
            ),
        ),
        System(
            provider="Bike Chattanooga",
            city="Chattanooga",
            country="🇺🇸",
            latitude=35.045630,
            longitude=-85.309680,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://chattanooga.publicbikesystem.net/customer/gbfs/v2/en/station_information.json",
                status_url="https://chattanooga.publicbikesystem.net/customer/gbfs/v2/en/station_status.json",
            ),
        ),
        System(
            provider="Careem BIKE",
            city="Dubai",
            country="🇦🇪",
            latitude=25.204849,
            longitude=55.270783,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://dubai.publicbikesystem.net/customer/gbfs/v2/en/station_information.json",
                status_url="https://dubai.publicbikesystem.net/customer/gbfs/v2/en/station_status.json",
            ),
        ),
        System(
            provider="Bike Itaú",
            city="Rio de Janeiro",
            country="🇧🇷",
            latitude=-22.906847,
            longitude=-43.172896,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://riodejaneiro-br.publicbikesystem.net/customer/gbfs/v2/en/station_information",
                status_url="https://riodejaneiro-br.publicbikesystem.net/customer/gbfs/v2/en/station_status",
            ),
        ),
        System(
            provider='Bicloo',
            city='Nantes',
            country='🇫🇷',
            latitude=47.21346056536673,
            longitude=-1.5545907831970511,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://transport.data.gouv.fr/gbfs/nantes/station_information.json',
                status_url='https://transport.data.gouv.fr/gbfs/nantes/station_status.json'
            )
        )
    ]
)
