# bike-sharing-history

This repo tracks the status of bike stations from various bike-sharing providers. The data is fetched every 15 minutes. The results are stored and versioned as GeoJSON files. This is done using the [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) technique.

The weather forecast for the next 24 hours is also collected every 15 minutes, for each city.

Everyone is welcome to add new cities. You simply have to contribute the necessary details to `cities.py`, before sending a pull request.
