# Air Quality Assessment in Torino through Integration of Environmental, Meteorological, and Spatial Enrichment Data

Data Management Project Report

Course: Data Management and Data Visualization
Institution: Universita degli Studi di Milano-Bicocca (UNIMIB)
Academic Year: 2025-2026
Repository: [insert repository URL]
Group Members:
- [Student 1]
- [Student 2]
- [Student 3]

Date: [insert final submission date]

## Abstract

This project analyzes air quality in Torino by integrating heterogeneous environmental datasets into a reproducible analytical pipeline. The system combines annual air-quality statistics from EEA DiscoData, hourly meteorological observations from Open-Meteo, and reverse-geocoded station metadata from Nominatim / OpenStreetMap. Data are acquired through automated Python pipelines, stored in Google BigQuery, transformed with dbt, validated through automated tests, and exposed through SQL queries and a Streamlit dashboard. The project addresses all phases required by the Data Management course: acquisition, storage, profiling, integration, analysis, and quality improvement. Particular attention is paid to enrichment quality measurement, especially for spatial integration, in line with the course FAQ.

## 1. Introduction

Air pollution remains a critical urban issue because it affects public health, environmental quality, and policy evaluation. Torino is a relevant case study because it contains both Traffic and Background monitoring stations and exhibits measurable differences in pollutant concentration across station types and years.

The project objective is twofold:

- O1: build a reproducible data-management pipeline that acquires, stores, transforms, validates, and integrates environmental datasets.
- O2: answer research-driven questions on PM10 and NO2 patterns in Torino through SQL analysis and a Streamlit dashboard.

### 1.1 Research Questions

The project answers the following research questions:

- RQ1: How do PM10 and NO2 annual concentrations differ between Traffic and Background monitoring stations in Torino during 2022-2024?
- RQ2: How do annual PM10 and NO2 indicators evolve between 2022 and 2024 for different station types?
- RQ3: How do PM10 exceedance days above 50 ug/m3 vary across years and station types?
- RQ4: Can yearly weather indicators and reverse-geocoded station information be integrated into the analytical warehouse with measurable quality?

### 1.2 Scope

The project focuses on Torino monitoring stations and covers the years 2022, 2023, and 2024. The implemented system is based on annual air-quality indicators, yearly weather aggregation, and spatial enrichment of station metadata. The analytical scope is intentionally descriptive and integrative rather than causal.

## 2. Data Sources and Acquisition

The project uses three complementary data sources.

### 2.1 Air-Quality Statistics (EEA DiscoData)

The core pollutant dataset is extracted from the EEA DiscoData AirQualityStatistics source. This dataset provides annual indicators for monitoring stations, including PM10 annual mean, NO2 annual mean, and PM10 exceedance days above the daily threshold.

Acquisition method:

- source type: API / HTTP SQL endpoint
- implementation: Python dlt pipeline
- destination raw table: raw.air_quality_statistics_torino

Loaded evidence:

- 669 annual air-quality records

### 2.2 Meteorological Data (Open-Meteo Historical API)

Weather data are acquired from the Open-Meteo Historical API. The source provides hourly meteorological observations that are later aggregated yearly to support enrichment of air-quality facts.

Acquisition method:

- source type: API
- implementation: Python dlt pipeline
- destination raw table: raw.weather_torino_hourly

Loaded evidence:

- 26,328 hourly weather records

### 2.3 Station Address Enrichment (Nominatim / OpenStreetMap)

Spatial enrichment is performed through reverse geocoding of monitoring station coordinates using Nominatim / OpenStreetMap. This source is used to generate a human-readable address and to measure integration quality through geographic distance between original and returned coordinates.

Acquisition method:

- source type: API
- implementation: Python dlt pipeline
- destination raw table: raw.station_reverse_geocoding

### 2.4 Acquisition Constraints

The acquisition process is shaped by the following constraints:

