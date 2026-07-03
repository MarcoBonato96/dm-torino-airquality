"""
Pipeline dlt: scarica meteo storico di Torino da Open-Meteo
e lo carica in BigQuery nel dataset 'raw', tabella 'weather_torino_hourly'.
"""

import dlt
import requests
from dotenv import load_dotenv

load_dotenv()

TORINO_LAT = 45.0703
TORINO_LON = 7.6869

API_URL = "https://archive-api.open-meteo.com/v1/archive"


@dlt.resource(
    name="weather_torino_hourly",
    write_disposition="replace",
    primary_key="ts_local",
)
def open_meteo_torino(
    start_date: str = "2024-01-01",
    end_date: str = "2024-01-31",
):
    params = {
        "latitude": TORINO_LAT,
        "longitude": TORINO_LON,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m",
                "wind_direction_10m",
                "surface_pressure",
            ]
        ),
        "timezone": "Europe/Berlin",
    }

    print(f"[open_meteo] Chiamo API per {start_date} -> {end_date}")

    response = requests.get(API_URL, params=params, timeout=60)
    response.raise_for_status()

    payload = response.json()
    hourly = payload["hourly"]
    times = hourly["time"]

    print(f"[open_meteo] Ricevute {len(times)} ore di dati")

    for i, ts in enumerate(times):
        yield {
            "ts_local": ts,
            "temperature_c": hourly["temperature_2m"][i],
            "humidity_pct": hourly["relative_humidity_2m"][i],
            "precipitation_mm": hourly["precipitation"][i],
            "wind_speed_kmh": hourly["wind_speed_10m"][i],
            "wind_direction_deg": hourly["wind_direction_10m"][i],
            "pressure_hpa": hourly["surface_pressure"][i],
            "latitude": payload["latitude"],
            "longitude": payload["longitude"],
            "source": "open_meteo",
        }


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="open_meteo_torino",
        destination="bigquery",
        dataset_name="raw",
    )

    load_info = pipeline.run(
        open_meteo_torino(
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
    )

    print("\n=== LOAD INFO ===")
    print(load_info)