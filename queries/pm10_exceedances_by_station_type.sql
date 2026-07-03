SELECT
  station_type,
  reporting_year,
  ROUND(AVG(pollution_level), 2) AS avg_days_above_50,
  COUNT(1) AS n_records
FROM raw.air_quality_statistics_torino
WHERE pollutant = 'PM10'
  AND aggregation_process_id = 'P1Y-daysAbove50'
  AND unit = 'count'
GROUP BY
  station_type,
  reporting_year
ORDER BY
  reporting_year,
  station_type;
