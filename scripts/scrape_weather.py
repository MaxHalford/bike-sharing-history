import concurrent.futures
import functools
import json
import logging
import pathlib
import re
import unicodedata

import requests

from systems import systems

def slugify(text, separator='-'):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[%s\s]+' % separator, separator, text)


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
                scrape=functools.partial(fetch_weather, system.latitude, system.longitude),
                save_to=pathlib.Path("data/weather") / f"{slugify(system.city)}.json",
            ): system.city
            for system in systems
        }

    n_exceptions = 0
    for future in concurrent.futures.as_completed(future_to_city):
        city = future_to_city[future]
        try:
            future.result()
            logging.info(f"✅ {city}")
        except Exception as exc:
            logging.exception(f"❌ {city} {exc}")
            n_exceptions += 1
    if n_exceptions:
        logging.warning(f"⚠️ {n_exceptions:,d} exceptions out of {len(systems):,d}")


if __name__ == "__main__":
    main()
