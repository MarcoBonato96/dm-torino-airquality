# Air Quality Assessment in Torino

Data Management Project Presentation

This presentation is designed to respect the DM FAQ constraints and is inspired by the structure of the provided sample presentation. It is written in English so it can be reused directly for the oral exam and converted into slides.

## Slide 1 - Cover

Title:

- Air Quality Assessment in Torino through Integration of Environmental, Meteorological, and Spatial Enrichment Data

Subtitle:

- Data Management Project Presentation
- Universita degli Studi di Milano-Bicocca (UNIMIB)
- Academic Year 2025-2026

Footer fields to complete:

- [Student 1]
- [Student 2]
- [Student 3]
- [date]

## Slide 2 - Agenda

- Motivation and objectives
- Research questions
- Data sources and acquisition
- Storage and database design
- Data quality and integration
- Analysis and dashboard
- Reproducibility
- Limitations and future work
- Conclusion

## Slide 3 - Motivation

- Air pollution is a relevant urban and public-health issue
- Torino offers a useful case because it includes both Traffic and Background monitoring stations
- We wanted to build a reproducible pipeline, not just a set of static charts
- The project studies PM10, NO2, exceedance days, and integration quality

Speaker note:

- Stress that the project is both analytical and infrastructural: not only findings, but also acquisition, storage, integration, and quality measurement

## Slide 4 - Objectives

- Acquire heterogeneous datasets automatically
- Store them in a DBMS suitable for analytical querying
- Transform and validate them through a reproducible workflow
- Integrate weather and spatial enrichment into the analytical warehouse
- Answer four research questions through SQL and Streamlit

## Slide 5 - Research Questions

- RQ1: How do PM10 and NO2 annual concentrations differ between Traffic and Background stations in 2022-2024?
- RQ2: How do annual PM10 and NO2 indicators evolve over time?
- RQ3: How do PM10 exceedance days above 50 ug/m3 vary by year and station type?
- RQ4: Can weather and reverse-geocoded station information be integrated with measurable quality?

## Slide 6 - Data Sources

Left column:

- EEA DiscoData AirQualityStatistics
- annual PM10 and NO2 indicators
- 669 loaded records

Center column:

- Open-Meteo Historical API
- hourly weather observations
- 26,328 loaded records

Right column:

- Nominatim / OpenStreetMap
- reverse geocoding for stations
- spatial enrichment and error measurement

## Slide 7 - Acquisition Strategy

- Three automated Python dlt pipelines
- API-based ingestion for all sources
- Raw tables loaded into BigQuery
- Repeatable and reproducible execution through environment variables and cloud credentials

Suggested visual:

- simple pipeline diagram: APIs -> dlt -> BigQuery raw

## Slide 8 - Storage and Architecture

- Storage layer: Google BigQuery
- Transformation layer: dbt
- Presentation layer: Streamlit
- Query layer: SQL files in the repository

Analytical tables:

- fact_air_quality_annual
- mart_station_type_year_summary
- mart_air_quality_weather_yearly
- dim_station_enriched
- dq_reverse_geocoding_quality

## Slide 9 - Data Quality

- Completeness: key fields tested with not_null
- Uniqueness: station keys tested with unique
- Validity: accepted station types and enrichment flags
- Automated evidence: 30 dbt tests passed

Speaker note:

- This slide answers FAQ 9 directly: quality is measured explicitly, not assumed

## Slide 10 - Data Integration and Enrichment

- Weather enrichment joins yearly weather indicators to annual air-quality facts
- Spatial enrichment reverse-geocodes monitoring stations
- Integration is fully automated in the warehouse pipeline
- Error is measured, not only described

Key metrics:

- weather enrichment success: 100%
- geocoding coverage: 100%
- average geocoding distance: 27.09 m
- maximum geocoding distance: 55.34 m

## Slide 11 - RQ1 and RQ2 Results

- Traffic stations consistently show worse pollutant values than Background stations
- In 2024, NO2 is 38.59 ug/m3 for Traffic vs 27.77 ug/m3 for Background
- PM10 decreases between 2022 and 2024 for both station types
- NO2 also declines, but remains close to the EU limit at Traffic stations

Suggested visual:

- use the dashboard charts from RQ1 and RQ2

## Slide 12 - RQ3 Results

- PM10 exceedance days are higher at Traffic stations in every observed year
- 2022: 71.5 vs 47.5
- 2023: 58.0 vs 28.0
- 2024: 44.5 vs 39.0
- The EU maximum of 35 days is exceeded systematically at Traffic stations

Suggested visual:

- use the per-station or station-type exceedance chart from the dashboard

## Slide 13 - RQ4 Results

- Weather and spatial enrichment were integrated successfully
- Reverse geocoding covered all stations
- Quality remained controlled, with low measured spatial error
- The project therefore satisfies the FAQ requirement on automated enrichment and error measurement

Suggested visual:

- table from the RQ4 dashboard page plus the geocoding quality chart

## Slide 14 - Dashboard

- Streamlit dashboard organized by executive summary and research-question pages
- KPI cards, evidence tables, and presentation-ready charts
- Built directly on BigQuery marts
- Useful both for analysis and for oral presentation support

## Slide 15 - Reproducibility

- Source code versioned in the repository
- Pipelines implemented in Python
- Warehouse modeled in BigQuery
- Transformations and tests implemented in dbt
- Analytical queries stored as SQL files
- Dashboard launchable through Streamlit

Suggested talking point:

- Mention that the repository also includes a launcher to simplify dashboard execution from the outer folder

## Slide 16 - Limitations

- Annual air-quality indicators limit temporal granularity
- The spatial scope is limited to the selected Torino stations
- The analysis is descriptive, not causal
- More external contextual datasets could strengthen interpretation

## Slide 17 - Future Work

- Add higher-frequency pollution data
- Extend beyond Torino
- Integrate additional spatial datasets such as traffic or land use
- Track data-quality indicators historically
- Add more advanced analytical comparisons and policy context

## Slide 18 - Conclusion

- End-to-end project: acquisition -> storage -> profiling -> integration -> analysis -> quality improvement
- At least two data sources used, with API-based acquisition
- Integrated data stored in a DBMS and queried through SQL
- Integration quality measured explicitly
- Final output includes both analytical results and a reproducible architecture

Closing sentence:

- The project demonstrates that a structured data-management workflow can produce both reliable analytical evidence and a reusable infrastructure for environmental monitoring.

## Slide 19 - Questions

- Thank you
- Questions?

Optional footer:

- repository URL
- course name
- student names