- the three external sources have different schemas and semantics
- Open-Meteo returns high-volume hourly data and therefore requires efficient storage
- Nominatim requires rate-aware usage and explicit user-agent configuration
- spatial enrichment must be evaluated quantitatively, not only executed operationally

These constraints motivated an automated multi-stage architecture rather than ad hoc local analysis.

## 3. Storage Layer and Database Design

### 3.1 Why BigQuery and dbt

The project stores raw and transformed data in Google BigQuery. BigQuery was selected because it supports scalable analytical querying, integrates well with Python pipelines, and simplifies downstream reporting. dbt is used as the transformation layer because it supports versioned SQL models, modular transformations, and declarative test-based quality checks.

### 3.2 Logical Schema

The implemented warehouse contains the following layers.

Raw tables:

- raw.air_quality_statistics_torino
- raw.weather_torino_hourly
- raw.station_reverse_geocoding

Staging models:

- stg_air_quality_statistics_torino
- stg_weather_torino_hourly
- stg_station_reverse_geocoding

Mart models:

- dim_station
- fact_air_quality_annual
- fact_weather_yearly
- mart_station_type_year_summary
- mart_air_quality_weather_yearly
- dim_station_enriched
- dq_reverse_geocoding_quality

### 3.3 Analytical Design

The warehouse is designed around a fact-dimension logic.

- fact_air_quality_annual stores annual PM10 and NO2 indicators by station and reporting year
- dim_station stores the canonical station metadata
- mart_station_type_year_summary aggregates facts by station type and year to support RQ1-RQ3
- mart_air_quality_weather_yearly enriches annual air-quality facts with yearly weather features
- dim_station_enriched adds spatial metadata and reverse-geocoded address fields
- dq_reverse_geocoding_quality stores the measured integration-quality metrics required by the course

This design satisfies the FAQ requirement to store integrated data in a DBMS and to support at least two queries on the resulting data.

## 4. Data Profiling and Data Quality

### 4.1 Standardization and Validation

The pipeline standardizes and validates incoming data before analytical use.

- Python ingestion pipelines normalize field names and data types
- dbt staging models clean and align raw schemas
- analytical marts expose business-ready fields for the dashboard and query layer

### 4.2 Automated Quality Checks

The project uses dbt tests to verify essential quality constraints. The implemented tests cover:

- completeness through not_null constraints
- uniqueness through unique constraints on station keys
- validity through accepted_values checks on station_type and enrichment flags
- enrichment success constraints for weather and reverse geocoding

Quality evidence:

- 30 dbt tests completed successfully

### 4.3 Quality Metrics

In line with FAQ 7 and FAQ 9, the project measures integration and enrichment quality explicitly.

For reverse geocoding, the project reports:

- total station coverage: 100%
- average geocoding distance: 27.09 m
- maximum geocoding distance: 55.34 m

For weather enrichment, the project reports:

- weather enrichment success: 100% of station-year records

These metrics demonstrate that enrichment is not treated as a black box; instead, it is monitored through quantitative indicators.

## 5. Data Integration and Enrichment

### 5.1 Weather Enrichment

The first integration task links annual air-quality indicators with yearly weather summaries. The resulting mart, mart_air_quality_weather_yearly, makes it possible to analyze pollutant behavior in the context of meteorological conditions.

The integration is automated through the warehouse pipeline rather than manual spreadsheet joins. This directly satisfies the course requirement that integration must be automated.

### 5.2 Spatial Enrichment

The second integration task enriches station metadata with reverse-geocoded information from Nominatim / OpenStreetMap. The resulting dim_station_enriched table contains human-readable address fields and the measured distance between original coordinates and the geocoded point.

This enrichment is particularly aligned with the FAQ suggestion to pay attention to spatial integration cases.

### 5.3 Integration Outcome

The integration outcome is positive on both dimensions:

- weather enrichment succeeded for all analytical records
- reverse geocoding enriched all stations
- the geocoding error remained within a small and interpretable range

