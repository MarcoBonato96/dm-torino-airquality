SELECT
  station_code,
  station_type,
  station_area,
  reporting_year,
  MAX(CASE WHEN pollutant = 'PM10'
        	AND aggregation_process_id = 'P1Y'
        	AND unit = 'ug/m3'
       	THEN pollution_level END) AS pm10_annual_mean_ugm3,
  MAX(CASE WHEN pollutant = 'NO2'
        	AND aggregation_process_id = 'P1Y'
        	AND unit = 'ug/m3'
       	THEN pollution_level END) AS no2_annual_mean_ugm3,
  MAX(CASE WHEN pollutant = 'PM10'
        	AND aggregation_process_id = 'P1Y-daysAbove50'
        	AND unit = 'count'
       	THEN pollution_level END) AS pm10_days_above_50
FROM raw.air_quality_statistics_torino
GROUP BY
  station_code,
  station_type,
  station_area,
  reporting_year
ORDER BY
  station_code,
  reporting_year;
