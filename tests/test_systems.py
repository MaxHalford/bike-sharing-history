import math
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scrape"))

import systems as systems_module
from systems import citybikes_scrape, gbfs_scrape, systems, youbike_scrape


class Response:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self.body


class SystemsTest(unittest.TestCase):
    def test_citybikes_scrape_converts_stations_to_geojson(self) -> None:
        body = {
            "network": {
                "stations": [
                    {
                        "id": "2",
                        "name": "Two",
                        "latitude": 2.2,
                        "longitude": 3.2,
                        "free_bikes": 4,
                        "empty_slots": 5,
                    },
                    {
                        "id": "1",
                        "name": "One",
                        "latitude": 2.1,
                        "longitude": 3.1,
                        "free_bikes": 6,
                        "empty_slots": 7,
                    },
                ]
            }
        }

        with (
            mock.patch.object(systems_module.utils, "env", {}),
            mock.patch.object(
                systems_module.requests, "get", return_value=Response(body)
            ) as get,
        ):
            result = citybikes_scrape("example")

        self.assertEqual(
            [feature["properties"]["id"] for feature in result["features"]],
            ["1", "2"],
        )
        self.assertEqual(result["features"][0]["geometry"]["coordinates"], [3.1, 2.1])
        get.assert_called_once_with(
            "https://api.citybik.es/v2/networks/example",
            params={"fields": "stations"},
            headers={},
            timeout=20,
        )

    def test_youbike_scrape_splits_the_shared_feed_by_area(self) -> None:
        stations = [
            {
                "area_code": "00",
                "station_no": "2",
                "name_en": "Two",
                "lat": "25.2",
                "lng": "121.2",
            },
            {
                "area_code": "00",
                "station_no": "1",
                "name_en": "One",
                "lat": "25.1",
                "lng": "121.1",
            },
            {
                "area_code": "01",
                "station_no": "3",
                "name_en": "Other city",
                "lat": "24.1",
                "lng": "120.1",
            },
        ]

        with mock.patch.object(systems_module, "_youbike_stations", stations):
            result = youbike_scrape("00")

        self.assertEqual(len(result["features"]), 2)
        self.assertEqual(
            [feature["properties"]["station_no"] for feature in result["features"]],
            ["1", "2"],
        )
        self.assertEqual(
            result["features"][0]["geometry"]["coordinates"], [121.1, 25.1]
        )

    def test_gbfs_scrape_keeps_information_without_a_matching_status(self) -> None:
        information = {
            "last_updated": 1,
            "data": {
                "stations": [
                    {"station_id": "1", "name": "One", "lat": 1, "lon": 2},
                    {"station_id": "2", "name": "Two", "lat": 3, "lon": 4},
                ]
            },
        }
        status = {
            "last_updated": 2,
            "data": {"stations": [{"station_id": "1", "num_bikes_available": 5}]},
        }

        with mock.patch.object(
            systems_module.requests,
            "get",
            side_effect=[Response(information), Response(status)],
        ):
            result = gbfs_scrape("information", "status")

        self.assertEqual(len(result["features"]), 2)
        self.assertEqual(result["features"][1]["properties"]["name"], "Two")
        self.assertNotIn("num_bikes_available", result["features"][1]["properties"])

    def test_registry_contains_the_new_gbfs_systems(self) -> None:
        self.assertEqual(len(systems), 369)
        self.assertEqual(
            len({system.gbfs_system_id for system in systems if system.gbfs_system_id}),
            313,
        )
        self.assertTrue(
            {
                "Optymo_FR_Belfort",
                "biketobike",
                "bcycle_aventura",
                "bcycle_bentonville",
                "bcycle_bikelnk",
                "bcycle_cincyredbike",
                "bcycle_desmoines",
                "bcycle_elpaso",
                "bcycle_greenbikeslc",
                "bcycle_greenville",
                "bcycle_heartland",
                "bcycle_jacksoncounty",
                "bcycle_lametro",
                "bcycle_madison",
                "bcycle_memphis",
                "bcycle_nashville",
                "bcycle_pacersbikeshare",
                "bcycle_redding",
                "bcycle_rtcbikeshare",
                "bcycle_sanantonio",
                "bcycle_santabarbara",
                "citybikes_helsinki",
                "levelo_inurba_marseille",
                "mp_ARBRESLE",
                "mp_COQUELICOT",
                "mp_GEVAUDAN",
                "mp_Opale",
                "mp_TARARE",
                "mugibike_vitoria",
                "nextbike_af",
                "nextbike_bj",
                "nextbike_bs",
                "nextbike_bv",
                "nextbike_bz",
                "nextbike_ce",
                "nextbike_cf",
                "nextbike_cn",
                "nextbike_cx",
                "nextbike_ek",
                "nextbike_gu",
                "nextbike_gv",
                "nextbike_gy",
                "nextbike_ls",
                "nextbike_pn",
                "nextbike_st",
                "nextbike_tx",
                "nextbike_um",
                "nextbike_xc",
                "nextbike_zz",
                "trondheimbysykkel",
                "velivert_saint_etienne",
                "velo-tbm-bordeaux",
                "vivelo",
            }
            <= {system.gbfs_system_id for system in systems}
        )

    def test_rejected_and_national_feeds_are_not_registered(self) -> None:
        active_ids = {system.gbfs_system_id for system in systems}

        self.assertTrue(
            systems_module._EXCLUDED_GBFS_SYSTEM_IDS.keys().isdisjoint(active_ids)
        )
        self.assertTrue(
            systems_module._DEFERRED_NATIONAL_GBFS_SYSTEM_IDS.isdisjoint(active_ids)
        )
        self.assertFalse(
            [
                system
                for system in systems
                if system.provider.lower() in {"beryl", "lime"}
            ]
        )

    def test_every_system_has_a_unique_source_id(self) -> None:
        self.assertEqual(
            len({system.source_id for system in systems}),
            len(systems),
        )
        self.assertTrue(
            all(
                system.source_id.startswith(("citybikes:", "youbike:"))
                for system in systems
                if system.gbfs_system_id is None
            )
        )

    def test_inactive_jcdecaux_systems_are_replaced_or_removed(self) -> None:
        providers = {(system.city, system.provider) for system in systems}

        self.assertIn(("Marseille", "levélo"), providers)
        self.assertIn(("Mulhouse", "VéloCité Mulhouse"), providers)
        self.assertIn(("Santander", "TUeBICI"), providers)
        self.assertNotIn(("Cergy-Pontoise", "JCDecaux"), providers)
        self.assertNotIn(("Créteil", "JCDecaux"), providers)

    def test_system_coordinates_are_valid(self) -> None:
        for system in systems:
            self.assertTrue(math.isfinite(system.latitude), system)
            self.assertTrue(math.isfinite(system.longitude), system)
            self.assertLessEqual(abs(system.latitude), 90, system)
            self.assertLessEqual(abs(system.longitude), 180, system)


if __name__ == "__main__":
    unittest.main()
