"""
Pipeline dlt: arricchisce le centraline EEA con indirizzo ottenuto tramite
reverse geocoding da Nominatim / OpenStreetMap.

Input:
- staging_marts.dim_station

Output:
- raw.station_reverse_geocoding

Nota:
- Nominatim richiede un User-Agent esplicito.
- Limitiamo le richieste a circa 1 richiesta/secondo.
"""

import math
import os
import time
import dlt
import requests
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "dm-torino-airquality")

NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"

USER_AGENT = "dm-torino-airquality-project/1.0 marco-bonato"


def haversine_distance_m(lat1, lon1, lat2, lon2):
    """
    Calcola la distanza geodetica approssimata in metri tra due coordinate.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None

    radius_m = 6371000

    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radius_m * c


def get_stations_from_bigquery():
    """
    Legge le stazioni dal mart dbt dim_station.
    """
    client = bigquery.Client(project=PROJECT_ID)

    query = """
    SELECT DISTINCT
      station_code,
      station_type,
      station_area,
      city,
      latitude,
      longitude
    FROM `dm-torino-airquality.staging_marts.dim_station`
    WHERE station_code IS NOT NULL
      AND latitude IS NOT NULL
      AND longitude IS NOT NULL
    ORDER BY station_code
    """

    rows = client.query(query).result()

    return [dict(row) for row in rows]


@dlt.resource(
    name="station_reverse_geocoding",
    write_disposition="replace",
    primary_key="station_code",
)
def station_reverse_geocoding():
    stations = get_stations_from_bigquery()

    print(f"[reverse_geocoding] Stazioni da arricchire: {len(stations)}")

    headers = {"User-Agent": USER_AGENT}

    for station in stations:
        station_code = station["station_code"]
        lat = station["latitude"]
        lon = station["longitude"]

        params = {
            "format": "jsonv2",
            "lat": lat,
            "lon": lon,
            "addressdetails": 1,
        }

        print(f"[reverse_geocoding] Chiamo Nominatim per {station_code}")

        response = requests.get(
            NOMINATIM_REVERSE_URL,
            params=params,
            headers=headers,
            timeout=60,
        )

        response.raise_for_status()
        payload = response.json()

        address = payload.get("address", {})

        geocoded_lat = payload.get("lat")
        geocoded_lon = payload.get("lon")

        distance_m = haversine_distance_m(
            lat,
            lon,
            geocoded_lat,
            geocoded_lon,
        )

        yield {
            "station_code": station_code,
            "station_type": station["station_type"],
            "station_area": station["station_area"],
            "city": station["city"],
            "original_latitude": lat,
            "original_longitude": lon,
            "geocoded_latitude": geocoded_lat,
            "geocoded_longitude": geocoded_lon,
            "display_name": payload.get("display_name"),
            "road": address.get("road"),
            "house_number": address.get("house_number"),
            "postcode": address.get("postcode"),
            "suburb": address.get("suburb"),
            "quarter": address.get("quarter"),
            "neighbourhood": address.get("neighbourhood"),
            "city_from_geocoder": address.get("city"),
            "municipality": address.get("municipality"),
            "county": address.get("county"),
            "state": address.get("state"),
            "country": address.get("country"),
            "reverse_geocoding_success": 1 if payload.get("display_name") else 0,
            "distance_original_geocoded_m": distance_m,
            "source": "nominatim_openstreetmap",
        }

        time.sleep(1.1)


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="station_reverse_geocoding",
        destination="bigquery",
        dataset_name="raw",
    )

    load_info = pipeline.run(station_reverse_geocoding())

    print("\n=== LOAD INFO ===")
    print(load_info)
