SELECT
  station_type,
  pollutant,
  reporting_year,
  ROUND(AVG(pollution_level), 2) AS avg_annual_mean_ugm3,
  COUNT(1) AS n_records
FROM raw.air_quality_statistics_torino
WHERE aggregation_process_id = 'P1Y'
  AND unit = 'ug/m3'
  AND pollutant IN ('PM10','NO2')
GROUP BY
  station_type,
  pollutant,
  reporting_year
ORDER BY
  pollutant,
  reporting_year,
  station_type;
