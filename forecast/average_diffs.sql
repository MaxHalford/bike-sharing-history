WITH diffs AS (
  SELECT
    curr.station,
    curr.time_step,
    curr.bikes,
    curr.bikes - prev.bikes AS bikes_diff
  FROM forecast.resampled_updates curr
  INNER JOIN forecast.resampled_updates prev ON
    curr.station = prev.station AND
    curr.time_step = prev.time_step + INTERVAL '15 minute'
)

SELECT
  station,
  PRINTF('%02d:%02d', EXTRACT(HOUR FROM time_step), EXTRACT(MINUTE FROM time_step)) time_step_in_day,
  AVG(bikes_diff),
  COUNT(*) AS n
FROM diffs
GROUP BY ALL
