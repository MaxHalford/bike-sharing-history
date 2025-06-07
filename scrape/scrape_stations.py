import argparse
import concurrent.futures
import json
import logging
import pathlib

from systems import systems
import utils


def scrape_parse_save(scrape, save_to):
    save_to.parent.mkdir(parents=True, exist_ok=True)
    raw_data = utils.exponential_backoff_retry(scrape, max_attempts=5)
    with open(save_to, "w") as f:
        json.dump(raw_data, f, sort_keys=True, indent=4)


def main(city: str = None):
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_city = {
            executor.submit(
                scrape_parse_save,
                scrape=system.scrape,
                save_to=pathlib.Path("data/stations") / utils.slugify(system.city) / f"{utils.slugify(system.provider)}.geojson",
            ): (system.provider, system.city)
            for system in systems
            if city is None or system.city == city
        }

        n_exceptions = 0
        for future in concurrent.futures.as_completed(future_to_city):
            provider, city = future_to_city[future]
            try:
                future.result()
                logging.info(f"✅ {provider} @ {city}")
            except Exception as exc:
                logging.exception(f"❌ {provider} @ {city} {exc}")
                n_exceptions += 1
        if n_exceptions > 5:
            logging.error(f"🚨 {n_exceptions:,d} exceptions out of {len(systems):,d}")
        elif n_exceptions:
            logging.warning(f"⚠️ {n_exceptions:,d} exceptions out of {len(systems):,d}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", help="City to scrape (optional)")
    args = parser.parse_args()
    main(args.city)
