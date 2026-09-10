import argparse
import concurrent.futures
import datetime as dt
import json
import logging
import pathlib

import utils
from systems import systems

logger = logging.getLogger(__name__)


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
    selected_systems = [
        system
        for system in systems
        if city_slug is None or utils.slugify(system.city) == city_slug
    ]
    if city_slug is not None and not selected_systems:
        raise ValueError(f"Unknown city slug: {city_slug}")

    run_started_at = dt.datetime.now(dt.timezone.utc)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_city = {
            executor.submit(
                scrape_parse_save,
                scrape=system.scrape,
                save_to=data_root
                / "data/stations"
                / utils.slugify(system.city)
                / f"{utils.slugify(system.provider)}.geojson",
            ): (system.provider, system.city)
            for system in selected_systems
        }

        results_by_city = {}
        n_exceptions = 0
        for future in concurrent.futures.as_completed(future_to_city):
            provider, city = future_to_city[future]
            result, exc = future.result()
            result["provider"] = provider
            result["provider_slug"] = utils.slugify(provider)
            results_by_city.setdefault(utils.slugify(city), []).append(result)
            if exc is None:
                logger.info(f"✅ {provider} @ {city}")
            else:
                logger.error(f"❌ {provider} @ {city} {type(exc).__name__}")
                n_exceptions += 1

        run_finished_at = dt.datetime.now(dt.timezone.utc)
        for result_city_slug, results in results_by_city.items():
            metadata_file = (
                data_root / "data/scrapes/stations" / f"{result_city_slug}.json"
            )
            metadata_file.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_file, "w") as f:
                json.dump(
                    {
                        "run_started_at": run_started_at.isoformat(),
                        "run_finished_at": run_finished_at.isoformat(),
                        "systems": sorted(
                            results, key=lambda result: result["provider"]
                        ),
                    },
                    f,
                    sort_keys=True,
                    indent=4,
                )
        if n_exceptions > 5:
            logger.error(
                f"🚨 {n_exceptions:,d} exceptions out of {len(selected_systems):,d}"
            )
        elif n_exceptions:
            logger.warning(
                f"⚠️ {n_exceptions:,d} exceptions out of {len(selected_systems):,d}"
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
