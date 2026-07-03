
SELECT
  station_type,
  reporting_year,

  ROUND(AVG(pm10_annual_mean_ugm3), 2) AS avg_pm10_annual_mean_ugm3,

  ROUND(AVG(no2_annual_mean_ugm3), 2) AS avg_no2_annual_mean_ugm3,

  ROUND(AVG(pm10_days_above_50), 2) AS avg_pm10_days_above_50,

  COUNT(*) AS n_stations

FROM {{ ref('fact_air_quality_annual') }}

GROUP BY
  station_type,
  reporting_year
