SELECT
  COUNT(1) AS total_stations,

  SUM(reverse_geocoding_success) AS enriched_stations,

  ROUND(
	SAFE_DIVIDE(SUM(reverse_geocoding_success), COUNT(1)) * 100,
	2
  ) AS enrichment_coverage_pct,

  SUM(
	CASE
  	WHEN display_name IS NULL THEN 1
  	ELSE 0
	END
  ) AS missing_display_name_count,

  ROUND(AVG(distance_original_geocoded_m), 2) AS avg_distance_m,

  ROUND(MAX(distance_original_geocoded_m), 2) AS max_distance_m,

  ROUND(
	SAFE_DIVIDE(
  	SUM(CASE WHEN distance_original_geocoded_m <= 50 THEN 1 ELSE 0 END),
  	COUNT(1)
	) * 100,
	2
  ) AS stations_within_50m_pct,

  ROUND(
	SAFE_DIVIDE(
  	SUM(CASE WHEN distance_original_geocoded_m <= 100 THEN 1 ELSE 0 END),
  	COUNT(1)
	) * 100,
	2
  ) AS stations_within_100m_pct

FROM {{ ref('dim_station_enriched') }}
