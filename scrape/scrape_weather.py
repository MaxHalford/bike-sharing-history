import argparse
import concurrent.futures
import datetime as dt
import functools
import json
import logging
import pathlib

import requests
import utils
from systems import systems

logger = logging.getLogger(__name__)


def fetch_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,rain,windspeed_10m&forecast_days=1&timezone=UTC"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    weather = r.json()
    del weather["generationtime_ms"]
    return weather


def scrape_parse_save(scrape, save_to):
    started_at = dt.datetime.now(dt.timezone.utc)
    attempts = 0

    def record_attempt(attempt):
        nonlocal attempts
        attempts = attempt

    try:
        raw_data = utils.exponential_backoff_retry(
            scrape, max_attempts=5, on_attempt=record_attempt
        )
        save_to.parent.mkdir(parents=True, exist_ok=True)
        with open(save_to, "w") as f:
            json.dump(raw_data, f, sort_keys=True, indent=4)
    except Exception as exc:  # noqa: BLE001 - scraper implementations are arbitrary
        return {
            "status": "error",
            "attempts": attempts,
            "started_at": started_at.isoformat(),
            "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "error_type": type(exc).__name__,
        }, exc
    return {
        "status": "ok",
        "attempts": attempts,
        "started_at": started_at.isoformat(),
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }, None


def main(
    city_slug: str | None = None,
    data_root: pathlib.Path = pathlib.Path("."),
):
    run_started_at = dt.datetime.now(dt.timezone.utc)
    # Deduplicate by city so we don't fetch weather twice for cities with multiple providers
    seen_cities = {}
    for system in systems:
        system_city_slug = utils.slugify(system.city)
        if system_city_slug not in seen_cities:
            seen_cities[system_city_slug] = system

    if city_slug is not None and city_slug not in seen_cities:
        raise ValueError(f"Unknown city slug: {city_slug}")
    selected_cities = {
        slug: system
        for slug, system in seen_cities.items()
        if city_slug is None or slug == city_slug
    }

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_city = {
            executor.submit(
                scrape_parse_save,
                scrape=functools.partial(
                    fetch_weather, system.latitude, system.longitude
                ),
                save_to=data_root / "data/weather" / f"{selected_city_slug}.json",
            ): system.city
            for selected_city_slug, system in selected_cities.items()
        }

        results_by_city = {}
        n_exceptions = 0
        for future in concurrent.futures.as_completed(future_to_city):
            city = future_to_city[future]
            result, exc = future.result()
            result_city_slug = utils.slugify(city)
            results_by_city[result_city_slug] = result
            if exc is None:
                logger.info(f"✅ {city}")
            else:
                logger.error(f"❌ {city} {type(exc).__name__}")
                n_exceptions += 1

        run_finished_at = dt.datetime.now(dt.timezone.utc)
        for result_city_slug, result in results_by_city.items():
            metadata_file = (
                data_root / "data/scrapes/weather" / f"{result_city_slug}.json"
            )
            metadata_file.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_file, "w") as f:
                json.dump(
                    {
                        "run_started_at": run_started_at.isoformat(),
                        "run_finished_at": run_finished_at.isoformat(),
                        **result,
                    },
                    f,
                    sort_keys=True,
                    indent=4,
                )
        if n_exceptions > 5:
            logger.error(
                f"🚨 {n_exceptions:,d} exceptions out of {len(selected_cities):,d}"
            )
        elif n_exceptions:
            logger.warning(
                f"⚠️ {n_exceptions:,d} exceptions out of {len(selected_cities):,d}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city-slug", help="City slug to scrape (optional)")
    parser.add_argument(
        "--data-root",
        type=pathlib.Path,
        default=pathlib.Path("."),
        help="Directory under which data/ is written",
    )
    args = parser.parse_args()
    main(args.city_slug, args.data_root)