Therefore, the project satisfies the requirement of integrating at least two datasets and measuring the related enrichment error.

## 6. Analysis and Visualization

### 6.1 SQL Query Layer

The project includes multiple analytical SQL queries, including:

- annual_means_by_station.sql
- annual_means_by_station_type.sql
- air_quality_station_year_summary.sql
- air_quality_station_type_year_summary.sql
- pm10_exceedances_by_station.sql
- pm10_exceedances_by_station_type.sql

These queries satisfy the course requirement to perform at least two queries on stored data.

### 6.2 Dashboard Overview

The Streamlit dashboard is built on top of the warehouse marts and is organized around the research questions. It includes:

- an executive summary
- dedicated RQ pages for descriptive comparison, temporal evolution, exceedance analysis, and integration quality
- metric cards and presentation-oriented charts
- evidence tables and reproducibility notes

### 6.3 Main Findings

The main analytical findings are the following.

RQ1:

- Traffic stations show higher PM10 and NO2 annual means than Background stations in every observed year
- in 2024, NO2 equals 38.59 ug/m3 at Traffic stations versus 27.77 ug/m3 at Background stations

RQ2:

- PM10 decreases between 2022 and 2024 for both station types
- NO2 also declines, but remains comparatively higher for Traffic stations

RQ3:

- Traffic stations show more PM10 exceedance days in all observed years
- yearly station-type values are 71.5 vs 47.5 in 2022, 58.0 vs 28.0 in 2023, and 44.5 vs 39.0 in 2024

RQ4:

- weather enrichment succeeded for all station-year records
- reverse-geocoding enrichment reached 100% coverage
- geocoding error remained limited, with a maximum of 55.34 m

## 7. Reproducibility and Deployment

The project is reproducible because all main components are codified in the repository.

Reproducibility elements:

- Python dlt pipelines for acquisition
- BigQuery as raw and analytical storage
- dbt models and schema tests for transformation and quality control
- SQL query files for direct analytical access
- Streamlit dashboard for final presentation
- environment variables for cloud credentials and project configuration

### 7.1 Operational Notes

The dashboard and pipelines depend on GCP credentials. The final operational setup uses:

- GOOGLE_APPLICATION_CREDENTIALS for the service account key
- GCP_PROJECT_ID for project routing
- the BigQuery dataset staging_marts for final analytical access

The Streamlit app can be launched from the outer dashboard folder through the added launcher app.py.

## 8. Limitations and Future Improvements

### 8.1 Limitations

The current implementation has the following limitations:

- the project works on annual air-quality indicators rather than finer-grained daily or hourly pollution series
- the number of monitoring stations is limited to the Torino scope available in the selected source
- the analysis is descriptive and does not estimate causal relationships
- weather enrichment is annual, which is appropriate for the current RQs but not for short-term event analysis

### 8.2 Future Improvements

Possible extensions include:

- adding daily or hourly air-quality sources to support higher-frequency analysis
- extending the geographic scope beyond Torino
- enriching the dashboard with stronger comparative policy context
- tracking quality metrics over time through a dedicated monitoring table or dashboard
- integrating additional spatial datasets such as road traffic or land-use indicators

## 9. Conclusion

This project demonstrates a complete end-to-end data-management workflow on a real environmental domain. It includes automated acquisition from multiple sources, structured storage in a DBMS, profiling and validation, automated integration and enrichment, explicit error measurement, analytical SQL queries, and a Streamlit dashboard for presentation. The solution is consistent with the course FAQ because it covers all required phases of the pipeline and provides measurable evidence for both data quality and integration quality.

In summary, the project shows that Traffic stations in Torino consistently exhibit worse air-quality indicators than Background stations, that PM10 decreases over the observed period but exceedances remain a relevant issue, and that weather and spatial enrichment can be integrated with full coverage and controlled error.