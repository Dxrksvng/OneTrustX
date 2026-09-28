"""Server-side public context aggregates. No outbound requests on page load."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from .db import get_db
from .public_fallback import PUBLIC_CONTEXT_FALLBACK
from .public_models import PublicDataset, PublicFlight, PublicObservation

router = APIRouter(prefix="/api/data")


def cache(name):
    p = Path(os.getenv("DATA_ROOT", "../data")) / "cache" / name
    return json.loads(p.read_text()) if p.exists() else None


@router.get("/catalog")
def catalog(db=Depends(get_db)):
    rows = db.scalars(
        select(PublicDataset).order_by(PublicDataset.source_name, PublicDataset.id)
    ).all()
    datasets = []
    for r in rows:
        stamp = (
            r.retrieved_at.replace(tzinfo=timezone.utc)
            if r.retrieved_at.tzinfo is None
            else r.retrieved_at
        )
        datasets.append(
            {c.name: getattr(r, c.name) for c in r.__table__.columns}
            | {"freshness": "FRESH" if (datetime.now(timezone.utc) - stamp).days < 30 else "STALE"}
        )
    unavailable = [
        {
            "source_name": "TSA",
            "freshness": "UNAVAILABLE",
            "source_type": None,
            "source_url": "https://www.tsa.gov/travel/passenger-volumes",
            "reason": "Official endpoint returned HTTP 403. No observations imported.",
        },
        {
            "source_name": "AOT",
            "freshness": "UNAVAILABLE",
            "source_type": None,
            "source_url": "https://corporatestrategy.airportthai.co.th/ats/",
            "reason": "Independent traffic validation not yet imported. Inline dashboard totals failed reconciliation; not used as observations.",
        },
        {
            "source_name": "EUROCONTROL ADRR",
            "freshness": "UNAVAILABLE",
            "source_type": None,
            "source_url": "https://www.eurocontrol.int/dashboard/aviation-data-research",
            "reason": "Future research connector; no account-gated data dependency.",
        },
    ]
    return {
        "datasets": datasets,
        "unavailable": unavailable,
        "freshness_definition": "Freshness describes cached source retrieval, not live airport telemetry. Historical periods remain visible.",
        "quality": cache("data-quality.json"),
        "queue_benchmark": cache("queue-benchmark.json"),
    }


@router.get("/context")
def context(db=Depends(get_db)):
    fallback = PUBLIC_CONTEXT_FALLBACK
    o = PublicObservation
    d = PublicDataset
    traffic = db.execute(
        select(o.date, o.airport, o.category, o.metric, o.value, d.source_url, d.id, d.date_to)
        .join(d)
        .where(d.source_name == "caat", o.metric == "passengers", o.value.is_not(None))
        .order_by(d.date_to, d.id)
    ).all()
    unique = {}
    for r in traffic:
        unique[(r.date, r.airport, r.category)] = {
            "date": r.date,
            "airport": r.airport,
            "category": r.category,
            "passengers": r.value,
            "source_url": r.source_url,
            "dataset_id": r.id,
            "source_type": "REAL_PUBLIC",
        }
    bkk = sorted(
        [r for r in unique.values() if r["airport"] == "BKK" and r["category"] == "Total · DAY"],
        key=lambda x: x["date"],
    )
    thailand = sorted(
        [
            r
            for r in unique.values()
            if r["airport"] == "TH_TOTAL" and r["category"] == "Total · DAY"
        ],
        key=lambda x: x["date"],
    )
    monthly = sorted(
        [
            r
            for r in unique.values()
            if r["airport"] == "TH_TOTAL" and r["category"] == "Total · MONTH"
        ],
        key=lambda x: x["date"],
    )
    weather = db.execute(
        select(func.substr(o.date, 1, 7).label("month"), o.metric, func.avg(o.value).label("mean"))
        .join(d)
        .where(
            d.source_name == "openmeteo",
            o.metric.in_(["temperature_2m", "wind_speed_10m", "precipitation"]),
        )
        .group_by("month", o.metric)
    ).all()
    flights = db.execute(
        select(
            PublicFlight.flight_date,
            func.count().label("flights"),
            func.avg(PublicFlight.departure_delay).label("mean_departure_delay"),
            func.sum(PublicFlight.cancelled).label("cancelled"),
        )
        .group_by(PublicFlight.flight_date)
        .order_by(PublicFlight.flight_date)
    ).all()
    return {
        "airport": {
            "iata": "BKK",
            "name": "Suvarnabhumi Airport",
            "coordinates": {
                r.metric: r.value
                for r in db.scalars(
                    select(o).where(o.airport == "BKK", o.dataset_id == "airport_master")
                )
            },
            "source_type": "REAL_PUBLIC",
        },
        "bkk_daily": bkk or fallback["bkk_daily"],
        "thailand_daily": thailand,
        "thailand_monthly": monthly or fallback["thailand_monthly"],
        "weather_monthly": [dict(r._mapping) for r in weather] or fallback["weather_monthly"],
        "bts_daily": [dict(r._mapping) for r in flights] or fallback["bts_daily"],
        "benchmark": cache("queue-benchmark.json") or fallback["benchmark"],
        "notice": "Historical public context; operational checkpoint configuration is modelled for the MVP, not BKK telemetry.",
    }
