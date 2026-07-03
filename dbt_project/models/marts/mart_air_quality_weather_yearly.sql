SELECT
  aq.station_code,
  aq.station_type,
  aq.station_area,
  aq.reporting_year,

  aq.pm10_annual_mean_ugm3,
  aq.no2_annual_mean_ugm3,
  aq.pm10_days_above_50,
  aq.avg_data_coverage,

  w.avg_temperature_c,
  w.avg_humidity_pct,
  w.total_precipitation_mm,
  w.avg_wind_speed_kmh,
  w.avg_pressure_hpa,
  w.n_weather_hours,

  CASE
	WHEN w.reporting_year IS NOT NULL THEN 1
	ELSE 0
  END AS weather_enrichment_success

FROM {{ ref('fact_air_quality_annual') }} aq

LEFT JOIN {{ ref('fact_weather_yearly') }} w
  ON aq.reporting_year = w.reporting_year
