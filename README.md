# bike-sharing-history

This repo tracks the status of bike stations from various bike-sharing providers. The data is fetched every 10 minutes. The results are stored and versioned as [GeoJSON](https://www.wikiwand.com/en/GeoJSON) files. This is done using the [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) technique.

The weather forecast for the next 24 hours is also collected every 10 minutes, for each city.

Everyone is welcome to add new cities. You simply have to contribute the necessary details to `cities.py`, before sending a pull request.

| Country | Name           | Stations (live)                                                  | Weather (live)                                            |
| ------- | -------------- | ---------------------------------------------------------------- | --------------------------------------------------------- |
| 🇦🇪      | dubai          | [`dubai.geojson`](data/stations/dubai.geojson)                   | [`dubai.json`](data/weather/dubai.json)                   |
| 🇦🇺      | brisbane       | [`brisbane.geojson`](data/stations/brisbane.geojson)             | [`brisbane.json`](data/weather/brisbane.json)             |
| 🇧🇪      | bruxelles      | [`bruxelles.geojson`](data/stations/bruxelles.geojson)           | [`bruxelles.json`](data/weather/bruxelles.json)           |
| 🇧🇪      | namur          | [`namur.geojson`](data/stations/namur.geojson)                   | [`namur.json`](data/weather/namur.json)                   |
| 🇧🇷      | rio-de-janeiro | [`rio-de-janeiro.geojson`](data/stations/rio-de-janeiro.geojson) | [`rio-de-janeiro.json`](data/weather/rio-de-janeiro.json) |
| 🇪🇸      | santander      | [`santander.geojson`](data/stations/santander.geojson)           | [`santander.json`](data/weather/santander.json)           |
| 🇪🇸      | seville        | [`seville.geojson`](data/stations/seville.geojson)               | [`seville.json`](data/weather/seville.json)               |
| 🇪🇸      | valence        | [`valence.geojson`](data/stations/valence.geojson)               | [`valence.json`](data/weather/valence.json)               |
| 🇫🇷      | amiens         | [`amiens.geojson`](data/stations/amiens.geojson)                 | [`amiens.json`](data/weather/amiens.json)                 |
| 🇫🇷      | besancon       | [`besancon.geojson`](data/stations/besancon.geojson)             | [`besancon.json`](data/weather/besancon.json)             |
| 🇫🇷      | cergy-pontoise | [`cergy-pontoise.geojson`](data/stations/cergy-pontoise.geojson) | [`cergy-pontoise.json`](data/weather/cergy-pontoise.json) |
| 🇫🇷      | creteil        | [`creteil.geojson`](data/stations/creteil.geojson)               | [`creteil.json`](data/weather/creteil.json)               |
| 🇫🇷      | lyon           | [`lyon.geojson`](data/stations/lyon.geojson)                     | [`lyon.json`](data/weather/lyon.json)                     |
| 🇫🇷      | marseille      | [`marseille.geojson`](data/stations/marseille.geojson)           | [`marseille.json`](data/weather/marseille.json)           |
| 🇫🇷      | mulhouse       | [`mulhouse.geojson`](data/stations/mulhouse.geojson)             | [`mulhouse.json`](data/weather/mulhouse.json)             |
| 🇫🇷      | nancy          | [`nancy.geojson`](data/stations/nancy.geojson)                   | [`nancy.json`](data/weather/nancy.json)                   |
| 🇫🇷      | nantes         | [`nantes.geojson`](data/stations/nantes.geojson)                 | [`nantes.json`](data/weather/nantes.json)                 |
| 🇫🇷      | rouen          | [`rouen.geojson`](data/stations/rouen.geojson)                   | [`rouen.json`](data/weather/rouen.json)                   |
| 🇫🇷      | toulouse       | [`toulouse.geojson`](data/stations/toulouse.geojson)             | [`toulouse.json`](data/weather/toulouse.json)             |
| 🇮🇪      | dublin         | [`dublin.geojson`](data/stations/dublin.geojson)                 | [`dublin.json`](data/weather/dublin.json)                 |
| 🇯🇵      | toyama         | [`toyama.geojson`](data/stations/toyama.geojson)                 | [`toyama.json`](data/weather/toyama.json)                 |
| 🇱🇹      | vilnius        | [`vilnius.geojson`](data/stations/vilnius.geojson)               | [`vilnius.json`](data/weather/vilnius.json)               |
| 🇱🇺      | luxembourg     | [`luxembourg.geojson`](data/stations/luxembourg.geojson)         | [`luxembourg.json`](data/weather/luxembourg.json)         |
| 🇳🇴      | lillestrom     | [`lillestrom.geojson`](data/stations/lillestrom.geojson)         | [`lillestrom.json`](data/weather/lillestrom.json)         |
| 🇸🇪      | lund           | [`lund.geojson`](data/stations/lund.geojson)                     | [`lund.json`](data/weather/lund.json)                     |
| 🇸🇪      | stockholm      | [`stockholm.geojson`](data/stations/stockholm.geojson)           | [`stockholm.json`](data/weather/stockholm.json)           |
| 🇸🇮      | ljubljana      | [`ljubljana.geojson`](data/stations/ljubljana.geojson)           | [`ljubljana.json`](data/weather/ljubljana.json)           |
| 🇸🇮      | maribor        | [`maribor.geojson`](data/stations/maribor.geojson)               | [`maribor.json`](data/weather/maribor.json)               |
| 🇺🇸      | boulder        | [`boulder.geojson`](data/stations/boulder.geojson)               | [`boulder.json`](data/weather/boulder.json)               |
| 🇺🇸      | chattanooga    | [`chattanooga.geojson`](data/stations/chattanooga.geojson)       | [`chattanooga.json`](data/weather/chattanooga.json)       |
