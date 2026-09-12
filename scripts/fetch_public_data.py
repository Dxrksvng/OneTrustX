"""Public contextual data only. Protected operations ALWAYS remain synthetic.
On failure retain an explicitly stale cache, or write an explicitly SYNTHETIC fallback.
"""

import csv
import io
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import httpx

root = Path(__file__).resolve().parents[1] / "data/raw"
root.mkdir(parents=True, exist_ok=True)
urls = {
    "airports": "https://davidmegginson.github.io/ourairports-data/airports.csv",
    "weather": "https://api.open-meteo.com/v1/forecast?latitude=13.69&longitude=100.75&hourly=temperature_2m,precipitation,wind_speed_10m,wind_gusts_10m,visibility,weather_code&forecast_days=1",
    "aircraft_positions": "https://opensky-network.org/api/states/all?lamin=12&lomin=99&lamax=15&lomax=102",
}
for name, url in urls.items():
    dest = root / (name + ".json")
    try:
        headers = {}
        if name == "aircraft_positions" and os.getenv("OPENSKY_ACCESS_TOKEN"):
            headers["Authorization"] = "Bearer " + os.environ["OPENSKY_ACCESS_TOKEN"]
        response = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
        response.raise_for_status()
        payload = (
            [
                row
                for row in csv.DictReader(io.StringIO(response.text))
                if row["ident"] == "VTBS"
            ]
            if name == "airports"
            else response.json()
        )
        record = {
            "source_type": "REAL_PUBLIC",
            "source_url": url,
            "retrieved_at": datetime.now(UTC).isoformat(),
            "stale": False,
            "payload": payload,
            "scope": "Context only; no queue, schedule completeness, or passenger claims",
        }
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        record = (
            json.loads(dest.read_text())
            if dest.exists()
            else {
                "source_type": "SYNTHETIC",
                "payload": [],
                "retrieved_at": None,
                "source_url": url,
            }
        )
        record.update(
            stale=True,
            last_attempt=datetime.now(UTC).isoformat(),
            error=type(exc).__name__,
        )
    dest.write_text(json.dumps(record, indent=2))
    print(name, record["source_type"], "STALE" if record["stale"] else "retrieved")
