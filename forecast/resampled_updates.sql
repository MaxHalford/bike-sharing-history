WITH updates AS (
  SELECT
    station,
    commit_at,
    TIMESTAMP 'epoch' + INTERVAL '1 second' * CEIL(EXTRACT(EPOCH FROM commit_at) / (15 * 60)) * (15 * 60) AS next_time_step,
    bikes,
    stands
  FROM forecast.updates
)

SELECT
  station,
  next_time_step AS time_step,
  bikes,
  stands
FROM (
  SELECT
    *,
    RANK() OVER (PARTITION BY (station, next_time_step) ORDER BY commit_at DESC) rn
  FROM updates
)
WHERE rn = 1
