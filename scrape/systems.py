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
    gbfs_system_id: str | None = None


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
                "properties": {k: v for k, v in station.items() if k != "position"},
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
            city="Ljubljana", country="🇸🇮", latitude=46.056947, longitude=14.505751
        ),
    ]
)
########
# GBFS #
########


def gbfs_scrape(info_url, status_url):
    r = requests.get(info_url, timeout=10)
    r.raise_for_status()
    information_feed = r.json()
    information = {s["station_id"]: s for s in information_feed["data"]["stations"]}

    r = requests.get(status_url, timeout=10)
    r.raise_for_status()
    status_feed = r.json()
    statuses = {s["station_id"]: s for s in status_feed["data"]["stations"]}

    def get_coordinates(x):
        pos = x.get("position", x)
        return pos["lon"], pos["lat"]

    return {
        "type": "FeatureCollection",
        # GeoJSON permits foreign members. Preserve the GBFS response metadata
        # which used to be discarded, including feed-level last_updated, ttl,
        # and version values.
        "gbfs": {
            "station_information": {
                key: value for key, value in information_feed.items() if key != "data"
            },
            "station_status": {
                key: value for key, value in status_feed.items() if key != "data"
            },
        },
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
                        for k, v in statuses.get(station_id, {}).items()
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
            provider="BIXI",
            city="Montréal",
            country="🇨🇦",
            latitude=45.5019,
            longitude=73.5674,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.velobixi.com/gbfs/fr/station_information.json",
                status_url="https://gbfs.velobixi.com/gbfs/fr/station_status.json",
            ),
        ),
        System(
            provider="Bluebikes",
            city="Boston",
            country="🇺🇸",
            latitude=42.3601,
            longitude=-71.0589,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.lyft.com/gbfs/1.1/bos/en/station_information.json",
                status_url="https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json",
            ),
        ),
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
            provider="C-Vélo",
            city="Clermont-Ferrand",
            country="🇫🇷",
            latitude=45.781306657894724,
            longitude=3.0946273052631583,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://clermontferrand.publicbikesystem.net/customer/gbfs/v2/en/station_information",
                status_url="https://clermontferrand.publicbikesystem.net/customer/gbfs/v2/en/station_status",
            ),
        ),
        System(
            provider="Smovengo",
            city="Paris",
            country="🇫🇷",
            latitude=48.856614,
            longitude=2.352222,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_information.json",
                status_url="https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json",
            ),
        ),
        System(
            provider="Bay Wheels",
            city="San Francisco Bay Area",
            country="🇺🇸",
            latitude=37.716962491434934,
            longitude=-122.3003446524034,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.lyft.com/gbfs/1.1/bay/en/station_information.json",
                status_url="https://gbfs.lyft.com/gbfs/1.1/bay/en/station_status.json",
            ),
        ),
        System(
            provider="Mobi Bike Share",
            city="Vancouver",
            country="🇨🇦",
            latitude=49.07083961264891,
            longitude=-122.61374698354875,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.kappa.fifteen.eu/gbfs/2.2/mobi/en/station_information.json",
                status_url="https://gbfs.kappa.fifteen.eu/gbfs/2.2/mobi/en/station_status.json",
            ),
        ),
        System(
            provider="Indego",
            city="Philadelphia",
            country="🇺🇸",
            latitude=39.952583,
            longitude=-75.165222,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.bcycle.com/bcycle_indego/station_information.json",
                status_url="https://gbfs.bcycle.com/bcycle_indego/station_status.json",
            ),
        ),
        System(
            provider="Ecobici",
            city="Buenos Aires",
            country="🇦🇷",
            latitude=-34.603722,
            longitude=-58.381592,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://buenosaires.publicbikesystem.net/customer/ube/gbfs/v1/en/station_information",
                status_url="https://buenosaires.publicbikesystem.net/customer/ube/gbfs/v1/en/station_status",
            ),
        ),
        System(
            provider="Nextbike",
            city="Vienna",
            country="🇦🇹",
            latitude=48.208174,
            longitude=16.373819,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_wr/de/station_information.json",
                status_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_wr/de/station_status.json",
            ),
        ),
        System(
            provider="Blue-bike",
            city="Antwerp",
            country="🇧🇪",
            latitude=51.219448,
            longitude=4.402464,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://api.delijn.be/gbfs/station_information.json",
                status_url="https://api.delijn.be/gbfs/station_status.json",
            ),
        ),
        System(
            provider="Velo Antwerpen",
            city="Antwerp",
            country="🇧🇪",
            latitude=51.219448,
            longitude=4.402464,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.smartbike.com/antwerp/1.0/de/station_information.json",
                status_url="https://gbfs.smartbike.com/antwerp/1.0/de/station_status.json",
            ),
        ),
        System(
            provider="Bike Itaú",
            city="Porto Alegre",
            country="🇧🇷",
            latitude=-30.034647,
            longitude=-51.217658,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://portoalegre.publicbikesystem.net/customer/gbfs/v2/en/station_information",
                status_url="https://portoalegre.publicbikesystem.net/customer/gbfs/v2/en/station_status",
            ),
        ),
        System(
            provider="Bike Itaú",
            city="Sampa",
            country="🇧🇷",
            latitude=-23.55052,
            longitude=-46.633308,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://saopaulo.publicbikesystem.net/customer/gbfs/v2/en/station_information",
                status_url="https://saopaulo.publicbikesystem.net/customer/gbfs/v2/en/station_status",
            ),
        ),
        System(
            provider="Bike Share Toronto",
            city="Toronto",
            country="🇨🇦",
            latitude=43.65107,
            longitude=-79.347015,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://toronto.publicbikesystem.net/customer/gbfs/v2/en/station_information",
                status_url="https://toronto.publicbikesystem.net/customer/gbfs/v2/en/station_status",
            ),
        ),
        System(
            provider="àVélo",
            city="Québec City",
            country="🇨🇦",
            latitude=46.813878,
            longitude=-71.207981,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://quebec.publicbikesystem.net/customer/gbfs/v2/en/station_information",
                status_url="https://quebec.publicbikesystem.net/customer/gbfs/v2/en/station_status",
            ),
        ),
        # NOTE: Salvador (Brazil) was removed — it was incorrectly pointing to Santiago's API.
        # Re-add when the correct GBFS endpoint is found.
        System(
            provider="Tembici",
            city="Bogotá",
            country="🇨🇴",
            latitude=4.710989,
            longitude=-74.072092,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://bogota.publicbikesystem.net/customer/gbfs/v2/en/station_information",
                status_url="https://bogota.publicbikesystem.net/customer/gbfs/v2/en/station_status",
            ),
        ),
        System(
            provider="Nextbike",
            city="Brno",
            country="🇨🇿",
            latitude=49.195061,
            longitude=16.606836,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_te/cs/station_information.json",
                status_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_te/cs/station_status.json",
            ),
        ),
        System(
            provider="Nextbike",
            city="Ostrava",
            country="🇨🇿",
            latitude=49.820923,
            longitude=18.262524,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_to/cs/station_information.json",
                status_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_to/cs/station_status.json",
            ),
        ),
        System(
            provider="Nextbike",
            city="Prague",
            country="🇨🇿",
            latitude=50.075538,
            longitude=14.437800,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tg/cs/station_information.json",
                status_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tg/cs/station_status.json",
            ),
        ),
        System(
            provider="Frelo Freiburg",
            city="Freiburg",
            country="🇩🇪",
            latitude=47.999008,
            longitude=7.842104,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_df/de/station_information.json",
                status_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_df/de/station_status.json",
            ),
        ),
        System(
            provider="Nextbike",
            city="Berlin",
            country="🇩🇪",
            latitude=52.520008,
            longitude=13.404954,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bn/de/station_information.json",
                status_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bn/de/station_status.json",
            ),
        ),
        System(
            provider="Nextbike",
            city="Düsseldorf",
            country="🇩🇪",
            latitude=51.227741,
            longitude=6.773456,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dd/de/station_information.json",
                status_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dd/de/station_status.json",
            ),
        ),
        System(
            provider="Nextbike",
            city="Leipzig",
            country="🇩🇪",
            latitude=51.339695,
            longitude=12.373075,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_le/de/station_information.json",
                status_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_le/de/station_status.json",
            ),
        ),
        System(
            provider="bicimad",
            city="Madrid",
            country="🇪🇸",
            latitude=40.416775,
            longitude=-3.703790,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://madrid.publicbikesystem.net/customer/gbfs/v2/en/station_information",
                status_url="https://madrid.publicbikesystem.net/customer/gbfs/v2/en/station_status",
            ),
        ),
        System(
            provider="Bicing",
            city="Barcelona",
            country="🇪🇸",
            latitude=41.385064,
            longitude=2.173404,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://barcelona.publicbikesystem.net/customer/gbfs/v2/en/station_information",
                status_url="https://barcelona.publicbikesystem.net/customer/gbfs/v2/en/station_status",
            ),
        ),
        System(
            provider="Beryl",
            city="Brighton",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=50.822530,
            longitude=-0.137163,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://beryl-gbfs-production.web.app/v2_2/Brighton/station_information.json",
                status_url="https://beryl-gbfs-production.web.app/v2_2/Brighton/station_status.json",
            ),
        ),
        System(
            provider="Beryl",
            city="Manchester",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=50.719164,
            longitude=-1.880769,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://beryl-gbfs-production.web.app/v2_2/Greater_Manchester/station_information.json",
                status_url="https://beryl-gbfs-production.web.app/v2_2/Greater_Manchester/station_status.json",
            ),
        ),
        System(
            provider="Beryl",
            city="Norwich",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=52.630886,
            longitude=1.297355,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://beryl-gbfs-production.web.app/v2_2/Norwich/station_information.json",
                status_url="https://beryl-gbfs-production.web.app/v2_2/Norwich/station_status.json",
            ),
        ),
        System(
            provider="Beryl",
            city="Plymouth",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=50.375456,
            longitude=-4.142656,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://beryl-gbfs-production.web.app/v2_2/Plymouth/station_information.json",
                status_url="https://beryl-gbfs-production.web.app/v2_2/Plymouth/station_status.json",
            ),
        ),
        System(
            provider="Beryl",
            city="Portsmouth",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=50.819767,
            longitude=-1.087976,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://beryl-gbfs-production.web.app/v2_2/Portsmouth/station_information.json",
                status_url="https://beryl-gbfs-production.web.app/v2_2/Portsmouth/station_status.json",
            ),
        ),
        System(
            provider="Beryl",
            city="Southampton",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=50.909698,
            longitude=-1.404351,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://beryl-gbfs-production.web.app/v2_2/Southampton/station_information.json",
                status_url="https://beryl-gbfs-production.web.app/v2_2/Southampton/station_status.json",
            ),
        ),
        System(
            provider="MOL Bubi",
            city="Budapest",
            country="🇭🇺",
            latitude=47.497913,
            longitude=19.040236,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.urbansharing.com/molbubi.hu/station_information.json",
                status_url="https://gbfs.urbansharing.com/molbubi.hu/station_status.json",
            ),
        ),
        System(
            provider="Bikemi",
            city="Milan",
            country="🇮🇹",
            latitude=45.464203,
            longitude=9.189982,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.urbansharing.com/bikemi.com/station_information.json",
                status_url="https://gbfs.urbansharing.com/bikemi.com/station_status.json",
            ),
        ),
        System(
            provider="Docomo Bike Sharing",
            city="Tokyo",
            country="🇯🇵",
            latitude=35.682839,
            longitude=139.759455,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://api-public.odpt.org/api/v4/gbfs/docomo-cycle-tokyo/station_information.json",
                status_url="https://api-public.odpt.org/api/v4/gbfs/docomo-cycle-tokyo/station_status.json",
            ),
        ),
        System(
            provider="Ecobici",
            city="Mexico City",
            country="🇲🇽",
            latitude=19.432608,
            longitude=-99.133209,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.mex.lyftbikes.com/gbfs/en/station_information.json",
                status_url="https://gbfs.mex.lyftbikes.com/gbfs/en/station_status.json",
            ),
        ),
        System(
            provider="Mibici",
            city="Guadalajara",
            country="🇲🇽",
            latitude=20.659698,
            longitude=-103.349609,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://guadalajara.publicbikesystem.net/customer/gbfs/v2/en/station_information",
                status_url="https://guadalajara.publicbikesystem.net/customer/gbfs/v2/en/station_status",
            ),
        ),
        System(
            provider="Bergen Bysykkel",
            city="Bergen",
            country="🇳🇴",
            latitude=60.391262,
            longitude=5.322054,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://api.entur.io/mobility/v2/gbfs/bergenbysykkel/station_information",
                status_url="https://api.entur.io/mobility/v2/gbfs/bergenbysykkel/station_status",
            ),
        ),
        System(
            provider="Kolumbus Bysykkel",
            city="Stavanger",
            country="🇳🇴",
            latitude=58.969976,
            longitude=5.733107,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://api.entur.io/mobility/v2/gbfs/kolumbusbysykkel/station_information",
                status_url="https://api.entur.io/mobility/v2/gbfs/kolumbusbysykkel/station_status",
            ),
        ),
        System(
            provider="Oslo Bysykkel",
            city="Oslo",
            country="🇳🇴",
            latitude=59.913869,
            longitude=10.752245,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://api.entur.io/mobility/v2/gbfs/oslobysykkel/station_information",
                status_url="https://api.entur.io/mobility/v2/gbfs/oslobysykkel/station_status",
            ),
        ),
        System(
            provider="Styr & Ställ",
            city="Gothenburg",
            country="🇸🇪",
            latitude=57.708870,
            longitude=11.974560,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zg/sv/station_information.json",
                status_url="https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zg/sv/station_status.json",
            ),
        ),
        System(
            provider="Biki",
            city="Honolulu",
            country="🇺🇸",
            latitude=21.306944,
            longitude=-157.858333,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://honolulu.publicbikesystem.net/customer/gbfs/v2/en/station_information",
                status_url="https://honolulu.publicbikesystem.net/customer/gbfs/v2/en/station_status",
            ),
        ),
        System(
            provider="Bublr Bikes",
            city="Milwaukee",
            country="🇺🇸",
            latitude=43.038902,
            longitude=-87.906471,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.bcycle.com/bcycle_bublr/station_information.json",
                status_url="https://gbfs.bcycle.com/bcycle_bublr/station_status.json",
            ),
        ),
        System(
            provider="Capital Bikeshare",
            city="Washington D.C.",
            country="🇺🇸",
            latitude=38.907192,
            longitude=-77.036871,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.lyft.com/gbfs/1.1/dca-cabi/en/station_information.json",
                status_url="https://gbfs.lyft.com/gbfs/1.1/dca-cabi/en/station_status.json",
            ),
        ),
        System(
            provider="citibike",
            city="New York City",
            country="🇺🇸",
            latitude=40.712776,
            longitude=-74.005974,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.lyft.com/gbfs/1.1/bkn/en/station_information.json",
                status_url="https://gbfs.lyft.com/gbfs/1.1/bkn/en/station_status.json",
            ),
        ),
        System(
            provider="Divvy",
            city="Chicago",
            country="🇺🇸",
            latitude=41.878113,
            longitude=-87.629799,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.lyft.com/gbfs/1.1/chi/en/station_information.json",
                status_url="https://gbfs.lyft.com/gbfs/1.1/chi/en/station_status.json",
            ),
        ),
        System(
            provider="BCycle",
            city="Santa Cruz",
            country="🇺🇸",
            latitude=36.974117,
            longitude=-122.030792,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.bcycle.com/bcycle_santacruz/station_information.json",
                status_url="https://gbfs.bcycle.com/bcycle_santacruz/station_status.json",
            ),
        ),
    ]
)
_EXISTING_GBFS_SYSTEM_IDS = {
    ('JCDecaux', 'Brussels'): 'bruxelles',
    ('JCDecaux', 'Namur'): 'namur',
    ('JCDecaux', 'Santander'): None,
    ('JCDecaux', 'Amiens'): 'amiens',
    ('JCDecaux', 'Cergy-Pontoise'): 'cergy',
    ('JCDecaux', 'Créteil'): None,
    ('JCDecaux', 'Lyon'): 'lyon',
    ('JCDecaux', 'Marseille'): 'levelo_inurba_marseille',
    ('JCDecaux', 'Mulhouse'): 'mulhouse',
    ('JCDecaux', 'Nancy'): 'nancy',
    ('JCDecaux', 'Nantes'): 'nantes',
    ('JCDecaux', 'Toulouse'): 'toulouse',
    ('JCDecaux', 'Dublin'): 'dublin',
    ('JCDecaux', 'Toyama'): 'toyama',
    ('JCDecaux', 'Vilnius'): 'vilnius',
    ('JCDecaux', 'Luxembourg'): 'luxembourg',
    ('JCDecaux', 'Lillestrøm'): 'lillestrom',
    ('JCDecaux', 'Besançon'): 'besancon',
    ('JCDecaux', 'Maribor'): 'maribor',
    ('JCDecaux', 'Sevilla'): 'seville',
    ('JCDecaux', 'Valencia'): 'valence',
    ('JCDecaux', 'Lund'): 'lund',
    ('JCDecaux', 'Ljubljana'): 'ljubljana',
    ('BIXI', 'Montréal'): 'Bixi_MTL',
    ('Bluebikes', 'Boston'): 'bluebikes',
    ('BCycle', 'Boulder'): 'bcycle_boulder',
    ('Bike Chattanooga', 'Chattanooga'): 'bike_chattanooga',
    ('Careem BIKE', 'Dubai'): 'careem_bike',
    ('Bike Itaú', 'Rio de Janeiro'): 'bike_rio',
    ('C-Vélo', 'Clermont-Ferrand'): 'CVelo_FR_Clermont-Ferrand',
    ('Smovengo', 'Paris'): 'Paris',
    ('Bay Wheels', 'San Francisco Bay Area'): 'lyft_bay',
    ('Mobi Bike Share', 'Vancouver'): 'Mobibikes_CA_Vancouver',
    ('Indego', 'Philadelphia'): 'bcycle_indego',
    ('Ecobici', 'Buenos Aires'): 'bike_buenosaires',
    ('Nextbike', 'Vienna'): 'nextbike_wr',
    ('Blue-bike', 'Antwerp'): 'bluebike',
    ('Velo Antwerpen', 'Antwerp'): 'cc_smartbike_antwerp',
    ('Bike Itaú', 'Porto Alegre'): 'bike_poa',
    ('Bike Itaú', 'Sampa'): 'bike_sampa',
    ('Bike Share Toronto', 'Toronto'): 'bike_share_toronto',
    ('àVélo', 'Québec City'): 'avelo_quebec',
    ('Tembici', 'Bogotá'): 'bogota_bike',
    ('Nextbike', 'Brno'): 'nextbike_te',
    ('Nextbike', 'Ostrava'): 'nextbike_to',
    ('Nextbike', 'Prague'): 'nextbike_tg',
    ('Frelo Freiburg', 'Freiburg'): 'nextbike_df',
    ('Nextbike', 'Berlin'): 'nextbike_bn',
    ('Nextbike', 'Düsseldorf'): 'nextbike_dd',
    ('Nextbike', 'Leipzig'): 'nextbike_le',
    ('bicimad', 'Madrid'): 'bicimad_madrid',
    ('Bicing', 'Barcelona'): 'bike_barcelona',
    ('Beryl', 'Brighton'): 'beryl_brighton',
    ('Beryl', 'Manchester'): 'beryl_greater_manchester',
    ('Beryl', 'Norwich'): 'beryl_norwich',
    ('Beryl', 'Plymouth'): 'beryl_plymouth',
    ('Beryl', 'Portsmouth'): 'beryl_portsmouth',
    ('Beryl', 'Southampton'): 'beryl_southampton',
    ('MOL Bubi', 'Budapest'): 'inurba-budapest',
    ('Bikemi', 'Milan'): 'milan-bikemi',
    ('Docomo Bike Sharing', 'Tokyo'): 'docomo-cycle-tokyo',
    ('Ecobici', 'Mexico City'): 'MEX',
    ('Mibici', 'Guadalajara'): 'mibici_guadalajara',
    ('Bergen Bysykkel', 'Bergen'): 'bergen-city-bike',
    ('Kolumbus Bysykkel', 'Stavanger'): 'kolumbusbysykkel',
    ('Oslo Bysykkel', 'Oslo'): 'oslobysykkel',
    ('Styr & Ställ', 'Gothenburg'): 'nextbike_zg',
    ('Biki', 'Honolulu'): 'go_biki',
    ('Bublr Bikes', 'Milwaukee'): 'bcycle_bublr',
    ('Capital Bikeshare', 'Washington D.C.'): 'cabi',
    ('citibike', 'New York City'): 'lyft_nyc',
    ('Divvy', 'Chicago'): 'lyft_chi',
    ('BCycle', 'Santa Cruz'): 'bcycle_santacruz',
}

