SELECT
  s.station_code,
  s.station,
  s.station_type,
  s.station_area,
  s.network,
  s.network_name,
  s.city,
  s.city_code,
  s.longitude,
  s.latitude,
  s.altitude,

  g.display_name,
  g.road,
  g.house_number,
  g.postcode,

  g.reverse_geocoding_success,
  g.distance_original_geocoded_m

FROM {{ ref('dim_station') }} s

LEFT JOIN {{ ref('stg_station_reverse_geocoding') }} g
  ON s.station_code = g.station_code
