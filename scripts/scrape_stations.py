import concurrent.futures
import json
import logging
import pathlib

from cities import cities


def scrape_parse_save(scrape, save_to):
    raw_data = scrape()
    with open(save_to, "w") as f:
        json.dump(raw_data, f, sort_keys=True, indent=4)

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_city = {
            executor.submit(
                scrape_parse_save,
                scrape=city.scrape,
                save_to=pathlib.Path("data/stations") / f"{city.name}.geojson"
            ): city.name
            for city in cities
        }

    n_exceptions = 0
    for future in concurrent.futures.as_completed(future_to_city):
        city_name = future_to_city[future]
        try:
            future.result()
            logging.info(f"✅ {city_name}")
        except Exception as exc:
            logging.exception(f"❌ {city_name} {exc}")
            n_exceptions += 1
    if n_exceptions:
        logging.warning(f"⚠️ {n_exceptions:,d} exceptions out of {len(cities):,d}")


if __name__ == "__main__":
    main()
