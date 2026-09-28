import csv, io, zipfile
from common import fetch, normalized, provenance

FIELDS = [
    "FlightDate",
    "Reporting_Airline",
    "Flight_Number_Reporting_Airline",
    "Origin",
    "Dest",
    "CRSDepTime",
    "DepTime",
    "DepDelay",
    "TaxiOut",
    "WheelsOff",
    "WheelsOn",
    "TaxiIn",
    "CRSArrTime",
    "ArrTime",
    "ArrDelay",
    "Cancelled",
    "Diverted",
    "CarrierDelay",
    "WeatherDelay",
    "NASDelay",
    "SecurityDelay",
    "LateAircraftDelay",
    "Distance",
]


def main():
    p = fetch(
        "bts",
        "https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_2.zip",
        "2025-02.zip",
        "US DOMESTIC",
        "2025-02",
        "US DOT public statistics; https://www.bts.gov/terms-use",
    )
    if not p:
        return
    with zipfile.ZipFile(p) as z:
        name = next(x for x in z.namelist() if x.endswith(".csv"))
        with z.open(name) as stream:
            reader = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig"))
            # Full month; preserve all real rows and missing values. Never relabel these as BKK flights.
            normalized(
                "bts_flights",
                ({k: r.get(k, "") for k in FIELDS} for r in reader),
                provenance(p),
            )


if __name__ == "__main__":
    main()
