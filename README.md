# bike-sharing-history

This repo tracks the status of bike stations from various bike-sharing providers. The data is fetched every 15 minutes. The results are stored and versioned as [GeoJSON](https://www.wikiwand.com/en/GeoJSON) files. This is done using the [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) technique.

The weather forecast for the next 24 hours is also collected every 15 minutes, for each city.

Everyone is welcome to add new cities. You simply have to contribute the necessary details to `scripts/systems.py`, and then send out a pull request.

## Live data

| #   | Country | City                   | Provider         | Stations                                                                                               | Weather                                                                   |
| --- | ------- | ---------------------- | ---------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| 001 | 🇦🇪      | Dubai                  | Careem BIKE      | [`dubai/careem-bike.geojson`](data/stations/dubai/careem-bike.geojson)                                 | [`dubai.json`](data/weather/dubai.json)                                   |
| 002 | 🇦🇺      | Brisbane               | JCDecaux         | [`brisbane/jcdecaux.geojson`](data/stations/brisbane/jcdecaux.geojson)                                 | [`brisbane.json`](data/weather/brisbane.json)                             |
| 003 | 🇧🇪      | Brussels               | JCDecaux         | [`brussels/jcdecaux.geojson`](data/stations/brussels/jcdecaux.geojson)                                 | [`brussels.json`](data/weather/brussels.json)                             |
| 004 | 🇧🇪      | Namur                  | JCDecaux         | [`namur/jcdecaux.geojson`](data/stations/namur/jcdecaux.geojson)                                       | [`namur.json`](data/weather/namur.json)                                   |
| 005 | 🇧🇷      | Rio de Janeiro         | Bike Itaú        | [`rio-de-janeiro/bike-itau.geojson`](data/stations/rio-de-janeiro/bike-itau.geojson)                   | [`rio-de-janeiro.json`](data/weather/rio-de-janeiro.json)                 |
| 006 | 🇨🇦      | Vancouver              | Mobi Bike Share  | [`vancouver/mobi-bike-share.geojson`](data/stations/vancouver/mobi-bike-share.geojson)                 | [`vancouver.json`](data/weather/vancouver.json)                           |
| 007 | 🇪🇸      | Santander              | JCDecaux         | [`santander/jcdecaux.geojson`](data/stations/santander/jcdecaux.geojson)                               | [`santander.json`](data/weather/santander.json)                           |
| 008 | 🇪🇸      | Sevilla                | JCDecaux         | [`sevilla/jcdecaux.geojson`](data/stations/sevilla/jcdecaux.geojson)                                   | [`sevilla.json`](data/weather/sevilla.json)                               |
| 009 | 🇪🇸      | Valencia               | JCDecaux         | [`valencia/jcdecaux.geojson`](data/stations/valencia/jcdecaux.geojson)                                 | [`valencia.json`](data/weather/valencia.json)                             |
| 010 | 🇫🇷      | Amiens                 | JCDecaux         | [`amiens/jcdecaux.geojson`](data/stations/amiens/jcdecaux.geojson)                                     | [`amiens.json`](data/weather/amiens.json)                                 |
| 011 | 🇫🇷      | Belfort                | Optymo           | [`belfort/optymo.geojson`](data/stations/belfort/optymo.geojson)                                       | [`belfort.json`](data/weather/belfort.json)                               |
| 012 | 🇫🇷      | Besançon               | JCDecaux         | [`besancon/jcdecaux.geojson`](data/stations/besancon/jcdecaux.geojson)                                 | [`besancon.json`](data/weather/besancon.json)                             |
| 013 | 🇫🇷      | Bordeaux               | Bird             | [`bordeaux/bird.geojson`](data/stations/bordeaux/bird.geojson)                                         | [`bordeaux.json`](data/weather/bordeaux.json)                             |
| 014 | 🇫🇷      | Bordeaux               | VCub             | [`bordeaux/vcub.geojson`](data/stations/bordeaux/vcub.geojson)                                         | [`bordeaux.json`](data/weather/bordeaux.json)                             |
| 015 | 🇫🇷      | Brest                  | Donkey Republic  | [`brest/donkey-republic.geojson`](data/stations/brest/donkey-republic.geojson)                         | [`brest.json`](data/weather/brest.json)                                   |
| 016 | 🇫🇷      | Carcassonne            | Cyclolib         | [`carcassonne/cyclolib.geojson`](data/stations/carcassonne/cyclolib.geojson)                           | [`carcassonne.json`](data/weather/carcassonne.json)                       |
| 017 | 🇫🇷      | Cergy-Pontoise         | JCDecaux         | [`cergy-pontoise/jcdecaux.geojson`](data/stations/cergy-pontoise/jcdecaux.geojson)                     | [`cergy-pontoise.json`](data/weather/cergy-pontoise.json)                 |
| 018 | 🇫🇷      | Châlons-en-Champagne   | Bird             | [`chalons-en-champagne/bird.geojson`](data/stations/chalons-en-champagne/bird.geojson)                 | [`chalons-en-champagne.json`](data/weather/chalons-en-champagne.json)     |
| 019 | 🇫🇷      | Clermont-Ferrand       | C-Vélo           | [`clermont-ferrand/c-velo.geojson`](data/stations/clermont-ferrand/c-velo.geojson)                     | [`clermont-ferrand.json`](data/weather/clermont-ferrand.json)             |
| 020 | 🇫🇷      | Créteil                | JCDecaux         | [`creteil/jcdecaux.geojson`](data/stations/creteil/jcdecaux.geojson)                                   | [`creteil.json`](data/weather/creteil.json)                               |
| 021 | 🇫🇷      | Draguignan             | Bird             | [`draguignan/bird.geojson`](data/stations/draguignan/bird.geojson)                                     | [`draguignan.json`](data/weather/draguignan.json)                         |
| 022 | 🇫🇷      | La Roche-sur-Yon       | Bird             | [`la-roche-sur-yon/bird.geojson`](data/stations/la-roche-sur-yon/bird.geojson)                         | [`la-roche-sur-yon.json`](data/weather/la-roche-sur-yon.json)             |
| 023 | 🇫🇷      | Laval                  | Bird             | [`laval/bird.geojson`](data/stations/laval/bird.geojson)                                               | [`laval.json`](data/weather/laval.json)                                   |
| 024 | 🇫🇷      | Lille                  | V'lille          | [`lille/v-lille.geojson`](data/stations/lille/v-lille.geojson)                                         | [`lille.json`](data/weather/lille.json)                                   |
| 025 | 🇫🇷      | Lyon                   | JCDecaux         | [`lyon/jcdecaux.geojson`](data/stations/lyon/jcdecaux.geojson)                                         | [`lyon.json`](data/weather/lyon.json)                                     |
| 026 | 🇫🇷      | Marseille              | JCDecaux         | [`marseille/jcdecaux.geojson`](data/stations/marseille/jcdecaux.geojson)                               | [`marseille.json`](data/weather/marseille.json)                           |
| 027 | 🇫🇷      | Marseille              | Bird             | [`marseille/bird.geojson`](data/stations/marseille/bird.geojson)                                       | [`marseille.json`](data/weather/marseille.json)                           |
| 028 | 🇫🇷      | Marseille              | Lime             | [`marseille/lime.geojson`](data/stations/marseille/lime.geojson)                                       | [`marseille.json`](data/weather/marseille.json)                           |
| 029 | 🇫🇷      | Millau                 | Bird             | [`millau/bird.geojson`](data/stations/millau/bird.geojson)                                             | [`millau.json`](data/weather/millau.json)                                 |
| 030 | 🇫🇷      | Montluçon              | Bird             | [`montlucon/bird.geojson`](data/stations/montlucon/bird.geojson)                                       | [`montlucon.json`](data/weather/montlucon.json)                           |
| 031 | 🇫🇷      | Montpellier            | Vélomagg'        | [`montpellier/velomagg.geojson`](data/stations/montpellier/velomagg.geojson)                           | [`montpellier.json`](data/weather/montpellier.json)                       |
| 032 | 🇫🇷      | Mulhouse               | JCDecaux         | [`mulhouse/jcdecaux.geojson`](data/stations/mulhouse/jcdecaux.geojson)                                 | [`mulhouse.json`](data/weather/mulhouse.json)                             |
| 033 | 🇫🇷      | Nancy                  | JCDecaux         | [`nancy/jcdecaux.geojson`](data/stations/nancy/jcdecaux.geojson)                                       | [`nancy.json`](data/weather/nancy.json)                                   |
| 034 | 🇫🇷      | Nantes                 | JCDecaux         | [`nantes/jcdecaux.geojson`](data/stations/nantes/jcdecaux.geojson)                                     | [`nantes.json`](data/weather/nantes.json)                                 |
| 035 | 🇫🇷      | Paris                  | Lime             | [`paris/lime.geojson`](data/stations/paris/lime.geojson)                                               | [`paris.json`](data/weather/paris.json)                                   |
| 036 | 🇫🇷      | Paris                  | Smovengo         | [`paris/smovengo.geojson`](data/stations/paris/smovengo.geojson)                                       | [`paris.json`](data/weather/paris.json)                                   |
| 037 | 🇫🇷      | Rouen                  | JCDecaux         | [`rouen/jcdecaux.geojson`](data/stations/rouen/jcdecaux.geojson)                                       | [`rouen.json`](data/weather/rouen.json)                                   |
| 038 | 🇫🇷      | Saint-Etienne          | Vélivert         | [`saint-etienne/velivert.geojson`](data/stations/saint-etienne/velivert.geojson)                       | [`saint-etienne.json`](data/weather/saint-etienne.json)                   |
| 039 | 🇫🇷      | Sarreguemines          | Bird             | [`sarreguemines/bird.geojson`](data/stations/sarreguemines/bird.geojson)                               | [`sarreguemines.json`](data/weather/sarreguemines.json)                   |
| 040 | 🇫🇷      | Toulouse               | JCDecaux         | [`toulouse/jcdecaux.geojson`](data/stations/toulouse/jcdecaux.geojson)                                 | [`toulouse.json`](data/weather/toulouse.json)                             |
| 041 | 🇫🇷      | Valenciennes           | Donkey Republic  | [`valenciennes/donkey-republic.geojson`](data/stations/valenciennes/donkey-republic.geojson)           | [`valenciennes.json`](data/weather/valenciennes.json)                     |
| 042 | 🇫🇷      | Vannes                 | Vélocéo          | [`vannes/veloceo.geojson`](data/stations/vannes/veloceo.geojson)                                       | [`vannes.json`](data/weather/vannes.json)                                 |
| 043 | 🇫🇷      | Vichy                  | Bird             | [`vichy/bird.geojson`](data/stations/vichy/bird.geojson)                                               | [`vichy.json`](data/weather/vichy.json)                                   |
| 044 | 🇮🇪      | Dublin                 | JCDecaux         | [`dublin/jcdecaux.geojson`](data/stations/dublin/jcdecaux.geojson)                                     | [`dublin.json`](data/weather/dublin.json)                                 |
| 045 | 🇯🇵      | Toyama                 | JCDecaux         | [`toyama/jcdecaux.geojson`](data/stations/toyama/jcdecaux.geojson)                                     | [`toyama.json`](data/weather/toyama.json)                                 |
| 046 | 🇱🇹      | Vilnius                | JCDecaux         | [`vilnius/jcdecaux.geojson`](data/stations/vilnius/jcdecaux.geojson)                                   | [`vilnius.json`](data/weather/vilnius.json)                               |
| 047 | 🇱🇺      | Luxembourg             | JCDecaux         | [`luxembourg/jcdecaux.geojson`](data/stations/luxembourg/jcdecaux.geojson)                             | [`luxembourg.json`](data/weather/luxembourg.json)                         |
| 048 | 🇳🇴      | Lillestrøm             | JCDecaux         | [`lillestrom/jcdecaux.geojson`](data/stations/lillestrom/jcdecaux.geojson)                             | [`lillestrom.json`](data/weather/lillestrom.json)                         |
| 049 | 🇸🇪      | Lund                   | JCDecaux         | [`lund/jcdecaux.geojson`](data/stations/lund/jcdecaux.geojson)                                         | [`lund.json`](data/weather/lund.json)                                     |
| 050 | 🇸🇪      | Stockholm              | JCDecaux         | [`stockholm/jcdecaux.geojson`](data/stations/stockholm/jcdecaux.geojson)                               | [`stockholm.json`](data/weather/stockholm.json)                           |
| 051 | 🇸🇮      | Ljubljana              | JCDecaux         | [`ljubljana/jcdecaux.geojson`](data/stations/ljubljana/jcdecaux.geojson)                               | [`ljubljana.json`](data/weather/ljubljana.json)                           |
| 052 | 🇸🇮      | Maribor                | JCDecaux         | [`maribor/jcdecaux.geojson`](data/stations/maribor/jcdecaux.geojson)                                   | [`maribor.json`](data/weather/maribor.json)                               |
| 053 | 🇺🇸      | Boulder                | BCycle           | [`boulder/bcycle.geojson`](data/stations/boulder/bcycle.geojson)                                       | [`boulder.json`](data/weather/boulder.json)                               |
| 054 | 🇺🇸      | Chattanooga            | Bike Chattanooga | [`chattanooga/bike-chattanooga.geojson`](data/stations/chattanooga/bike-chattanooga.geojson)           | [`chattanooga.json`](data/weather/chattanooga.json)                       |
| 055 | 🇺🇸      | San Francisco Bay Area | Bay Wheels       | [`san-francisco-bay-area/bay-wheels.geojson`](data/stations/san-francisco-bay-area/bay-wheels.geojson) | [`san-francisco-bay-area.json`](data/weather/san-francisco-bay-area.json) |

## Archives

The git history contains the state of each station and weather at several points in time. This git history can be turned into Parquet files for easy consumption. This is done by `archive.py` script. The latter generates Parquet files. These files are stored in a GCP bucket, [here](https://console.cloud.google.com/storage/browser?forceOnBucketsSortingFiltering=true&project=bike-sharing-407017&prefix=&forceOnObjectsSortingFiltering=false).

An easy way to query these files is to use [DuckDB](https://duckdb.org/). The following Python snippet shows how to fetch the all bike station updates for the city of Toulouse:

```py
import duckdb

with duckdb.connect(":memory:") as con:
    con.execute("SET s3_endpoint='storage.googleapis.com'")
    updates = con.execute(f"""
    SELECT *
    FROM READ_PARQUET('s3://bike-sharing-history/toulouse/jcdecaux/*/*.parquet');
    """).fetch_df()
```

And here's a snippet to fetch the 24 hour weather forecast at different points in time for the city of Toulouse:

```py
with duckdb.connect(":memory:") as con:
    con.execute("SET s3_endpoint='storage.googleapis.com'")
    weather = con.execute(f"""
    SELECT *
    FROM READ_PARQUET('s3://weather-forecast-history/toulouse/*/*.parquet');
    """).fetch_df()
```

If these exports are not adapted to your needs, feel welcome to reach out. The exports can be easily adapted to different needs, because the source of truth is the git history.
