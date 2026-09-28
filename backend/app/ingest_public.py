"""Idempotent import of cached normalized data. Replaces only matching dataset revisions."""

import csv
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import delete, insert

from .db import Session
from .models import MODELS
from .public_models import PublicDataset, PublicFlight, PublicObservation, PublicQueue


def main():
    root = Path(os.getenv("DATA_ROOT", "../data"))
    reports = json.loads((root / "cache/data-quality.json").read_text())["datasets"]
    with Session() as db:
        master = root / "normalized/airport_master.csv"
        if master.exists():
            bkk = next(r for r in csv.DictReader(master.open()) if r["iata_code"] == "BKK")
            airport = db.get(MODELS["airports"], "demo-airport")
            if airport:
                for key, value in {
                    "iata": "BKK",
                    "icao": bkk["ident"],
                    "airport_name": bkk["name"],
                    "city": bkk["municipality"],
                    "country": bkk["iso_country"],
                    "latitude": float(bkk["latitude_deg"]),
                    "longitude": float(bkk["longitude_deg"]),
                    "source_type": "REAL_PUBLIC",
                }.items():
                    setattr(airport, key, value)
                db.commit()
        for report in reports:
            name = report["dataset"]
            old = db.get(PublicDataset, name)
            if old and old.checksum == report["checksum"]:
                continue
            batch = []
            model = PublicObservation
            if name == "bts_flights":
                model = PublicFlight
            if name.startswith("cbp_"):
                model = PublicQueue
            if old:
                db.execute(delete(model).where(model.dataset_id == name))
                db.delete(old)
                db.flush()
            sample = report["sample"][0]
            db.add(
                PublicDataset(
                    id=name,
                    source_name=report["source_name"],
                    source_url=report["source_url"],
                    retrieved_at=datetime.fromisoformat(report["retrieved_at"]),
                    source_geography=report["source_geography"],
                    source_period=sample["source_period"],
                    source_type="REAL_PUBLIC",
                    checksum=report["checksum"],
                    records=report["records"],
                    missing_percent=report["missing_percent"],
                    duplicate_percent=report["duplicate_percent"],
                    date_from=report["date_from"],
                    date_to=report["date_to"],
                    granularity=report["granularity"],
                    license_or_terms=sample["license_or_terms"],
                )
            )
            db.flush()
            for i, r in enumerate(csv.DictReader((root / "normalized" / f"{name}.csv").open()), 1):
                common = dict(
                    id=hashlib.sha256(f"{name}:{i}".encode()).hexdigest(),
                    dataset_id=name,
                    source_type="REAL_PUBLIC",
                    source_row=i,
                )

                def number(key, r=r):
                    try:
                        return float(r[key])
                    except (KeyError, ValueError, TypeError):
                        return None

                if model == PublicFlight:
                    row = dict(
                        **common,
                        flight_date=r["FlightDate"],
                        airline=r["Reporting_Airline"],
                        flight_number=r["Flight_Number_Reporting_Airline"],
                        origin=r["Origin"],
                        destination=r["Dest"],
                        scheduled_departure=r["CRSDepTime"],
                        **{
                            k: number(v)
                            for k, v in {
                                "departure_delay": "DepDelay",
                                "arrival_delay": "ArrDelay",
                                "taxi_out": "TaxiOut",
                                "taxi_in": "TaxiIn",
                                "cancelled": "Cancelled",
                                "diverted": "Diverted",
                                "distance": "Distance",
                                "carrier_delay": "CarrierDelay",
                                "weather_delay": "WeatherDelay",
                                "nas_delay": "NASDelay",
                                "security_delay": "SecurityDelay",
                                "late_aircraft_delay": "LateAircraftDelay",
                            }.items()
                        },
                    )
                    batch.append(row)
                elif model == PublicQueue:
                    row = dict(
                        **common,
                        airport=r["AirportCode"],
                        terminal=r["TerminalName"],
                        date=r["FlightDate"],
                        hour=r["HourRange"],
                        **{
                            k: number(v)
                            for k, v in {
                                "average_wait": "AverageWait",
                                "max_wait": "MaxWait",
                                "us_average_wait": "UsaPassengerAverageWait",
                                "us_max_wait": "UsaPassengerMaxWait",
                                "non_us_average_wait": "NonUsaPassengerAverageWait",
                                "non_us_max_wait": "NonUsaPassengerMaxWait",
                                "passengers": "TotalPassengerCount",
                                "flights": "FlightCount",
                                "booths": "BoothsUsed",
                                "excluded": "ExcludedPassengerCount",
                                "bucket_0_15": "Average_0_15_PassengerCount",
                                "bucket_16_30": "Average_16_30_PassengerCount",
                                "bucket_31_45": "Average_31_45_PassengerCount",
                                "bucket_46_60": "Average_46_60_PassengerCount",
                                "bucket_61_90": "Average_61_90_PassengerCount",
                                "bucket_91_120": "Average_91_120_PassengerCount",
                                "bucket_121_plus": "Average_121_PassengerCount",
                            }.items()
                        },
                    )
                    batch.append(row)
                else:
                    metrics = []
                    if name.startswith("caat_"):
                        metrics = [
                            (
                                r["metric"],
                                number("value"),
                                r["date"],
                                r["airport"],
                                r["category"] + " · " + r["granularity"],
                            )
                        ]
                    elif name == "weather_hourly":
                        metrics = [
                            (k, number(k), r["time"], "BKK", "HOUR")
                            for k in [
                                "temperature_2m",
                                "precipitation",
                                "wind_speed_10m",
                                "wind_gusts_10m",
                                "relative_humidity_2m",
                                "rain",
                                "weather_code",
                                "pressure_msl",
                                "cloud_cover",
                                "wind_direction_10m",
                            ]
                        ]
                    elif name == "airport_master":
                        metrics = [
                            (k, number(k), "", r["iata_code"] or r["ident"], r["name"])
                            for k in ["latitude_deg", "longitude_deg", "elevation_ft"]
                        ]
                    elif "uk_caa" in name:
                        keys = (
                            ["this_year_pax"]
                            if "Table_01" in name
                            else ["grand_total", "air_transport"]
                            if "Table_03" in name
                            else ["total_pax_tp", "term_pax_tp", "tran_pax_tp"]
                        )
                        metrics = [
                            (
                                k,
                                number(k),
                                r.get("report_period", r.get("this_period", "2025")),
                                r.get("airport_name", r.get("rpt_apt_name", "")),
                                "YEAR",
                            )
                            for k in keys
                        ]
                    for j, (metric, value, date, airport, category) in enumerate(metrics):
                        batch.append(
                            {
                                **common,
                                "id": hashlib.sha256(f"{name}:{i}:{j}".encode()).hexdigest(),
                                "airport": airport,
                                "date": date,
                                "metric": metric,
                                "category": category,
                                "value": value,
                                "unit": "source units",
                            }
                        )
                if len(batch) >= 2000:
                    db.execute(insert(model), batch)
                    batch = []
            if batch:
                db.execute(insert(model), batch)
            db.commit()
            print("Imported", name, report["records"], flush=True)


if __name__ == "__main__":
    main()
