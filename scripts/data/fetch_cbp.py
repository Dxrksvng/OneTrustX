import json, calendar, time
from common import fetch, normalized, provenance


def main():
    for airport in ["JFK", "LAX", "SFO"]:
        for month in [1, 2, 3]:
            period = f"2025-{month:02d}"
            p = fetch(
                "cbp",
                "https://awt.cbp.gov/api/waitTime",
                f"{airport}-{period}.json",
                f"US / {airport}",
                period,
                "CBP public airport wait report; immigration benchmark only",
                body={
                    "Id": airport,
                    "FromDate": period + "-01",
                    "ToDate": period + f"-{calendar.monthrange(2025, month)[1]}",
                },
            )
            if p:
                obj = json.loads(p.read_text())
                rows = obj.get("Items", [])
                if rows:
                    normalized("cbp_" + airport + "_" + period, rows, provenance(p))
                else:
                    print("No Items:", list(obj)[:10])
            time.sleep(1)


if __name__ == "__main__":
    main()
