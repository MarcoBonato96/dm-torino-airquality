SELECT
  station_code,
  station_type,
  station_area,
  pollutant,
  reporting_year,
  pollution_level AS annual_mean_ugm3,
  data_coverage
FROM raw.air_quality_statistics_torino
WHERE aggregation_process_id = 'P1Y'
  AND unit = 'ug/m3'
  AND pollutant IN ('PM10','NO2')
ORDER BY station_code, pollutant, reporting_year;
