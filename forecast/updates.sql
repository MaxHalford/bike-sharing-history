SELECT filename, *
FROM READ_PARQUET('gs://bike-sharing-history/toulouse/jcdecaux/*/*.parquet')
