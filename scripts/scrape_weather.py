import concurrent.futures
import functools
import json
import logging
import pathlib

import requests

from cities import cities


def fetch_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,rain,windspeed_10m&forecast_days=1"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    weather = r.json()
    del weather["generationtime_ms"]
    return weather

def scrape_parse_save(scrape, save_to):
    raw_data = scrape()
    with open(save_to, "w") as f:
        json.dump(raw_data, f, sort_keys=True, indent=4)

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_city = {
            executor.submit(
                scrape_parse_save,
                scrape=functools.partial(fetch_weather, city.latitude, city.longitude),
                save_to=pathlib.Path("data/weather") / f"{city.name}.json"
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
