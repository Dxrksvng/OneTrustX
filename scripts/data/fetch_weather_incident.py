"""Hourly BKK weather for the Sept 2026 flood/baggage reference incident (Open-Meteo archive)."""
import csv, json, urllib.parse
from common import ROOT, fetch, normalized, provenance

START, END = "2026-09-22", "2026-10-03"


def main():
    airports = list(csv.DictReader((ROOT / "data/normalized/airport_master.csv").open()))
    bkk = next(x for x in airports if x["iata_code"] == "BKK")
    params = dict(
        latitude=bkk["latitude_deg"],
        longitude=bkk["longitude_deg"],
        start_date=START,
        end_date=END,
        hourly="precipitation,rain,weather_code,wind_gusts_10m",
        timezone="Asia/Bangkok",
    )
    p = fetch(
        "openmeteo",
        "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params),
        "bkk-2026-09-incident.json",
        "TH / BKK",
        f"{START}/{END}",
        "CC BY 4.0; https://open-meteo.com/en/terms",
    )
    if p:
        h = json.loads(p.read_text())["hourly"]
        normalized(
            "weather_hourly_incident_2026_09",
            ({"airport": "BKK", **{k: v[i] for k, v in h.items()}} for i in range(len(h["time"]))),
            provenance(p),
        )


if __name__ == "__main__":
    main()
