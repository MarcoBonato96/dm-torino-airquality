SELECT DISTINCT
  station_code,
  station,
  station_type,
  station_area,
  network,
  network_name,
  city,
  city_code,
  longitude,
  latitude,
  altitude
FROM {{ ref('stg_air_quality_statistics_torino') }}
WHERE station_code IS NOT NULL
