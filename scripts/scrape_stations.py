import concurrent.futures
import json
import logging
import pathlib

from systems import systems
import utils


def scrape_parse_save(scrape, save_to):
    save_to.parent.mkdir(parents=True, exist_ok=True)
    raw_data = utils.exponential_backoff_retry(scrape, max_attempts=4)
    with open(save_to, "w") as f:
        json.dump(raw_data, f, sort_keys=True, indent=4)


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_city = {
            executor.submit(
                scrape_parse_save,
                scrape=system.scrape,
                save_to=pathlib.Path("data/stations") / utils.slugify(system.city) / f"{utils.slugify(system.provider)}.geojson",
            ): (system.provider, system.city)
            for system in systems
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
        if n_exceptions:
            raise RuntimeError(f"⚠️ {n_exceptions:,d} exceptions out of {len(systems):,d}")


if __name__ == "__main__":
    main()
