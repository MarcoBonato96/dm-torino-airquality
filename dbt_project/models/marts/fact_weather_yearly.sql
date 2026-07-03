SELECT
  EXTRACT(YEAR FROM ts_local) AS reporting_year,

  ROUND(AVG(temperature_c), 2) AS avg_temperature_c,
  ROUND(AVG(humidity_pct), 2) AS avg_humidity_pct,
  ROUND(SUM(precipitation_mm), 2) AS total_precipitation_mm,
  ROUND(AVG(wind_speed_kmh), 2) AS avg_wind_speed_kmh,
  ROUND(AVG(pressure_hpa), 2) AS avg_pressure_hpa,

  COUNT(1) AS n_weather_hours

FROM {{ ref('stg_weather_torino_hourly') }}

GROUP BY
  reporting_year
