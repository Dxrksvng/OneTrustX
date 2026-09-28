import csv
from common import fetch, normalized, provenance


def main():
    for name in ["airports", "runways", "airport-frequencies", "countries", "regions"]:
        p = fetch(
            "ourairports",
            f"https://davidmegginson.github.io/ourairports-data/{name}.csv",
            name + ".csv",
            "GLOBAL",
            "Current snapshot",
            "Public domain; https://ourairports.com/data/",
        )
        if p and name == "airports":
            rows = list(csv.DictReader(p.open()))
            selected = [
                r
                for r in rows
                if r["iso_country"] == "TH"
                or r["iata_code"]
                in [
                    "SIN",
                    "HKG",
                    "KUL",
                    "NRT",
                    "HND",
                    "ICN",
                    "JFK",
                    "LAX",
                    "SFO",
                    "LHR",
                ]
            ]
            normalized("airport_master", selected, provenance(p))


if __name__ == "__main__":
    main()
