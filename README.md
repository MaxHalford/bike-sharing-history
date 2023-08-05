# bike-sharing-history

This repo tracks the status of bike stations from various bike-sharing providers. The data is fetched every 10 minutes. The results are stored and versioned as [GeoJSON](https://www.wikiwand.com/en/GeoJSON) files. This is done using the [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) technique.

The weather forecast for the next 24 hours is also collected every 10 minutes, for each city.

Everyone is welcome to add new cities. You simply have to contribute the necessary details to `cities.py`, before sending a pull request.

| Country | City | Provider | Stations (live) | Weather (live) |
|---------|------|----------|-----------------|----------------|
| 🇦🇪 | Dubai | Careem BIKE | [`dubai/careem-bike.geojson`](data/stations/dubai/careem-bike.geojson) | [`dubai.json`](data/weather/dubai.json) |
| 🇦🇺 | Brisbane | JCDecaux | [`brisbane/jcdecaux.geojson`](data/stations/brisbane/jcdecaux.geojson) | [`brisbane.json`](data/weather/brisbane.json) |
| 🇧🇪 | Brussels | JCDecaux | [`brussels/jcdecaux.geojson`](data/stations/brussels/jcdecaux.geojson) | [`brussels.json`](data/weather/brussels.json) |
| 🇧🇪 | Namur | JCDecaux | [`namur/jcdecaux.geojson`](data/stations/namur/jcdecaux.geojson) | [`namur.json`](data/weather/namur.json) |
| 🇧🇷 | Rio de Janeiro | Bike Itaú | [`rio-de-janeiro/bike-itau.geojson`](data/stations/rio-de-janeiro/bike-itau.geojson) | [`rio-de-janeiro.json`](data/weather/rio-de-janeiro.json) |
| 🇪🇸 | Santander | JCDecaux | [`santander/jcdecaux.geojson`](data/stations/santander/jcdecaux.geojson) | [`santander.json`](data/weather/santander.json) |
| 🇪🇸 | Sevilla | JCDecaux | [`sevilla/jcdecaux.geojson`](data/stations/sevilla/jcdecaux.geojson) | [`sevilla.json`](data/weather/sevilla.json) |
| 🇪🇸 | Valencia | JCDecaux | [`valencia/jcdecaux.geojson`](data/stations/valencia/jcdecaux.geojson) | [`valencia.json`](data/weather/valencia.json) |
| 🇫🇷 | Amiens | JCDecaux | [`amiens/jcdecaux.geojson`](data/stations/amiens/jcdecaux.geojson) | [`amiens.json`](data/weather/amiens.json) |
| 🇫🇷 | Besançon | JCDecaux | [`besancon/jcdecaux.geojson`](data/stations/besancon/jcdecaux.geojson) | [`besancon.json`](data/weather/besancon.json) |
| 🇫🇷 | Cergy-Pontoise | JCDecaux | [`cergy-pontoise/jcdecaux.geojson`](data/stations/cergy-pontoise/jcdecaux.geojson) | [`cergy-pontoise.json`](data/weather/cergy-pontoise.json) |
| 🇫🇷 | Créteil | JCDecaux | [`creteil/jcdecaux.geojson`](data/stations/creteil/jcdecaux.geojson) | [`creteil.json`](data/weather/creteil.json) |
| 🇫🇷 | Lyon | JCDecaux | [`lyon/jcdecaux.geojson`](data/stations/lyon/jcdecaux.geojson) | [`lyon.json`](data/weather/lyon.json) |
| 🇫🇷 | Marseille | JCDecaux | [`marseille/jcdecaux.geojson`](data/stations/marseille/jcdecaux.geojson) | [`marseille.json`](data/weather/marseille.json) |
| 🇫🇷 | Mulhouse | JCDecaux | [`mulhouse/jcdecaux.geojson`](data/stations/mulhouse/jcdecaux.geojson) | [`mulhouse.json`](data/weather/mulhouse.json) |
| 🇫🇷 | Nancy | JCDecaux | [`nancy/jcdecaux.geojson`](data/stations/nancy/jcdecaux.geojson) | [`nancy.json`](data/weather/nancy.json) |
| 🇫🇷 | Nantes | JCDecaux | [`nantes/jcdecaux.geojson`](data/stations/nantes/jcdecaux.geojson) | [`nantes.json`](data/weather/nantes.json) |
| 🇫🇷 | Rouen | JCDecaux | [`rouen/jcdecaux.geojson`](data/stations/rouen/jcdecaux.geojson) | [`rouen.json`](data/weather/rouen.json) |
| 🇫🇷 | Toulouse | JCDecaux | [`toulouse/jcdecaux.geojson`](data/stations/toulouse/jcdecaux.geojson) | [`toulouse.json`](data/weather/toulouse.json) |
| 🇮🇪 | Dublin | JCDecaux | [`dublin/jcdecaux.geojson`](data/stations/dublin/jcdecaux.geojson) | [`dublin.json`](data/weather/dublin.json) |
| 🇯🇵 | Toyama | JCDecaux | [`toyama/jcdecaux.geojson`](data/stations/toyama/jcdecaux.geojson) | [`toyama.json`](data/weather/toyama.json) |
| 🇱🇹 | Vilnius | JCDecaux | [`vilnius/jcdecaux.geojson`](data/stations/vilnius/jcdecaux.geojson) | [`vilnius.json`](data/weather/vilnius.json) |
| 🇱🇺 | Luxembourg | JCDecaux | [`luxembourg/jcdecaux.geojson`](data/stations/luxembourg/jcdecaux.geojson) | [`luxembourg.json`](data/weather/luxembourg.json) |
| 🇳🇴 | Lillestrøm | JCDecaux | [`lillestrom/jcdecaux.geojson`](data/stations/lillestrom/jcdecaux.geojson) | [`lillestrom.json`](data/weather/lillestrom.json) |
| 🇸🇪 | Lund | JCDecaux | [`lund/jcdecaux.geojson`](data/stations/lund/jcdecaux.geojson) | [`lund.json`](data/weather/lund.json) |
| 🇸🇪 | Stockholm | JCDecaux | [`stockholm/jcdecaux.geojson`](data/stations/stockholm/jcdecaux.geojson) | [`stockholm.json`](data/weather/stockholm.json) |
| 🇸🇮 | Ljubljana | JCDecaux | [`ljubljana/jcdecaux.geojson`](data/stations/ljubljana/jcdecaux.geojson) | [`ljubljana.json`](data/weather/ljubljana.json) |
| 🇸🇮 | Maribor | JCDecaux | [`maribor/jcdecaux.geojson`](data/stations/maribor/jcdecaux.geojson) | [`maribor.json`](data/weather/maribor.json) |
| 🇺🇸 | Boulder | BCycle | [`boulder/bcycle.geojson`](data/stations/boulder/bcycle.geojson) | [`boulder.json`](data/weather/boulder.json) |
| 🇺🇸 | Chattanooga | Bike Chattanooga | [`chattanooga/bike-chattanooga.geojson`](data/stations/chattanooga/bike-chattanooga.geojson) | [`chattanooga.json`](data/weather/chattanooga.json) |
