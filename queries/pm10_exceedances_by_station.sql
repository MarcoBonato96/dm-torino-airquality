SELECT
  station_code,
  station_type,
  station_area,
  reporting_year,
  pollution_level AS days_above_50,
  data_coverage
FROM raw.air_quality_statistics_torino
WHERE pollutant = 'PM10'
  AND aggregation_process_id = 'P1Y-daysAbove50'
  AND unit = 'count'
ORDER BY
  reporting_year,
  station_code;