for system in systems:
    system.gbfs_system_id = _EXISTING_GBFS_SYSTEM_IDS[(system.provider, system.city)]


# Feed metadata comes from MobilityData's GBFS systems catalog.
# City coordinates: © OpenStreetMap contributors, ODbL 1.0; resolved with Nominatim.
_ADDITIONAL_GBFS_SYSTEMS = [
    (
        'MiBiciTuBici', 'Rosario', '🇦🇷',
        -32.959361, -60.661702, 'biketobike',
        'https://www.mibicitubici.gob.ar/opendata/station_information.json',
        'https://www.mibicitubici.gob.ar/opendata/station_status.json',
    ),
    (
        'VVT REGIORAD Tirol', 'Tirol', '🇦🇹',
        47.223193, 11.526103, 'nextbike_vt',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_vt/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_vt/en/station_status.json',
    ),
    (
        'Stadtrad Innsbruck Austria', 'Innsbruck', '🇦🇹',
        47.265430, 11.392769, 'nextbike_si',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_si/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_si/en/station_status.json',
    ),
    (
        'nextbike Klagenfurt Austria', 'Klagenfurt', '🇦🇹',
        46.623943, 14.307598, 'nextbike_ka',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ka/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ka/en/station_status.json',
    ),
    (
        'city bike Linz', 'Linz', '🇦🇹',
        48.305908, 14.286198, 'nextbike_al',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_al/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_al/en/station_status.json',
    ),
    (
        'nextbike BIH', 'Bosnia and Herzegovina', '🇧🇦',
        44.305348, 17.596147, 'nextbike_ba',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ba/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ba/en/station_status.json',
    ),
    (
        'nextbike BE Vlaamse Rand', 'Brussels region', '🇧🇪',
        50.846737, 4.352493, 'nextbike_hf',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_hf/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_hf/en/station_status.json',
    ),
    (
        'nextbike Switzerland', 'Switzerland', '🇨🇭',
        46.798562, 8.231974, 'nextbike_ch',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ch/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ch/en/station_status.json',
    ),
    (
        'nextbike Cyprus', 'Cyprus', '🇨🇾',
        34.917416, 32.889903, 'nextbike_cy',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cy/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cy/en/station_status.json',
    ),
    (
        'nextbike Benešov', 'Benešov', '🇨🇿',
        49.782890, 14.687593, 'nextbike_co',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_co/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_co/en/station_status.json',
    ),
    (
        'nextbike Berounsko', 'Berounsko', '🇨🇿',
        49.964029, 14.073391, 'nextbike_td',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_td/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_td/en/station_status.json',
    ),
    (
        'nextbike Valašsko', 'Valašsko', '🇨🇿',
        49.338977, 17.996153, 'nextbike_vm',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_vm/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_vm/en/station_status.json',
    ),
    (
        'nextbike Mladoboleslavsko', 'Mladá Boleslav', '🇨🇿',
        50.411619, 14.903130, 'nextbike_tq',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tq/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tq/en/station_status.json',
    ),
    (
        'nextbike Dvůr Králové', 'Dvůr Králové', '🇨🇿',
        50.431905, 15.813995, 'nextbike_tf',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tf/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tf/en/station_status.json',
    ),
    (
        'nextbike Frýdek-Místek', 'Frýdek-Místek', '🇨🇿',
        49.685635, 18.348342, 'nextbike_ts',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ts/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ts/en/station_status.json',
    ),
    (
        'nextbike Hodonín', 'Hodonín', '🇨🇿',
        48.856391, 17.123465, 'nextbike_nh',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nh/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nh/en/station_status.json',
    ),
    (
        'nextbike Hořice', 'Hořice', '🇨🇿',
        50.366534, 15.632174, 'nextbike_uf',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_uf/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_uf/en/station_status.json',
    ),
    (
        'nextbike Hradec Králové', 'Hradec Králové', '🇨🇿',
        50.209211, 15.832751, 'nextbike_tl',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tl/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tl/en/station_status.json',
    ),
    (
        'nextbike Hranice', 'Hranice', '🇨🇿',
        49.548176, 17.734741, 'nextbike_na',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_na/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_na/en/station_status.json',
    ),
    (
        'nextbike Jablonec', 'Jablonec nad Nisou', '🇨🇿',
        50.724090, 15.171096, 'nextbike_ud',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ud/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ud/en/station_status.json',
    ),
    (
        'nextbike Jičín', 'Jičín', '🇨🇿',
        50.437045, 15.351653, 'nextbike_nt',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nt/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nt/en/station_status.json',
    ),
    (
        'nextbike Kladno', 'Kladno', '🇨🇿',
        50.146605, 14.102640, 'nextbike_tk',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tk/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tk/en/station_status.json',
    ),
    (
        'nextbike Klášterec nad Ohří', 'Klášterec nad Ohří', '🇨🇿',
        50.384305, 13.171019, 'nextbike_ko',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ko/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ko/en/station_status.json',
    ),
    (
        'nextbike Kolín', 'Kolin', '🇨🇿',
        50.028889, 15.201157, 'nextbike_ni',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ni/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ni/en/station_status.json',
    ),
    (
        'nextbike Krnov', 'Krnov', '🇨🇿',
        50.089894, 17.704084, 'nextbike_tw',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tw/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tw/en/station_status.json',
    ),
    (
        'nextbike Kyjov', 'Kyjov', '🇨🇿',
        49.010446, 17.122487, 'nextbike_ky',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ky/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ky/en/station_status.json',
    ),
    (
        'nextbike Liberec', 'Liberec', '🇨🇿',
        50.770265, 15.058395, 'nextbike_xa',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_xa/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_xa/en/station_status.json',
    ),
    (
        'nextbike Litovel', 'Litovel', '🇨🇿',
        49.701330, 17.075878, 'nextbike_nl',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nl/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nl/en/station_status.json',
    ),
    (
        'nextbike Lovosice', 'Lovosice', '🇨🇿',
        50.515003, 14.051756, 'nextbike_lo',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_lo/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_lo/en/station_status.json',
    ),
    (
        'nextbike Most', 'Most', '🇨🇿',
        50.503274, 13.636112, 'nextbike_uo',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_uo/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_uo/en/station_status.json',
    ),
    (
        'nextbike Neratovice', 'Neratovice', '🇨🇿',
        50.259848, 14.517509, 'nextbike_ne',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ne/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ne/en/station_status.json',
    ),
    (
        'nextbike OlbramoviceVotice', 'Olbramovice', '🇨🇿',
        49.676979, 14.632755, 'nextbike_cu',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cu/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cu/en/station_status.json',
    ),
    (
        'nextbike Opava', 'Opava', '🇨🇿',
        49.938900, 17.902417, 'nextbike_tj',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tj/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tj/en/station_status.json',
    ),
    (
        'nextbike Otrokovice', 'Otrokovice', '🇨🇿',
        49.208828, 17.535387, 'nextbike_ot',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ot/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ot/en/station_status.json',
    ),
    (
        'nextbike Pelhřimov', 'Pelhřimov', '🇨🇿',
        49.430874, 15.223234, 'nextbike_cq',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cq/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cq/en/station_status.json',
    ),
    (
        'nextbike Písek', 'Písek', '🇨🇿',
        49.308989, 14.147769, 'nextbike_ty',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ty/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ty/en/station_status.json',
    ),
    (
        'nextbike Přerov', 'Přerov', '🇨🇿',
        49.455377, 17.450862, 'nextbike_nr',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nr/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nr/en/station_status.json',
    ),
    (
        'nextbike Roudnice nad Labem', 'Roudnice nad Labem', '🇨🇿',
        50.424446, 14.260382, 'nextbike_rl',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_rl/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_rl/en/station_status.json',
    ),
    (
        'nextbike Trutnov', 'Trutnov', '🇨🇿',
        50.560817, 15.912897, 'nextbike_xb',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_xb/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_xb/en/station_status.json',
    ),
    (
        'nextbike Třebíč', 'Třebíč', '🇨🇿',
        49.215875, 15.881084, 'nextbike_tu',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tu/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tu/en/station_status.json',
    ),
    (
        'nextbike Uherské Hradiště', 'Uherské Hradiště', '🇨🇿',
        49.068102, 17.466390, 'nextbike_tt',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tt/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tt/en/station_status.json',
    ),
    (
        'nextbike Uničov', 'Uničov', '🇨🇿',
        49.771184, 17.121394, 'nextbike_nu',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nu/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nu/en/station_status.json',
    ),
    (
        'nextbike Vrchlabí', 'Vrchlabí', '🇨🇿',
        50.627145, 15.609578, 'nextbike_vr',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_vr/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_vr/en/station_status.json',
    ),
    (
        'nextbike Zlín', 'Zlín', '🇨🇿',
        49.226766, 17.666742, 'nextbike_tv',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tv/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tv/en/station_status.json',
    ),
    (
        'nextbike Česká Třebová', 'Česká Třebová', '🇨🇿',
        49.902159, 16.447204, 'nextbike_nc',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nc/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nc/en/station_status.json',
    ),
    (
        'nextbike Český Brod', 'Český Brod', '🇨🇿',
        50.074054, 14.860611, 'nextbike_nd',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nd/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nd/en/station_status.json',
    ),
    (
        'nextbike Šumperk', 'Šumperk', '🇨🇿',
        49.965552, 16.970565, 'nextbike_ns',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ns/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ns/en/station_status.json',
    ),
    (
        'nextbike Ždár nad Sázavou', 'Ždár nad Sázavou', '🇨🇿',
        49.562901, 15.939192, 'nextbike_zs',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zs/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zs/en/station_status.json',
    ),
    (
        'euregiobike', 'Aachen', '🇩🇪',
        50.776351, 6.083862, 'nextbike_an',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_an/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_an/en/station_status.json',
    ),
    (
        'moin mobil Achim', 'Achim', '🇩🇪',
        53.020744, 9.024707, 'nextbike_am',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_am/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_am/en/station_status.json',
    ),
    (
        'swabi - augsburg', 'Augsburg', '🇩🇪',
        48.369034, 10.897952, 'swabi',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/swabi/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/swabi/en/station_status.json',
    ),
    (
        'Bergisches e-Bike', 'Bergisches Land', '🇩🇪',
        50.992930, 7.127738, 'nextbike_ac',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ac/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ac/en/station_status.json',
    ),
    (
        'Campus Berlin-Buch', 'Berlin-Buch', '🇩🇪',
        52.636672, 13.499929, 'nextbike_cb',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cb/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cb/en/station_status.json',
    ),
    (
        'Bre.Bike', 'Bremen', '🇩🇪',
        53.075820, 8.807165, 'nextbike_bq',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bq/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bq/en/station_status.json',
    ),
    (
        'HelBi (Kreis Soest)', 'Soest', '🇩🇪',
        51.572550, 8.106126, 'nextbike_hb',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_hb/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_hb/en/station_status.json',
    ),
    (
        'flux Bikesharing', 'Friedrichsdorf', '🇩🇪',
        50.262091, 8.624890, 'nextbike_ev',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ev/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ev/en/station_status.json',
    ),
    (
        'nextbike Gießen', 'Gießen', '🇩🇪',
        50.586207, 8.674231, 'nextbike_ng',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ng/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ng/en/station_status.json',
    ),
    (
        'Graben - ready4green', 'Graben', '🇩🇪',
        48.189081, 10.822031, 'nextbike_da',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_da/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_da/en/station_status.json',
    ),
    (
        'StadtRad Greifswald', 'Greifswald', '🇩🇪',
        54.095791, 13.381524, 'nextbike_ug',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ug/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ug/en/station_status.json',
    ),
    (
        'EDEKA Grünheide', 'Grünheide (Mark)', '🇩🇪',
        52.426230, 13.822646, 'nextbike_ed',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ed/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ed/en/station_status.json',
    ),
    (
        'nextbike Gütersloh', 'Gütersloh', '🇩🇪',
        51.916662, 8.404328, 'nextbike_dj',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dj/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dj/en/station_status.json',
    ),
    (
        'movemix_bike', 'Halle', '🇩🇪',
        51.482435, 11.971298, 'nextbike_mx',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_mx/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_mx/en/station_status.json',
    ),
    (
        'nextbike Hannover', 'Hannover', '🇩🇪',
        52.374478, 9.738553, 'nextbike_dh',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dh/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dh/en/station_status.json',
    ),
    (
        'westBike', 'Heinsberg', '🇩🇪',
        51.065427, 6.098446, 'nextbike_gh',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gh/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gh/en/station_status.json',
    ),
    (
        'nextbike Kassel', 'Kassel', '🇩🇪',
        51.315783, 9.497848, 'nextbike_dk',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dk/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dk/en/station_status.json',
    ),
    (
        'Mein konrad', 'Konstanz', '🇩🇪',
        47.659216, 9.175072, 'nextbike_kk',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_kk/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_kk/en/station_status.json',
    ),
    (
        'wupsiRad Leverkusen', 'Leverkusen', '🇩🇪',
        51.032474, 6.988119, 'nextbike_dw',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dw/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dw/en/station_status.json',
    ),
    (
        'nextbike Marburg', 'Marburg', '🇩🇪',
        50.809011, 8.770470, 'nextbike_nm',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nm/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nm/en/station_status.json',
    ),
    (
        'nextbike Norderstedt', 'Norderstedt', '🇩🇪',
        53.708990, 9.989191, 'nextbike_nn',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nn/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_nn/en/station_status.json',
    ),
    (
        'Landkreis Nordsachsen', 'Nordsachsen', '🇩🇪',
        51.442330, 13.038396, 'nextbike_lc',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_lc/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_lc/en/station_status.json',
    ),
    (
        'VAG_Rad', 'Nuremberg', '🇩🇪',
        49.453872, 11.077298, 'nextbike_dv',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dv/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dv/en/station_status.json',
    ),
    (
        'VRNnextbike', 'Rhine-Neckar', '🇩🇪',
        49.489291, 8.467310, 'nextbike_vn',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_vn/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_vn/en/station_status.json',
    ),
    (
        'nextbike Ruhrgebiet', 'Ruhr', '🇩🇪',
        51.458224, 7.015817, 'nextbike_mr',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_mr/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_mr/en/station_status.json',
    ),
    (
        'nextbike Rüsselsheim am Main', 'Rüsselsheim', '🇩🇪',
        49.994849, 8.411636, 'nextbike_do',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_do/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_do/en/station_status.json',
    ),
    (
        'LaRa to go', 'Waiblingen', '🇩🇪',
        48.832566, 9.316382, 'lara_to_go',
        'https://api.mobidata-bw.de/sharing/gbfs/v3/lara_to_go/station_information',
        'https://api.mobidata-bw.de/sharing/gbfs/v3/lara_to_go/station_status',
    ),
    (
        'nextbike Wiesbaden', 'Wiesbaden', '🇩🇪',
        50.082038, 8.241656, 'nextbike_wn',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_wn/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_wn/en/station_status.json',
    ),
    (
        'WinsenRad', 'Winsen (Luhe)', '🇩🇪',
        53.363647, 10.205921, 'nextbike_wd',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_wd/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_wd/en/station_status.json',
    ),
    (
        'biciArteixo', 'Arteixo', '🇪🇸',
        43.304579, -8.507910, 'nextbike_aa',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_aa/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_aa/en/station_status.json',
    ),
    (
        'bizkaibizi (Spain)', 'Bilbao', '🇪🇸',
        43.263002, -2.935004, 'nextbike_bw',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bw/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bw/en/station_status.json',
    ),
    (
        'moxsi (Las Palmas de Gran Canaria)', 'Las Palmas de Gran Canaria', '🇪🇸',
        28.128869, -15.434902, 'nextbike_el',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_el/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_el/en/station_status.json',
    ),
    (
        'nextbike León', 'León', '🇪🇸',
        42.634145, -5.971415, 'nextbike_sl',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_sl/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_sl/en/station_status.json',
    ),
    (
        'nextbike BiciLOG', 'Logroño', '🇪🇸',
        42.466120, -2.439668, 'nextbike_ej',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ej/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ej/en/station_status.json',
    ),
    (
        'BiciMislata', 'Mislata', '🇪🇸',
        39.475144, -0.417913, 'nextbike_ad',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ad/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ad/en/station_status.json',
    ),
    (
        'BiciPalma', 'Palma', '🇪🇸',
        39.569582, 2.650075, 'nextbike_ea',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ea/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ea/en/station_status.json',
    ),
    (
        'Ganxeta', 'Reus', '🇪🇸',
        41.155556, 1.107613, 'ganxeta_reus',
        'https://gbfs.ganxeta.cat/v3/station_information.json',
        'https://gbfs.ganxeta.cat/v3/station_status.json',
    ),
    (
        'City Bikes Helsinki', 'Helsinki', '🇫🇮',
        60.166620, 24.943541, 'citybikes_helsinki',
        'https://gbfs.theta.fifteen.eu/gbfs/2.2/helsinki/en/station_information.json',
        'https://gbfs.theta.fifteen.eu/gbfs/2.2/helsinki/en/station_status.json',
    ),
    (
        'Vélo Modalis Angoulême', 'Angoulême', '🇫🇷',
        45.648451, 0.156195, 'velo_modalis_angouleme',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/angouleme/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/angouleme/en/station_status.json',
    ),
    (
        'Vélonecy', 'Annecy', '🇫🇷',
        45.899235, 6.128885, 'velonecy60minutes_annecy',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/annecy/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/annecy/en/station_status.json',
    ),
    (
        "VALLEE D'OSSAU", 'Arudy', '🇫🇷',
        43.106174, -0.428084, 'mp_OSSAU',
        'https://www.mobility-parc.net/gbfs/v3/OSSAU/station_information.json',
        'https://www.mobility-parc.net/gbfs/v3/OSSAU/station_status.json',
    ),
    (
        'AQTA', 'Auray', '🇫🇷',
        47.666449, -2.983372, 'auray-quiberon',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/auray-quiberon/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/auray-quiberon/en/station_status.json',
    ),
    (
        'Vélopop', 'Avignon', '🇫🇷',
        43.949249, 4.805901, 'velopop',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/avignon/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/avignon/en/station_status.json',
    ),
    (
        'Twisto Vélolib', 'Caen', '🇫🇷',
        49.181340, -0.363561, 'twisto_velolib_caen',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/caen/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/caen/en/station_status.json',
    ),
    (
        'Vel’in', 'Calais', '🇫🇷',
        50.952477, 1.853845, 'calais-velos',
        'https://stce.transdev-hdf.fr/gbfs/station_information.php',
        'https://stce.transdev-hdf.fr/gbfs/station_status.php',
    ),
    (
        'CHATELLERAULT', 'Châtellerault', '🇫🇷',
        46.818005, 0.545812, 'mp_CHATELLERAULT',
        'https://www.mobility-parc.net/gbfs/v3/CHATELLERAULT/station_information.json',
        'https://www.mobility-parc.net/gbfs/v3/CHATELLERAULT/station_status.json',
    ),
    (
        'Vélo Modalis Grand Cognac', 'Cognac', '🇫🇷',
        45.693165, -0.325018, 'velo-modalis',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/velo-modalis/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/velo-modalis/en/station_status.json',
    ),
    (
        'Estrées Saint Denis', 'Estrées-Saint-Denis', '🇫🇷',
        49.426649, 2.644051, 'mp_ESTREES',
        'https://www.mobility-parc.net/gbfs/v3/ESTREES/station_information.json',
        'https://www.mobility-parc.net/gbfs/v3/ESTREES/station_status.json',
    ),
    (
        'VélO2', 'Cergy-Pontoise', '🇫🇷',
        49.052753, 2.038874, 'nextbike_ah',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ah/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ah/en/station_status.json',
    ),
    (
        'Vélo Fluo Grand-Est', 'Grand Est', '🇫🇷',
        48.484516, 6.113035, 'grand-est',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/velo-fluo/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/velo-fluo/en/station_status.json',
    ),
    (
        'Ti Vélo', 'Landerneau', '🇫🇷',
        48.451480, -4.255790, 'ti_velo',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/landerneau/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/landerneau/en/station_status.json',
    ),
    (
        'VELO VEZERE LASCAUX', 'Lascaux', '🇫🇷',
        45.063870, 1.165228, 'mp_LASCAUX',
        'https://www.mobility-parc.net/gbfs/v3/LASCAUX/station_information.json',
        'https://www.mobility-parc.net/gbfs/v3/LASCAUX/station_status.json',
    ),
    (
        "V'lille", 'Lille', '🇫🇷',
        50.636565, 3.063528, 'v_lille',
        'https://media.ilevia.fr/opendata/station_information.json',
        'https://media.ilevia.fr/opendata/station_status.json',
    ),
    (
        'MontenVélo', 'Mont Blanc', '🇫🇷',
        45.936125, 6.630255, 'montenvelo_mont_blanc',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/mont_blanc/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/mont_blanc/en/station_status.json',
    ),
    (
        'IDEcycle (Pau)', 'PAU', '🇫🇷',
        43.295755, -0.368567, 'idecycle_pau',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/pau/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/pau/en/station_status.json',
    ),
    (
        'VéloMoove', 'Pompey', '🇫🇷',
        48.765830, 6.122992, 'velomoove_pompey',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/pompey/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/pompey/en/station_status.json',
    ),
    (
        'LE vélo STAR', 'Rennes', '🇫🇷',
        48.111339, -1.680020, 'le_velo_star',
        'https://eu.ftp.opendatasoft.com/star/gbfs/station_information.json',
        'https://eu.ftp.opendatasoft.com/star/gbfs/station_status.json',
    ),
    (
        'Vélo Modalis Royan', 'Royan', '🇫🇷',
        45.624533, -1.028764, 'modalis_royan',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/modalis-royan/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/modalis-royan/en/station_status.json',
    ),
    (
        "Vélo'Baie", 'Saint-Brieuc', '🇫🇷',
        48.514113, -2.760328, 'saintbrieuc',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/saintbrieuc/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/saintbrieuc/en/station_status.json',
    ),
    (
        'Vélo Modalis Saintes', 'Saintes', '🇫🇷',
        45.746066, -0.630067, 'velo-modalis-saintes',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/saintes/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/saintes/en/station_status.json',
    ),
    (
        'Brennus à Vélo (Sens)', 'Sens', '🇫🇷',
        48.197856, 3.282606, 'brennus_a_velo_sens',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/sens/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/sens/en/station_status.json',
    ),
    (
        'Vélhop - Strasbourg', 'Strasbourg', '🇫🇷',
        48.584614, 7.750713, 'nextbike_ae',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ae/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ae/en/station_status.json',
    ),
    (
        'Vilvolt', 'Épinal', '🇫🇷',
        48.174768, 6.450364, 'vilvolt_epinal',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/epinal/en/station_information.json',
        'https://gbfs.partners.fifteen.eu/gbfs/2.2/epinal/en/station_status.json',
    ),
    (
        'nextbike Stirling', 'Stirling', '🇬🇧',
        56.118124, -3.936001, 'nextbike_uk',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_uk/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_uk/en/station_status.json',
    ),
    (
        'Swansea University Cycles', 'Swansea University', '🇬🇧',
        51.609777, -3.980350, 'nextbike_uu',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_uu/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_uu/en/station_status.json',
    ),
    (
        'Bike Sharing Glyfada', 'Glyfada', '🇬🇷',
        37.861597, 23.754590, 'nextbike_gx',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gx/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gx/en/station_status.json',
    ),
    (
        'Grad Split (Croatia)', 'Split', '🇭🇷',
        43.511638, 16.439966, 'nextbike_gt',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gt/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gt/en/station_status.json',
    ),
    (
        'Bajs Zagreb (Croatia)', 'Grad Zagreb', '🇭🇷',
        45.813097, 15.977279, 'nextbike_hd',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_hd/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_hd/en/station_status.json',
    ),
    (
        'Grad Karlovac (Croatia)', 'Karlovac', '🇭🇷',
        45.489252, 15.548630, 'nextbike_kc',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_kc/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_kc/en/station_status.json',
    ),
    (
        'Grad Križevci (Croatia)', 'Križevci', '🇭🇷',
        46.024739, 16.545779, 'nextbike_gk',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gk/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gk/en/station_status.json',
    ),
    (
        'eMobi (Croatia)', 'Osijek', '🇭🇷',
        45.554879, 18.695369, 'nextbike_em',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_em/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_em/en/station_status.json',
    ),
    (
        'Porec bike share (Croatia)', 'Porec', '🇭🇷',
        45.227196, 13.595733, 'nextbike_cv',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cv/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cv/en/station_status.json',
    ),
    (
        'Grad Zadar (Croatia)', 'Zadar', '🇭🇷',
        44.116859, 15.235326, 'nextbike_zd',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zd/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zd/en/station_status.json',
    ),
    (
        'Grad Šibenik (Croatia)', 'Šibenik', '🇭🇷',
        43.734065, 15.894477, 'nextbike_bc',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bc/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bc/en/station_status.json',
    ),
    (
        'Verona Bike', 'Verona', '🇮🇹',
        45.442498, 10.985738, 'verona-bike',
        'https://gbfs.urbansharing.com/bikeverona.it/station_information.json',
        'https://gbfs.urbansharing.com/bikeverona.it/station_status.json',
    ),
    (
        'BIKER Białystok', 'Białystok', '🇵🇱',
        53.132398, 23.159168, 'nextbike_bp',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bp/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bp/en/station_status.json',
    ),
    (
        'Chełmski Rower', 'Chełm', '🇵🇱',
        51.133922, 23.471155, 'nextbike_cw',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cw/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_cw/en/station_status.json',
    ),
    (
        'MEVO', 'Gdansk', '🇵🇱',
        54.348291, 18.654023, 'inurba-gdansk',
        'https://gbfs.urbansharing.com/rowermevo.pl/station_information.json',
        'https://gbfs.urbansharing.com/rowermevo.pl/station_status.json',
    ),
    (
        'GRM Grodzisk Poland', 'Grodzisk Mazowiecki', '🇵🇱',
        52.106622, 20.631344, 'nextbike_gp',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gp/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gp/en/station_status.json',
    ),
    (
        'JasKółka', 'Jastrzębie-Zdrój', '🇵🇱',
        49.951909, 18.602361, 'nextbike_pj',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_pj/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_pj/en/station_status.json',
    ),
    (
        'Koszaliński Rower Miejski Poland', 'Koszalin', '🇵🇱',
        54.190920, 16.177070, 'nextbike_ps',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ps/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ps/en/station_status.json',
    ),
    (
        'Kołobrzeski Rower Nextbike', 'Kołobrzeg', '🇵🇱',
        54.175961, 15.576421, 'nextbike_kr',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_kr/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_kr/en/station_status.json',
    ),
    (
        'Mławskie Rowery Miejskie', 'Mława', '🇵🇱',
        53.111618, 20.383173, 'nextbike_oe',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_oe/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_oe/en/station_status.json',
    ),
    (
        'Otwocki Rower Miejski', 'Otwock', '🇵🇱',
        52.104120, 21.268109, 'nextbike_os',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_os/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_os/en/station_status.json',
    ),
    (
        'Piaseczyński Rower Miejski', 'Piaseczno', '🇵🇱',
        52.074738, 21.027089, 'nextbike_pi',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_pi/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_pi/en/station_status.json',
    ),
    (
        'VETURILO 3.0', 'Warsaw', '🇵🇱',
        52.231958, 21.006725, 'nextbike_vw',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_vw/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_vw/en/station_status.json',
    ),
    (
        'Pruszkowski Rower Miejski', 'Pruszków', '🇵🇱',
        52.162614, 20.808020, 'nextbike_or',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_or/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_or/en/station_status.json',
    ),
    (
        'System Rowerów Miejskich w Pszczynie', 'Pszczyna', '🇵🇱',
        49.977809, 18.942372, 'nextbike_ap',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ap/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ap/en/station_status.json',
    ),
    (
        'Tarnowski Rower Miejski', 'Tarnów', '🇵🇱',
        50.012378, 20.988074, 'nextbike_tn',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tn/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tn/en/station_status.json',
    ),
    (
        'Toruński Rower Miejski', 'Toruń', '🇵🇱',
        53.010272, 18.604809, 'nextbike_tr',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tr/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tr/en/station_status.json',
    ),
    (
        'METROROWER', 'Tychy', '🇵🇱',
        50.114397, 18.996593, 'nextbike_zz',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zz/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zz/en/station_status.json',
    ),
    (
        'Włower - Włocławski Rower Miejski', 'Włocławek', '🇵🇱',
        52.660387, 19.071948, 'nextbike_wf',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_wf/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_wf/en/station_status.json',
    ),
    (
        'Zielonogórski Rower Miejski', 'Zielona Góra', '🇵🇱',
        51.938378, 15.505041, 'nextbike_pm',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_pm/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_pm/en/station_status.json',
    ),
    (
        'ŁoKeR - Łomża', 'Łomża', '🇵🇱',
        53.175070, 22.072755, 'nextbike_oa',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_oa/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_oa/en/station_status.json',
    ),
    (
        'Żyrardowski Rower Miejski', 'Żyrardów', '🇵🇱',
        52.054331, 20.443501, 'nextbike_zy',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zy/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zy/en/station_status.json',
    ),
    (
        'Bora', 'Viseu Dão Lafões', '🇵🇹',
        40.521456, -8.083606, 'bora_viseu',
        'https://gbfs.primelayer.pt/gbfs-smartmobility/gbfs/v3/station_information.json',
        'https://gbfs.primelayer.pt/gbfs-smartmobility/gbfs/v3/station_status.json',
    ),
    (
        'Alba Iulia Velocity', 'Alba Iulia', '🇷🇴',
        46.068275, 23.566476, 'nextbike_ai',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ai/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ai/en/station_status.json',
    ),
    (
        'BikeCity Campia Turzii', 'Câmpia Turzii', '🇷🇴',
        46.547181, 23.886967, 'nextbike_rc',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_rc/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_rc/en/station_status.json',
    ),
    (
        'Topoloveni Bike', 'Topoloveni', '🇷🇴',
        44.807972, 25.085284, 'nextbike_rt',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_rt/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_rt/en/station_status.json',
    ),
    (
        'Arriva Bike', 'Nitra', '🇸🇰',
        48.312950, 18.089459, 'nextbike_as',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_as/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_as/en/station_status.json',
    ),
    (
        'Senica bajk', 'Senica', '🇸🇰',
        48.678756, 17.366153, 'nextbike_av',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_av/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_av/en/station_status.json',
    ),
    (
        'AAR Bike', 'Konya', '🇹🇷',
        37.872734, 32.492438, 'linka_aar_bike',
        'https://app.linkalock.com/api/gbfs/D2uRLGw8vBa2FJxa8/station_information.json',
        'https://app.linkalock.com/api/gbfs/D2uRLGw8vBa2FJxa8/station_status.json',
    ),
    (
        'Prishtina bike (Kosovo)', 'Prishtina', '🇽🇰',
        42.663877, 21.164085, 'nextbike_gs',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gs/en/station_information.json',
        'https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gs/en/station_status.json',
    ),
]

systems.extend(
    System(
        provider=provider,
        city=city,
        country=country,
        latitude=latitude,
        longitude=longitude,
        gbfs_system_id=gbfs_system_id,
        scrape=functools.partial(
            gbfs_scrape, info_url=info_url, status_url=status_url
        ),
    )
    for (
        provider,
        city,
        country,
        latitude,
        longitude,
        gbfs_system_id,
        info_url,
        status_url,
    ) in _ADDITIONAL_GBFS_SYSTEMS
)
