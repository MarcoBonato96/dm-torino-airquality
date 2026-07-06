# Air Quality Torino - Streamlit Dashboard v2

A redesigned Streamlit dashboard for the Data Management project.

## Main improvements over v1

- Cleaner Power BI-like layout
- Sidebar navigation instead of top tabs
- Large custom KPI cards
- Better chart sizing
- Stronger executive narrative
- Dedicated Data Quality page for FAQ 7 and FAQ 9
- BigQuery Storage API disabled in `to_dataframe()` to avoid `bigquery.readsessions.create` permission errors

## Run

From the project root:

```powershell
pip install -r dashboard_streamlit_v2\requirements.txt
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Pc\gcp-keys\dlt-loader-key.json"
$env:GCP_PROJECT_ID = "dm-torino-airquality"
streamlit run dashboard_streamlit_v2\app.py
```

## BigQuery marts used

- `staging_marts.mart_station_type_year_summary`
- `staging_marts.fact_air_quality_annual`
- `staging_marts.mart_air_quality_weather_yearly`
- `staging_marts.dim_station_enriched`
- `staging_marts.dq_reverse_geocoding_quality`
