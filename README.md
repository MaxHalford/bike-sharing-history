# bike-sharing-history

This repo tracks the status of bike stations from various bike-sharing providers. The data is fetched every 15 minutes. The results are stored and versioned as [GeoJSON](https://www.wikiwand.com/en/GeoJSON) files. This is done using the [git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) technique.

The weather forecast for the next 24 hours is also collected every 15 minutes, for each city.

Everyone is welcome to add new cities. You simply have to contribute the necessary details to [`scripts/systems.py`](scripts/systems.py), and then send out a pull request.

## Live data

| # | Country | City | Provider | Stations | Weather |
|---|---------|------|----------|----------|---------|
| 001 | 🇦🇪 | Dubai | Careem BIKE | [`dubai/careem-bike.geojson`](data/stations/dubai/careem-bike.geojson) | [`dubai.json`](data/weather/dubai.json) |
| 002 | 🇦🇷 | Buenos Aires | Ecobici | [`buenos-aires/ecobici.geojson`](data/stations/buenos-aires/ecobici.geojson) | [`buenos-aires.json`](data/weather/buenos-aires.json) |
| 003 | 🇦🇹 | Vienna | Nextbike | [`vienna/nextbike.geojson`](data/stations/vienna/nextbike.geojson) | [`vienna.json`](data/weather/vienna.json) |
| 004 | 🇦🇺 | Brisbane | JCDecaux | [`brisbane/jcdecaux.geojson`](data/stations/brisbane/jcdecaux.geojson) | [`brisbane.json`](data/weather/brisbane.json) |
| 005 | 🇧🇪 | Antwerp | Blue-bike | [`antwerp/blue-bike.geojson`](data/stations/antwerp/blue-bike.geojson) | [`antwerp.json`](data/weather/antwerp.json) |
| 006 | 🇧🇪 | Antwerp | Velo Antwerpen | [`antwerp/velo-antwerpen.geojson`](data/stations/antwerp/velo-antwerpen.geojson) | [`antwerp.json`](data/weather/antwerp.json) |
| 007 | 🇧🇪 | Brussels | JCDecaux | [`brussels/jcdecaux.geojson`](data/stations/brussels/jcdecaux.geojson) | [`brussels.json`](data/weather/brussels.json) |
| 008 | 🇧🇪 | Namur | JCDecaux | [`namur/jcdecaux.geojson`](data/stations/namur/jcdecaux.geojson) | [`namur.json`](data/weather/namur.json) |
| 009 | 🇧🇷 | Porto Alegre | Bike Itaú | [`porto-alegre/bike-itau.geojson`](data/stations/porto-alegre/bike-itau.geojson) | [`porto-alegre.json`](data/weather/porto-alegre.json) |
| 010 | 🇧🇷 | Rio de Janeiro | Bike Itaú | [`rio-de-janeiro/bike-itau.geojson`](data/stations/rio-de-janeiro/bike-itau.geojson) | [`rio-de-janeiro.json`](data/weather/rio-de-janeiro.json) |
| 011 | 🇧🇷 | Salvador | Bike Itaú | [`salvador/bike-itau.geojson`](data/stations/salvador/bike-itau.geojson) | [`salvador.json`](data/weather/salvador.json) |
| 012 | 🇧🇷 | Sampa | Bike Itaú | [`sampa/bike-itau.geojson`](data/stations/sampa/bike-itau.geojson) | [`sampa.json`](data/weather/sampa.json) |
| 013 | 🇨🇦 | Montréal | BIXI | [`montreal/bixi.geojson`](data/stations/montreal/bixi.geojson) | [`montreal.json`](data/weather/montreal.json) |
| 014 | 🇨🇦 | Québec City | àVélo | [`quebec-city/avelo.geojson`](data/stations/quebec-city/avelo.geojson) | [`quebec-city.json`](data/weather/quebec-city.json) |
| 015 | 🇨🇦 | Toronto | Bike Share Toronto | [`toronto/bike-share-toronto.geojson`](data/stations/toronto/bike-share-toronto.geojson) | [`toronto.json`](data/weather/toronto.json) |
| 016 | 🇨🇦 | Vancouver | Mobi Bike Share | [`vancouver/mobi-bike-share.geojson`](data/stations/vancouver/mobi-bike-share.geojson) | [`vancouver.json`](data/weather/vancouver.json) |
| 017 | 🇨🇴 | Bogotá | Tembici | [`bogota/tembici.geojson`](data/stations/bogota/tembici.geojson) | [`bogota.json`](data/weather/bogota.json) |
| 018 | 🇨🇿 | Brno | Nextbike | [`brno/nextbike.geojson`](data/stations/brno/nextbike.geojson) | [`brno.json`](data/weather/brno.json) |
| 019 | 🇨🇿 | Olomouc | Nextbike | [`olomouc/nextbike.geojson`](data/stations/olomouc/nextbike.geojson) | [`olomouc.json`](data/weather/olomouc.json) |
| 020 | 🇨🇿 | Ostrava | Nextbike | [`ostrava/nextbike.geojson`](data/stations/ostrava/nextbike.geojson) | [`ostrava.json`](data/weather/ostrava.json) |
| 021 | 🇨🇿 | Prague | Nextbike | [`prague/nextbike.geojson`](data/stations/prague/nextbike.geojson) | [`prague.json`](data/weather/prague.json) |
| 022 | 🇩🇪 | Berlin | Nextbike | [`berlin/nextbike.geojson`](data/stations/berlin/nextbike.geojson) | [`berlin.json`](data/weather/berlin.json) |
| 023 | 🇩🇪 | Düsseldorf | Nextbike | [`dusseldorf/nextbike.geojson`](data/stations/dusseldorf/nextbike.geojson) | [`dusseldorf.json`](data/weather/dusseldorf.json) |
| 024 | 🇩🇪 | Frankfurt | Nextbike | [`frankfurt/nextbike.geojson`](data/stations/frankfurt/nextbike.geojson) | [`frankfurt.json`](data/weather/frankfurt.json) |
| 025 | 🇩🇪 | Freiburg | Frelo Freiburg | [`freiburg/frelo-freiburg.geojson`](data/stations/freiburg/frelo-freiburg.geojson) | [`freiburg.json`](data/weather/freiburg.json) |
| 026 | 🇩🇪 | Leipzig | Nextbike | [`leipzig/nextbike.geojson`](data/stations/leipzig/nextbike.geojson) | [`leipzig.json`](data/weather/leipzig.json) |
| 027 | 🇪🇸 | Barcelona | Bicing | [`barcelona/bicing.geojson`](data/stations/barcelona/bicing.geojson) | [`barcelona.json`](data/weather/barcelona.json) |
| 028 | 🇪🇸 | Madrid | bicimad | [`madrid/bicimad.geojson`](data/stations/madrid/bicimad.geojson) | [`madrid.json`](data/weather/madrid.json) |
| 029 | 🇪🇸 | Santander | JCDecaux | [`santander/jcdecaux.geojson`](data/stations/santander/jcdecaux.geojson) | [`santander.json`](data/weather/santander.json) |
| 030 | 🇪🇸 | Sevilla | JCDecaux | [`sevilla/jcdecaux.geojson`](data/stations/sevilla/jcdecaux.geojson) | [`sevilla.json`](data/weather/sevilla.json) |
| 031 | 🇪🇸 | Valencia | JCDecaux | [`valencia/jcdecaux.geojson`](data/stations/valencia/jcdecaux.geojson) | [`valencia.json`](data/weather/valencia.json) |
| 032 | 🇫🇷 | Amiens | JCDecaux | [`amiens/jcdecaux.geojson`](data/stations/amiens/jcdecaux.geojson) | [`amiens.json`](data/weather/amiens.json) |
| 033 | 🇫🇷 | Besançon | JCDecaux | [`besancon/jcdecaux.geojson`](data/stations/besancon/jcdecaux.geojson) | [`besancon.json`](data/weather/besancon.json) |
| 034 | 🇫🇷 | Bordeaux | Bird | [`bordeaux/bird.geojson`](data/stations/bordeaux/bird.geojson) | [`bordeaux.json`](data/weather/bordeaux.json) |
| 035 | 🇫🇷 | Brest | Donkey Republic | [`brest/donkey-republic.geojson`](data/stations/brest/donkey-republic.geojson) | [`brest.json`](data/weather/brest.json) |
| 036 | 🇫🇷 | Cergy-Pontoise | JCDecaux | [`cergy-pontoise/jcdecaux.geojson`](data/stations/cergy-pontoise/jcdecaux.geojson) | [`cergy-pontoise.json`](data/weather/cergy-pontoise.json) |
| 037 | 🇫🇷 | Châlons-en-Champagne | Bird | [`chalons-en-champagne/bird.geojson`](data/stations/chalons-en-champagne/bird.geojson) | [`chalons-en-champagne.json`](data/weather/chalons-en-champagne.json) |
| 038 | 🇫🇷 | Clermont-Ferrand | C-Vélo | [`clermont-ferrand/c-velo.geojson`](data/stations/clermont-ferrand/c-velo.geojson) | [`clermont-ferrand.json`](data/weather/clermont-ferrand.json) |
| 039 | 🇫🇷 | Créteil | JCDecaux | [`creteil/jcdecaux.geojson`](data/stations/creteil/jcdecaux.geojson) | [`creteil.json`](data/weather/creteil.json) |
| 040 | 🇫🇷 | Draguignan | Bird | [`draguignan/bird.geojson`](data/stations/draguignan/bird.geojson) | [`draguignan.json`](data/weather/draguignan.json) |
| 041 | 🇫🇷 | La Roche-sur-Yon | Bird | [`la-roche-sur-yon/bird.geojson`](data/stations/la-roche-sur-yon/bird.geojson) | [`la-roche-sur-yon.json`](data/weather/la-roche-sur-yon.json) |
| 042 | 🇫🇷 | Laval | Bird | [`laval/bird.geojson`](data/stations/laval/bird.geojson) | [`laval.json`](data/weather/laval.json) |
| 043 | 🇫🇷 | Lyon | JCDecaux | [`lyon/jcdecaux.geojson`](data/stations/lyon/jcdecaux.geojson) | [`lyon.json`](data/weather/lyon.json) |
| 044 | 🇫🇷 | Marseille | JCDecaux | [`marseille/jcdecaux.geojson`](data/stations/marseille/jcdecaux.geojson) | [`marseille.json`](data/weather/marseille.json) |
| 045 | 🇫🇷 | Marseille | Bird | [`marseille/bird.geojson`](data/stations/marseille/bird.geojson) | [`marseille.json`](data/weather/marseille.json) |
| 046 | 🇫🇷 | Marseille | Lime | [`marseille/lime.geojson`](data/stations/marseille/lime.geojson) | [`marseille.json`](data/weather/marseille.json) |
| 047 | 🇫🇷 | Millau | Bird | [`millau/bird.geojson`](data/stations/millau/bird.geojson) | [`millau.json`](data/weather/millau.json) |
| 048 | 🇫🇷 | Montluçon | Bird | [`montlucon/bird.geojson`](data/stations/montlucon/bird.geojson) | [`montlucon.json`](data/weather/montlucon.json) |
| 049 | 🇫🇷 | Mulhouse | JCDecaux | [`mulhouse/jcdecaux.geojson`](data/stations/mulhouse/jcdecaux.geojson) | [`mulhouse.json`](data/weather/mulhouse.json) |
| 050 | 🇫🇷 | Nancy | JCDecaux | [`nancy/jcdecaux.geojson`](data/stations/nancy/jcdecaux.geojson) | [`nancy.json`](data/weather/nancy.json) |
| 051 | 🇫🇷 | Nantes | JCDecaux | [`nantes/jcdecaux.geojson`](data/stations/nantes/jcdecaux.geojson) | [`nantes.json`](data/weather/nantes.json) |
| 052 | 🇫🇷 | Paris | Lime | [`paris/lime.geojson`](data/stations/paris/lime.geojson) | [`paris.json`](data/weather/paris.json) |
| 053 | 🇫🇷 | Paris | Smovengo | [`paris/smovengo.geojson`](data/stations/paris/smovengo.geojson) | [`paris.json`](data/weather/paris.json) |
| 054 | 🇫🇷 | Rouen | JCDecaux | [`rouen/jcdecaux.geojson`](data/stations/rouen/jcdecaux.geojson) | [`rouen.json`](data/weather/rouen.json) |
| 055 | 🇫🇷 | Sarreguemines | Bird | [`sarreguemines/bird.geojson`](data/stations/sarreguemines/bird.geojson) | [`sarreguemines.json`](data/weather/sarreguemines.json) |
| 056 | 🇫🇷 | Toulouse | JCDecaux | [`toulouse/jcdecaux.geojson`](data/stations/toulouse/jcdecaux.geojson) | [`toulouse.json`](data/weather/toulouse.json) |
| 057 | 🇫🇷 | Valenciennes | Donkey Republic | [`valenciennes/donkey-republic.geojson`](data/stations/valenciennes/donkey-republic.geojson) | [`valenciennes.json`](data/weather/valenciennes.json) |
| 058 | 🇫🇷 | Vichy | Bird | [`vichy/bird.geojson`](data/stations/vichy/bird.geojson) | [`vichy.json`](data/weather/vichy.json) |
| 059 | 🇭🇺 | Budapest | MOL Bubi | [`budapest/mol-bubi.geojson`](data/stations/budapest/mol-bubi.geojson) | [`budapest.json`](data/weather/budapest.json) |
| 060 | 🇮🇪 | Dublin | JCDecaux | [`dublin/jcdecaux.geojson`](data/stations/dublin/jcdecaux.geojson) | [`dublin.json`](data/weather/dublin.json) |
| 061 | 🇮🇹 | Milan | Bikemi | [`milan/bikemi.geojson`](data/stations/milan/bikemi.geojson) | [`milan.json`](data/weather/milan.json) |
| 062 | 🇯🇵 | Tokyo | Docomo Bike Sharing | [`tokyo/docomo-bike-sharing.geojson`](data/stations/tokyo/docomo-bike-sharing.geojson) | [`tokyo.json`](data/weather/tokyo.json) |
| 063 | 🇯🇵 | Toyama | JCDecaux | [`toyama/jcdecaux.geojson`](data/stations/toyama/jcdecaux.geojson) | [`toyama.json`](data/weather/toyama.json) |
| 064 | 🇱🇹 | Vilnius | JCDecaux | [`vilnius/jcdecaux.geojson`](data/stations/vilnius/jcdecaux.geojson) | [`vilnius.json`](data/weather/vilnius.json) |
| 065 | 🇱🇺 | Luxembourg | JCDecaux | [`luxembourg/jcdecaux.geojson`](data/stations/luxembourg/jcdecaux.geojson) | [`luxembourg.json`](data/weather/luxembourg.json) |
| 066 | 🇲🇽 | Guadalajara | Mibici | [`guadalajara/mibici.geojson`](data/stations/guadalajara/mibici.geojson) | [`guadalajara.json`](data/weather/guadalajara.json) |
| 067 | 🇲🇽 | Mexico City | Ecobici | [`mexico-city/ecobici.geojson`](data/stations/mexico-city/ecobici.geojson) | [`mexico-city.json`](data/weather/mexico-city.json) |
| 068 | 🇳🇴 | Bergen | Bergen Bysykkel | [`bergen/bergen-bysykkel.geojson`](data/stations/bergen/bergen-bysykkel.geojson) | [`bergen.json`](data/weather/bergen.json) |
| 069 | 🇳🇴 | Lillestrøm | JCDecaux | [`lillestrom/jcdecaux.geojson`](data/stations/lillestrom/jcdecaux.geojson) | [`lillestrom.json`](data/weather/lillestrom.json) |
| 070 | 🇳🇴 | Oslo | Oslo Bysykkel | [`oslo/oslo-bysykkel.geojson`](data/stations/oslo/oslo-bysykkel.geojson) | [`oslo.json`](data/weather/oslo.json) |
| 071 | 🇳🇴 | Stavanger | Kolumbus Bysykkel | [`stavanger/kolumbus-bysykkel.geojson`](data/stations/stavanger/kolumbus-bysykkel.geojson) | [`stavanger.json`](data/weather/stavanger.json) |
| 072 | 🇸🇪 | Gothenburg | Styr & Ställ | [`gothenburg/styr--stall.geojson`](data/stations/gothenburg/styr--stall.geojson) | [`gothenburg.json`](data/weather/gothenburg.json) |
| 073 | 🇸🇪 | Lund | JCDecaux | [`lund/jcdecaux.geojson`](data/stations/lund/jcdecaux.geojson) | [`lund.json`](data/weather/lund.json) |
| 074 | 🇸🇪 | Stockholm | JCDecaux | [`stockholm/jcdecaux.geojson`](data/stations/stockholm/jcdecaux.geojson) | [`stockholm.json`](data/weather/stockholm.json) |
| 075 | 🇸🇮 | Ljubljana | JCDecaux | [`ljubljana/jcdecaux.geojson`](data/stations/ljubljana/jcdecaux.geojson) | [`ljubljana.json`](data/weather/ljubljana.json) |
| 076 | 🇸🇮 | Maribor | JCDecaux | [`maribor/jcdecaux.geojson`](data/stations/maribor/jcdecaux.geojson) | [`maribor.json`](data/weather/maribor.json) |
| 077 | 🇺🇸 | Boulder | BCycle | [`boulder/bcycle.geojson`](data/stations/boulder/bcycle.geojson) | [`boulder.json`](data/weather/boulder.json) |
| 078 | 🇺🇸 | Chattanooga | Bike Chattanooga | [`chattanooga/bike-chattanooga.geojson`](data/stations/chattanooga/bike-chattanooga.geojson) | [`chattanooga.json`](data/weather/chattanooga.json) |
| 079 | 🇺🇸 | Chicago | Divvy | [`chicago/divvy.geojson`](data/stations/chicago/divvy.geojson) | [`chicago.json`](data/weather/chicago.json) |
| 080 | 🇺🇸 | Honolulu | Biki | [`honolulu/biki.geojson`](data/stations/honolulu/biki.geojson) | [`honolulu.json`](data/weather/honolulu.json) |
| 081 | 🇺🇸 | Milwaukee | Bublr Bikes | [`milwaukee/bublr-bikes.geojson`](data/stations/milwaukee/bublr-bikes.geojson) | [`milwaukee.json`](data/weather/milwaukee.json) |
| 082 | 🇺🇸 | New York City | citibike | [`new-york-city/citibike.geojson`](data/stations/new-york-city/citibike.geojson) | [`new-york-city.json`](data/weather/new-york-city.json) |
| 083 | 🇺🇸 | Philadelphia | Indego | [`philadelphia/indego.geojson`](data/stations/philadelphia/indego.geojson) | [`philadelphia.json`](data/weather/philadelphia.json) |
| 084 | 🇺🇸 | San Francisco Bay Area | Bay Wheels | [`san-francisco-bay-area/bay-wheels.geojson`](data/stations/san-francisco-bay-area/bay-wheels.geojson) | [`san-francisco-bay-area.json`](data/weather/san-francisco-bay-area.json) |
| 085 | 🇺🇸 | Santa Cruz | BCycle | [`santa-cruz/bcycle.geojson`](data/stations/santa-cruz/bcycle.geojson) | [`santa-cruz.json`](data/weather/santa-cruz.json) |
| 086 | 🇺🇸 | Washington D.C. | Capital Bikeshare | [`washington-d-c/capital-bikeshare.geojson`](data/stations/washington-d-c/capital-bikeshare.geojson) | [`washington-d-c.json`](data/weather/washington-d-c.json) |
| 087 | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 | Brighton | Beryl | [`brighton/beryl.geojson`](data/stations/brighton/beryl.geojson) | [`brighton.json`](data/weather/brighton.json) |
| 088 | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 | Manchester | Beryl | [`manchester/beryl.geojson`](data/stations/manchester/beryl.geojson) | [`manchester.json`](data/weather/manchester.json) |
| 089 | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 | Norwich | Beryl | [`norwich/beryl.geojson`](data/stations/norwich/beryl.geojson) | [`norwich.json`](data/weather/norwich.json) |
| 090 | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 | Plymouth | Beryl | [`plymouth/beryl.geojson`](data/stations/plymouth/beryl.geojson) | [`plymouth.json`](data/weather/plymouth.json) |
| 091 | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 | Portsmouth | Beryl | [`portsmouth/beryl.geojson`](data/stations/portsmouth/beryl.geojson) | [`portsmouth.json`](data/weather/portsmouth.json) |
| 092 | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 | Southampton | Beryl | [`southampton/beryl.geojson`](data/stations/southampton/beryl.geojson) | [`southampton.json`](data/weather/southampton.json) |
| 093 | 🏴󠁧󠁢󠁳󠁣󠁴󠁿 | Glasgow | Nextbike | [`glasgow/nextbike.geojson`](data/stations/glasgow/nextbike.geojson) | [`glasgow.json`](data/weather/glasgow.json) |

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
