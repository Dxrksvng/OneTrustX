import csv, json, urllib.parse
from common import ROOT, fetch, normalized, provenance


def main():
    airports = list(
        csv.DictReader((ROOT / "data/normalized/airport_master.csv").open())
    )
    bkk = next(x for x in airports if x["iata_code"] == "BKK")
    params = dict(
        latitude=bkk["latitude_deg"],
        longitude=bkk["longitude_deg"],
        start_date="2025-01-01",
        end_date="2025-12-31",
        hourly="temperature_2m,relative_humidity_2m,precipitation,rain,weather_code,pressure_msl,cloud_cover,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        timezone="Asia/Bangkok",
    )
    p = fetch(
        "openmeteo",
        "https://archive-api.open-meteo.com/v1/archive?"
        + urllib.parse.urlencode(params),
        "bkk-2025.json",
        "TH / BKK",
        "2025-01-01/2025-12-31",
        "CC BY 4.0; https://open-meteo.com/en/terms",
    )
    if p:
        h = json.loads(p.read_text())["hourly"]
        normalized(
            "weather_hourly",
            (
                {"airport": "BKK", **{k: v[i] for k, v in h.items()}}
                for i in range(len(h["time"]))
            ),
            provenance(p),
        )


if __name__ == "__main__":
    main()
