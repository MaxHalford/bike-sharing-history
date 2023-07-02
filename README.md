# bike-sharing-history

This repo tracks the status of bike stations from various bike-sharing providers. The data is fetched every 15 minutes. The results are stored and versioned as [GeoJSON](https://www.wikiwand.com/en/GeoJSON) files. This is done using the [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) technique.

The weather forecast for the next 24 hours is also collected every 15 minutes, for each city.

Everyone is welcome to add new cities. You simply have to contribute the necessary details to `cities.py`, before sending a pull request.

| Country | Name | Live |
|---------|------|------|
| 🇦🇪 | dubai | [`dubai.geojson`](data/stations/dubai.geojson) |
| 🇦🇺 | brisbane | [`brisbane.geojson`](data/stations/brisbane.geojson) |
| 🇧🇪 | bruxelles | [`bruxelles.geojson`](data/stations/bruxelles.geojson) |
| 🇧🇪 | namur | [`namur.geojson`](data/stations/namur.geojson) |
| 🇧🇷 | rio-de-janeiro | [`rio-de-janeiro.geojson`](data/stations/rio-de-janeiro.geojson) |
| 🇪🇸 | santander | [`santander.geojson`](data/stations/santander.geojson) |
| 🇪🇸 | seville | [`seville.geojson`](data/stations/seville.geojson) |
| 🇪🇸 | valence | [`valence.geojson`](data/stations/valence.geojson) |
| 🇫🇷 | amiens | [`amiens.geojson`](data/stations/amiens.geojson) |
| 🇫🇷 | besancon | [`besancon.geojson`](data/stations/besancon.geojson) |
| 🇫🇷 | cergy-pontoise | [`cergy-pontoise.geojson`](data/stations/cergy-pontoise.geojson) |
| 🇫🇷 | creteil | [`creteil.geojson`](data/stations/creteil.geojson) |
| 🇫🇷 | lyon | [`lyon.geojson`](data/stations/lyon.geojson) |
| 🇫🇷 | marseille | [`marseille.geojson`](data/stations/marseille.geojson) |
| 🇫🇷 | mulhouse | [`mulhouse.geojson`](data/stations/mulhouse.geojson) |
| 🇫🇷 | nancy | [`nancy.geojson`](data/stations/nancy.geojson) |
| 🇫🇷 | nantes | [`nantes.geojson`](data/stations/nantes.geojson) |
| 🇫🇷 | rouen | [`rouen.geojson`](data/stations/rouen.geojson) |
| 🇫🇷 | toulouse | [`toulouse.geojson`](data/stations/toulouse.geojson) |
| 🇮🇪 | dublin | [`dublin.geojson`](data/stations/dublin.geojson) |
| 🇯🇵 | toyama | [`toyama.geojson`](data/stations/toyama.geojson) |
| 🇱🇹 | vilnius | [`vilnius.geojson`](data/stations/vilnius.geojson) |
| 🇱🇺 | luxembourg | [`luxembourg.geojson`](data/stations/luxembourg.geojson) |
| 🇳🇴 | lillestrom | [`lillestrom.geojson`](data/stations/lillestrom.geojson) |
| 🇸🇪 | lund | [`lund.geojson`](data/stations/lund.geojson) |
| 🇸🇪 | stockholm | [`stockholm.geojson`](data/stations/stockholm.geojson) |
| 🇸🇮 | ljubljana | [`ljubljana.geojson`](data/stations/ljubljana.geojson) |
| 🇸🇮 | maribor | [`maribor.geojson`](data/stations/maribor.geojson) |
| 🇺🇸 | boulder | [`boulder.geojson`](data/stations/boulder.geojson) |
| 🇺🇸 | chattanooga | [`chattanooga.geojson`](data/stations/chattanooga.geojson) |
