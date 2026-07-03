"""
Pipeline dlt: estrae statistiche annuali di qualità dell'aria per Torino
da EEA DiscoData e le carica in BigQuery nel dataset raw.

Fonte:
https://discodata.eea.europa.eu/

Tabella sorgente:
[AirQualityDataFlows].[latest].[AirQualityStatistics]
"""

import os
from urllib.parse import quote

import dlt
import requests
from dotenv import load_dotenv


load_dotenv()

DISCODATA_SQL_ENDPOINT = "https://discodata.eea.europa.eu/sql?query="


SQL_QUERY = """
SELECT
	[AirQualityStationEoICode]   AS station_code,
	[AirQualityStation]      	AS station,
	[AirQualityStationType]  	AS station_type,
	[AirQualityStationArea]  	AS station_area,
	[AirQualityNetwork]      	AS network,
	[AirQualityNetworkName]  	AS network_name,
	[SamplingPoint]          	AS sampling_point,
	[City]                   	AS city,
	[CityCode]               	AS city_code,
	[AirPollutant]           	AS pollutant,
	[AirPollutantCode]       	AS pollutant_code,
	[AirPollutionLevel]      	AS pollution_level,
	[UnitOfAirPollutionLevel]	AS unit,
	[DataAggregationProcess] 	AS aggregation_process,
	[DataAggregationProcessId]   AS aggregation_process_id,
	[ReportingYear]          	AS reporting_year,
	[DataCoverage]           	AS data_coverage,
	[Verification]           	AS verification,
	[Longitude]              	AS longitude,
	[Latitude]               	AS latitude,
	[Altitude]               	AS altitude
FROM [AirQualityDataFlows].[latest].[AirQualityStatistics]
WHERE [Countrycode] = 'IT'
  AND [City] = 'Torino'
  AND [AirPollutant] IN ('PM10','NO2','PM2.5','O3')
  AND [ReportingYear] BETWEEN 2022 AND 2024
"""


def normalize_discodata_response(payload):
    """
    Normalizza la risposta JSON di DiscoData in una lista di record.
    """

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ["results", "result", "data", "rows"]:
            if key in payload and isinstance(payload[key], list):
                return payload[key]

    raise ValueError(f"Formato JSON DiscoData non riconosciuto: {type(payload)}")


@dlt.resource(
    name="air_quality_statistics_torino",
    write_disposition="replace",
    primary_key=[
        "station_code",
        "sampling_point",
        "pollutant",
        "aggregation_process_id",
        "reporting_year",
    ],
)
def eea_air_quality_statistics_torino():
    encoded_query = quote(SQL_QUERY.strip())
    url = DISCODATA_SQL_ENDPOINT + encoded_query

    print("[eea_discodata] Chiamo DiscoData API")

    response = requests.get(url, timeout=180)
    response.raise_for_status()

    payload = response.json()
    records = normalize_discodata_response(payload)

    print(f"[eea_discodata] Ricevuti {len(records)} record")

    for record in records:
        yield record


if __name__ == "__main__":
    project_id = os.getenv("GCP_PROJECT_ID")

    print(f"[eea_discodata] Project ID da .env: {project_id}")

    pipeline = dlt.pipeline(
        pipeline_name="eea_discodata_torino",
        destination="bigquery",
        dataset_name="raw",
    )

    load_info = pipeline.run(eea_air_quality_statistics_torino())

    print("\n=== LOAD INFO ===")
    print(load_info)
