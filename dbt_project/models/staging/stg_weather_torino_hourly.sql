SELECT
  ts_local,
  temperature_c,
  humidity_pct,
  precipitation_mm,
  wind_speed_kmh,
  wind_direction_deg,
  pressure_hpa,
  latitude,
  longitude,
  source
FROM {{ source('raw', 'weather_torino_hourly') }}
