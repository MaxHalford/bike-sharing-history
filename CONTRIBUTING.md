# Contributing

Add or update bike-sharing systems in `scrape/systems.py`, then run the test suite before opening a pull request.

## Scheduled jobs

Railway runs the live station and weather scraper every 15 minutes. Its container and schedule are defined by `Dockerfile`, `railway.toml`, and `scripts/railway-scrape.sh`.

The live scraper workflow in `.github/workflows/scrape.yml` is a manual fallback and must not have a schedule.

GitHub Actions continues to run the monthly archive workflow in `.github/workflows/archive.yml`. It can also be started manually when an archive needs to be rebuilt.
