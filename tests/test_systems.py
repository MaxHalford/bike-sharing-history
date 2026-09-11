import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scrape"))

import systems as systems_module
from systems import gbfs_scrape, systems


class Response:
    def __init__(self, body):
        self.body = body

    def raise_for_status(self):
        return None

    def json(self):
        return self.body


class SystemsTest(unittest.TestCase):
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
        self.assertNotIn(
            "num_bikes_available", result["features"][1]["properties"]
        )

    def test_registry_contains_the_new_gbfs_systems(self) -> None:
        self.assertEqual(len(systems), 224)
        self.assertEqual(
            len(
                {
                    system.gbfs_system_id
                    for system in systems
                    if system.gbfs_system_id
                }
            ),
            222,
        )
        self.assertTrue(
            {"biketobike", "citybikes_helsinki", "nextbike_zz"}
            <= {system.gbfs_system_id for system in systems}
        )

    def test_only_non_gbfs_systems_have_no_catalog_id(self) -> None:
        self.assertEqual(
            {
                (system.provider, system.city)
                for system in systems
                if system.gbfs_system_id is None
            },
            {("JCDecaux", "Créteil"), ("JCDecaux", "Santander")},
        )

    def test_system_coordinates_are_valid(self) -> None:
        for system in systems:
            self.assertLessEqual(abs(system.latitude), 90, system)
            self.assertLessEqual(abs(system.longitude), 180, system)


if __name__ == "__main__":
    unittest.main()
