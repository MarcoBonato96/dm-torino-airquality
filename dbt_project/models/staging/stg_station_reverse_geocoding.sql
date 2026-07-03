SELECT
  station_code,
  station_type,
  station_area,
  city,

  CAST(original_latitude AS FLOAT64) AS original_latitude,
  CAST(original_longitude AS FLOAT64) AS original_longitude,
  CAST(geocoded_latitude AS FLOAT64) AS geocoded_latitude,
  CAST(geocoded_longitude AS FLOAT64) AS geocoded_longitude,

  display_name,
  road,
  house_number,
  postcode,

  CAST(reverse_geocoding_success AS INT64) AS reverse_geocoding_success,
  CAST(distance_original_geocoded_m AS FLOAT64) AS distance_original_geocoded_m,

  source

FROM {{ source('raw', 'station_reverse_geocoding') }}
