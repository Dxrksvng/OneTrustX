"""Read-only public context cache, never an operational passenger data feed."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path


def context():
    root = Path(
        os.getenv("PUBLIC_CACHE_DIR", str(Path(__file__).resolve().parents[2] / "data/raw"))
    )
    feeds = {}
    for name in ["airports", "weather", "aircraft_positions"]:
        path = root / (name + ".json")
        record = {
            "source_type": "SYNTHETIC",
            "payload": [],
            "stale": True,
            "retrieved_at": None,
            "status": "NO PUBLIC CACHE",
        }
        if path.exists():
            try:
                record = json.loads(path.read_text())
                stamp = record.get("retrieved_at")
                age = (
                    (datetime.now(UTC) - datetime.fromisoformat(stamp)).total_seconds()
                    if stamp
                    else None
                )
                ttl = 86400 if name == "airports" else 3600 if name == "weather" else 120
                record["stale"] = record.get("stale", False) or age is None or age > ttl
                record["age_seconds"] = age
            except (ValueError, OSError):
                record["status"] = "INVALID CACHE — FALLBACK"
        record["provider"] = {
            "airports": "OurAirports",
            "weather": "Open-Meteo",
            "aircraft_positions": "OpenSky Network",
        }[name]
        record["documentation_url"] = {
            "airports": "https://ourairports.com/data/",
            "weather": "https://open-meteo.com/en/docs",
            "aircraft_positions": "https://openskynetwork.github.io/opensky-api/rest.html",
        }[name]
        feeds[name] = record
    return {
        "data_mode": os.getenv("DATA_MODE", "synthetic"),
        "scope": "Public context only; operational predictions remain SYNTHETIC/SIMULATED",
        "feeds": feeds,
    }
