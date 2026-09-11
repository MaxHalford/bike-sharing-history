# Contributing

Add or update bike-sharing systems in `scrape/systems.py`, then run the test suite before opening a pull request.

## Scheduled jobs

Railway scrapes live station data every 12 minutes and weather data hourly. The container is defined by `Dockerfile` and `scripts/railway-scrape.sh`; the live Railway cron is `1,13,25,37,49 * * * *` and is mirrored in `railway.toml`.

The live scraper workflow in `.github/workflows/scrape.yml` is a manual fallback and must not have a schedule.

GitHub Actions continues to run the monthly archive workflow in `.github/workflows/archive.yml`. It can also be started manually when an archive needs to be rebuilt.
