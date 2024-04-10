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
            provider="BIXI",
            city="Montréal",
            country='🇨🇦',
            latitude=45.5019,
            longitude=73.5674,
            scrape=functools.partial(
                gbfs_scrape,
                info_url="https://gbfs.velobixi.com/gbfs/fr/station_information.json",
                status_url="https://gbfs.velobixi.com/gbfs/fr/station_status.json",
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
            provider='Bird',
            city='Bordeaux',
            country='🇫🇷',
            latitude=44.84377499845755,
            longitude=-0.5843216203476395,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://mds.bird.co/gbfs/v2/public/bordeaux/station_information.json',
                status_url='https://mds.bird.co/gbfs/v2/public/bordeaux/station_status.json'
            )
        ),
        System(
            provider='Bird',
            city='Châlons-en-Champagne',
            country='🇫🇷',
            latitude=48.95389565865669,
            longitude=4.364512797796962,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://mds.bird.co/gbfs/v2/public/chalonsenchampagne/station_information.json',
                status_url='https://mds.bird.co/gbfs/v2/public/chalonsenchampagne/station_status.json'
            )
        ),
        System(
            provider='Bird',
            city='Draguignan',
            country='🇫🇷',
            latitude=43.53293289391363,
            longitude=6.466050043868904,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://mds.bird.co/gbfs/v2/public/draguignan/station_information.json',
                status_url='https://mds.bird.co/gbfs/v2/public/draguignan/station_status.json'
            )
        ),
        System(
            provider='Bird',
            city='La Roche-sur-Yon',
            country='🇫🇷',
            latitude=46.66938416018546,
            longitude=-1.4284853789022371,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://mds.bird.co/gbfs/v2/public/larochesuryon/station_information.json',
                status_url='https://mds.bird.co/gbfs/v2/public/larochesuryon/station_status.json'
            )
        ),
        System(
            provider='Bird',
            city='Laval',
            country='🇫🇷',
            latitude=48.07000010472725,
            longitude=-0.7707006983860001,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://mds.bird.co/gbfs/v2/public/laval/station_information.json',
                status_url='https://mds.bird.co/gbfs/v2/public/laval/station_status.json'
            )
        ),
        System(
            provider='Bird',
            city='Marseille',
            country='🇫🇷',
            latitude=43.291472383388545,
            longitude=5.3886846196188625,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://mds.bird.co/gbfs/v2/public/marseille/station_information.json',
                status_url='https://mds.bird.co/gbfs/v2/public/marseille/station_status.json'
            )
        ),
        System(
            provider='Bird',
            city='Millau',
            country='🇫🇷',
            latitude=44.10274359594474,
            longitude=3.072323394253621,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://mds.bird.co/gbfs/v2/public/millau/station_information.json',
                status_url='https://mds.bird.co/gbfs/v2/public/millau/station_status.json'
            )
        ),
        System(
            provider='Bird',
            city='Montluçon',
            country='🇫🇷',
            latitude=46.34088949353921,
            longitude=2.600538760958011,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://mds.bird.co/gbfs/v2/public/montlucon/station_information.json',
                status_url='https://mds.bird.co/gbfs/v2/public/montlucon/station_status.json'
            )
        ),
        System(
            provider='Bird',
            city='Sarreguemines',
            country='🇫🇷',
            latitude=49.11062577893537,
            longitude=7.070520369681416,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://mds.bird.co/gbfs/v2/public/sarreguemines/station_information.json',
                status_url='https://mds.bird.co/gbfs/v2/public/sarreguemines/station_status.json'
            )
        ),
        System(
            provider='Bird',
            city='Vichy',
            country='🇫🇷',
            latitude=46.12709559264645,
            longitude=3.4254834051107093,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://mds.bird.co/gbfs/v2/public/vichy/station_information.json',
                status_url='https://mds.bird.co/gbfs/v2/public/vichy/station_status.json'
            )
        ),
        System(
            provider='C-Vélo',
            city='Clermont-Ferrand',
            country='🇫🇷',
            latitude=45.781306657894724,
            longitude=3.0946273052631583,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://clermontferrand.publicbikesystem.net/customer/gbfs/v2/en/station_information',
                status_url='https://clermontferrand.publicbikesystem.net/customer/gbfs/v2/en/station_status'
            )
        ),
        System(
            provider='Donkey Republic',
            city='Brest',
            country='🇫🇷',
            latitude=48.39133502000002,
            longitude=-4.486644220000002,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://stables.donkey.bike/api/public/gbfs/2/donkey_brest/en/station_information.json',
                status_url='https://stables.donkey.bike/api/public/gbfs/2/donkey_brest/en/station_status.json'
            )
        ),
        System(
            provider='Donkey Republic',
            city='Valenciennes',
            country='🇫🇷',
            latitude=50.34180905945946,
            longitude=3.5188289567567566,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://stables.donkey.bike/api/public/gbfs/2/donkey_valenciennes/en/station_information.json',
                status_url='https://stables.donkey.bike/api/public/gbfs/2/donkey_valenciennes/en/station_status.json'
            )
        ),
        System(
            provider='Lime',
            city='Marseille',
            country='🇫🇷',
            latitude=43.3909,
            longitude=5.4266,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://data.lime.bike/api/partners/v2/gbfs/marseille/station_information',
                status_url='https://data.lime.bike/api/partners/v2/gbfs/marseille/station_status'
            )
        ),
        System(
            provider='Lime',
            city='Paris',
            country='🇫🇷',
            latitude=48.829,
            longitude=2.3898,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://data.lime.bike/api/partners/v2/gbfs/paris/station_information',
                status_url='https://data.lime.bike/api/partners/v2/gbfs/paris/station_status'
            )
        ),
        # System(
        #     provider='Optymo',
        #     city='Belfort',
        #     country='🇫🇷',
        #     latitude=47.63146551428573,
        #     longitude=6.859593971428572,
        #     scrape=functools.partial(
        #         gbfs_scrape,
        #         info_url='https://belfort-gbfs.klervi.net/gbfs/en/station_information.json',
        #         status_url='https://belfort-gbfs.klervi.net/gbfs/en/station_status.json'
        #     )
        # ),
        # System(
        #     provider='Vélivert',
        #     city='Saint-Etienne',
        #     country='🇫🇷',
        #     latitude=45.441481028125,
        #     longitude=4.389507587500001,
        #     scrape=functools.partial(
        #         gbfs_scrape,
        #         info_url='https://saint-etienne-gbfs.klervi.net/gbfs/en/station_information.json',
        #         status_url='https://saint-etienne-gbfs.klervi.net/gbfs/en/station_status.json'
        #     )
        # ),
        # System(
        #     provider='Vélocéo',
        #     city='Vannes',
        #     country='🇫🇷',
        #     latitude=47.65592616666665,
        #     longitude=-2.7642901666666666,
        #     scrape=functools.partial(
        #         gbfs_scrape,
        #         info_url='https://vannes-gbfs.klervi.net/gbfs/en/station_information.json',
        #         status_url='https://vannes-gbfs.klervi.net/gbfs/en/station_status.json'
        #     )
        # ),
        # System(
        #     provider="Vélomagg'",
        #     city='Montpellier',
        #     country='🇫🇷',
        #     latitude=43.609848249603445,
        #     longitude=3.87712589659722,
        #     scrape=functools.partial(
        #         gbfs_scrape,
        #         info_url='https://montpellier-fr-smoove.klervi.net/gbfs/en/station_information.json',
        #         status_url='https://montpellier-fr-smoove.klervi.net/gbfs/en/station_status.json'
        #     )
        # ),
        System(
            provider='Smovengo',
            city='Paris',
            country='🇫🇷',
            latitude=43.653908,
            longitude=-79.384293,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_information.json',
                status_url='https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json'
            )
        ),
        System(
            provider='Bay Wheels',
            city='San Francisco Bay Area',
            country='🇺🇸',
            latitude=37.716962491434934,
            longitude=-122.3003446524034,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.lyft.com/gbfs/1.1/bay/en/station_information.json',
                status_url='https://gbfs.lyft.com/gbfs/1.1/bay/en/station_status.json'
            )
        ),
        System(
            provider='Mobi Bike Share',
            city='Vancouver',
            country='🇨🇦',
            latitude=49.07083961264891,
            longitude=-122.61374698354875,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://vancouver-gbfs.smoove.pro/gbfs/2/en/station_information.json',
                status_url='https://vancouver-gbfs.smoove.pro/gbfs/2/en/station_status.json'
            )
        ),
        System(
            provider='Indego',
            city='Philadelphia',
            country='🇺🇸',
            latitude=39.952583,
            longitude=-75.165222,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.bcycle.com/bcycle_indego/station_information.json',
                status_url='https://gbfs.bcycle.com/bcycle_indego/station_status.json'
            )
        ),
        System(
            provider='Ecobici',
            city='Buenos Aires',
            country='🇦🇷',
            latitude=-34.603722,
            longitude=-58.381592,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://buenosaires.publicbikesystem.net/customer/ube/gbfs/v1/en/station_information',
                status_url='https://buenosaires.publicbikesystem.net/customer/ube/gbfs/v1/en/station_status'
            )
        ),
        System(
            provider='Nextbike',
            city='Vienna',
            country='🇦🇹',
            latitude=48.208174,
            longitude=16.373819,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_wr/de/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_wr/de/station_status.json'
            )
        ),
        System(
            provider='Blue-bike',
            city='Antwerp',
            country='🇧🇪',
            latitude=51.219448,
            longitude=4.402464,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://api.delijn.be/gbfs/station_information.json',
                status_url='https://api.delijn.be/gbfs/station_status.json'
            )
        ),
        System(
            provider='Velo Antwerpen',
            city='Antwerp',
            country='🇧🇪',
            latitude=51.219448,
            longitude=4.402464,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.smartbike.com/antwerp/1.0/de/station_information.json',
                status_url='https://gbfs.smartbike.com/antwerp/1.0/de/station_status.json'
            )
        ),
        System(
            provider="Bike Itaú",
            city="Porto Alegre",
            country="🇧🇷",
            latitude=-30.034647,
            longitude=-51.217658,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://portoalegre.publicbikesystem.net/customer/gbfs/v2/en/station_information',
                status_url='https://portoalegre.publicbikesystem.net/customer/gbfs/v2/en/station_status'
            )
        ),
        System(
            provider="Bike Itaú",
            city="Sampa",
            country="🇧🇷",
            latitude=-23.55052,
            longitude=-46.633308,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://saopaulo.publicbikesystem.net/customer/gbfs/v2/en/station_information',
                status_url='https://saopaulo.publicbikesystem.net/customer/gbfs/v2/en/station_status'
            )
        ),
        System(
            provider="Bike Share Toronto",
            city="Toronto",
            country="🇨🇦",
            latitude=43.65107,
            longitude=-79.347015,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://toronto.publicbikesystem.net/customer/gbfs/v2/en/station_information',
                status_url='https://toronto.publicbikesystem.net/customer/gbfs/v2/en/station_status'
            )
        ),
        System(
            provider="àVélo",
            city="Québec City",
            country="🇨🇦",
            latitude=46.813878,
            longitude=-71.207981,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://quebec.publicbikesystem.net/customer/gbfs/v2/en/station_information',
                status_url='https://quebec.publicbikesystem.net/customer/gbfs/v2/en/station_status'
            )
        ),
        System(
            provider="Bike Itaú",
            city="Salvador",
            country="🇧🇷",
            latitude=-12.971599,
            longitude=-38.501705,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://santiago.publicbikesystem.net/customer/gbfs/v2/en/station_information',
                status_url='https://santiago.publicbikesystem.net/customer/gbfs/v2/en/station_status'
            )
        ),
        System(
            provider="Tembici",
            city="Bogotá",
            country="🇨🇴",
            latitude=4.710989,
            longitude=-74.072092,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://bogota.publicbikesystem.net/customer/gbfs/v2/en/station_information',
                status_url='https://bogota.publicbikesystem.net/customer/gbfs/v2/en/station_status'
            )
        ),
        System(
            provider="Nextbike",
            city="Brno",
            country="🇨🇿",
            latitude=49.195061,
            longitude=16.606836,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_te/cs/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_te/cs/station_status.json'
            )
        ),
        System(
            provider="Nextbike",
            city="Ostrava",
            country="🇨🇿",
            latitude=49.820923,
            longitude=18.262524,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_to/cs/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_to/cs/station_status.json'
            )
        ),
        System(
            provider="Nextbike",
            city="Olomouc",
            country="🇨🇿",
            latitude=49.593778,
            longitude=17.250878,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ti/cs/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ti/cs/station_status.json'
            )
        ),
        System(
            provider="Nextbike",
            city="Prague",
            country="🇨🇿",
            latitude=50.075538,
            longitude=14.437800,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tg/cs/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_tg/cs/station_status.json'
            )
        ),
        System(
            provider="Frelo Freiburg",
            city="Freiburg",
            country="🇩🇪",
            latitude=47.999008,
            longitude=7.842104,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_df/de/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_df/de/station_status.json'
            )
        ),
        System(
            provider="Nextbike",
            city="Berlin",
            country="🇩🇪",
            latitude=52.520008,
            longitude=13.404954,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bn/de/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bn/de/station_status.json'
            )
        ),
        System(
            provider="Nextbike",
            city="Düsseldorf",
            country="🇩🇪",
            latitude=51.227741,
            longitude=6.773456,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dd/de/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_dd/de/station_status.json'
            )
        ),
        System(
            provider="Nextbike",
            city="Frankfurt",
            country="🇩🇪",
            latitude=50.110924,
            longitude=8.682127,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ff/de/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_ff/de/station_status.json'
            )
        ),
        System(
            provider="Nextbike",
            city="Leipzig",
            country="🇩🇪",
            latitude=51.339695,
            longitude=12.373075,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_le/de/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_le/de/station_status.json'
            )
        ),
        System(
            provider="bicimad",
            city="Madrid",
            country="🇪🇸",
            latitude=40.416775,
            longitude=-3.703790,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://madrid.publicbikesystem.net/customer/gbfs/v2/en/station_information',
                status_url='https://madrid.publicbikesystem.net/customer/gbfs/v2/en/station_status'
            )
        ),
        System(
            provider="Bicing",
            city="Barcelona",
            country="🇪🇸",
            latitude=41.385064,
            longitude=2.173404,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://barcelona.publicbikesystem.net/customer/gbfs/v2/en/station_information',
                status_url='https://barcelona.publicbikesystem.net/customer/gbfs/v2/en/station_status'
            )
        ),
        System(
            provider="Beryl",
            city="Brighton",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=50.822530,
            longitude=-0.137163,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://beryl-gbfs-production.web.app/v2_2/Brighton/station_information.json',
                status_url='https://beryl-gbfs-production.web.app/v2_2/Brighton/station_status.json'
            )
        ),
        System(
            provider="Beryl",
            city="Manchester",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=50.719164,
            longitude=-1.880769,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://beryl-gbfs-production.web.app/v2_2/Greater_Manchester/station_information.json',
                status_url='https://beryl-gbfs-production.web.app/v2_2/Greater_Manchester/station_status.json'
            )
        ),
        System(
            provider="Beryl",
            city="Norwich",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=52.630886,
            longitude=1.297355,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://beryl-gbfs-production.web.app/v2_2/Norwich/station_information.json',
                status_url='https://beryl-gbfs-production.web.app/v2_2/Norwich/station_status.json'
            )
        ),
        System(
            provider="Beryl",
            city="Plymouth",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=50.375456,
            longitude=-4.142656,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://beryl-gbfs-production.web.app/v2_2/Plymouth/station_information.json',
                status_url='https://beryl-gbfs-production.web.app/v2_2/Plymouth/station_status.json'
            )
        ),
        System(
            provider="Beryl",
            city="Portsmouth",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=50.819767,
            longitude=-1.087976,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://beryl-gbfs-production.web.app/v2_2/Portsmouth/station_information.json',
                status_url='https://beryl-gbfs-production.web.app/v2_2/Portsmouth/station_status.json'
            )
        ),
        System(
            provider="Beryl",
            city="Southampton",
            country="🏴󠁧󠁢󠁥󠁮󠁧󠁿",
            latitude=50.909698,
            longitude=-1.404351,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://beryl-gbfs-production.web.app/v2_2/Southampton/station_information.json',
                status_url='https://beryl-gbfs-production.web.app/v2_2/Southampton/station_status.json'
            )
        ),
        System(
            provider="Nextbike",
            city="Glasgow",
            country="🏴󠁧󠁢󠁳󠁣󠁴󠁿",
            latitude=55.864239,
            longitude=-4.251806,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gg/en/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_gg/en/station_status.json'
            )
        ),
        System(
            provider="MOL Bubi",
            city="Budapest",
            country="🇭🇺",
            latitude=47.497913,
            longitude=19.040236,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bh/hu/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_bh/hu/station_status.json'
            )
        ),
        System(
            provider="Bikemi",
            city="Milan",
            country="🇮🇹",
            latitude=45.464203,
            longitude=9.189982,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.urbansharing.com/bikemi.com/station_information.json',
                status_url='https://gbfs.urbansharing.com/bikemi.com/station_status.json'
            )
        ),
        System(
            provider="Docomo Bike Sharing",
            city="Tokyo",
            country="🇯🇵",
            latitude=35.682839,
            longitude=139.759455,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://api-public.odpt.org/api/v4/gbfs/docomo-cycle-tokyo/station_information.json',
                status_url='https://api-public.odpt.org/api/v4/gbfs/docomo-cycle-tokyo/station_status.json'
            )
        ),
        System(
            provider="Ecobici",
            city="Mexico City",
            country="🇲🇽",
            latitude=19.432608,
            longitude=-99.133209,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.mex.lyftbikes.com/gbfs/en/station_information.json',
                status_url='https://gbfs.mex.lyftbikes.com/gbfs/en/station_status.json'
            )
        ),
        System(
            provider="Mibici",
            city="Guadalajara",
            country="🇲🇽",
            latitude=20.659698,
            longitude=-103.349609,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://guadalajara.publicbikesystem.net/customer/gbfs/v2/en/station_information',
                status_url='https://guadalajara.publicbikesystem.net/customer/gbfs/v2/en/station_status'
            )
        ),
        System(
            provider="Bergen Bysykkel",
            city="Bergen",
            country="🇳🇴",
            latitude=60.391262,
            longitude=5.322054,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://api.entur.io/mobility/v2/gbfs/bergenbysykkel/station_information',
                status_url='https://api.entur.io/mobility/v2/gbfs/bergenbysykkel/station_status'
            )
        ),
        System(
            provider="Kolumbus Bysykkel",
            city="Stavanger",
            country="🇳🇴",
            latitude=58.969976,
            longitude=5.733107,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://api.entur.io/mobility/v2/gbfs/kolumbusbysykkel/station_information',
                status_url='https://api.entur.io/mobility/v2/gbfs/kolumbusbysykkel/station_status'
            )
        ),
        System(
            provider="Oslo Bysykkel",
            city="Oslo",
            country="🇳🇴",
            latitude=59.913869,
            longitude=10.752245,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://api.entur.io/mobility/v2/gbfs/oslobysykkel/station_information',
                status_url='https://api.entur.io/mobility/v2/gbfs/oslobysykkel/station_status'
            )
        ),
        System(
            provider="Styr & Ställ",
            city="Gothenburg",
            country="🇸🇪",
            latitude=57.708870,
            longitude=11.974560,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zg/sv/station_information.json',
                status_url='https://gbfs.nextbike.net/maps/gbfs/v2/nextbike_zg/sv/station_status.json'
            )
        ),
        System(
            provider="Biki",
            city="Honolulu",
            country="🇺🇸",
            latitude=21.306944,
            longitude=-157.858333,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://honolulu.publicbikesystem.net/customer/gbfs/v2/en/station_information',
                status_url='https://honolulu.publicbikesystem.net/customer/gbfs/v2/en/station_status'
            )
        ),
        System(
            provider="Bublr Bikes",
            city="Milwaukee",
            country="🇺🇸",
            latitude=43.038902,
            longitude=-87.906471,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.bcycle.com/bcycle_bublr/station_information.json',
                status_url='https://gbfs.bcycle.com/bcycle_bublr/station_status.json'
            )
        ),
        System(
            provider="Capital Bikeshare",
            city="Washington D.C.",
            country="🇺🇸",
            latitude=38.907192,
            longitude=-77.036871,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.lyft.com/gbfs/1.1/dca-cabi/en/station_information.json',
                status_url='https://gbfs.lyft.com/gbfs/1.1/dca-cabi/en/station_status.json'
            )
        ),
        System(
            provider="citibike",
            city="New York City",
            country="🇺🇸",
            latitude=40.712776,
            longitude=-74.005974,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.lyft.com/gbfs/1.1/bkn/en/station_information.json',
                status_url='https://gbfs.lyft.com/gbfs/1.1/bkn/en/station_status.json'
            )
        ),
        System(
            provider="Divvy",
            city="Chicago",
            country="🇺🇸",
            latitude=41.878113,
            longitude=-87.629799,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.lyft.com/gbfs/1.1/chi/en/station_information.json',
                status_url='https://gbfs.lyft.com/gbfs/1.1/chi/en/station_status.json'
            )
        ),
        System(
            provider="BCycle",
            city="Santa Cruz",
            country="🇺🇸",
            latitude=36.974117,
            longitude=-122.030792,
            scrape=functools.partial(
                gbfs_scrape,
                info_url='https://gbfs.bcycle.com/bcycle_santacruz/station_information.json',
                status_url='https://gbfs.bcycle.com/bcycle_santacruz/station_status.json'
            )
        )
    ]
)
