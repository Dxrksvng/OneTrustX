"""Streaming business-field completeness / duplicate checks. No fabricated missing records."""

import csv, json, hashlib
from datetime import datetime, timezone
from collections import Counter
from common import ROOT

PROV = {
    "source_type",
    "source_name",
    "source_url",
    "retrieved_at",
    "source_geography",
    "source_period",
    "license_or_terms",
    "checksum",
}
report = []
for path in sorted((ROOT / "data/normalized").glob("*.csv")):
    with path.open() as f:
        reader = csv.DictReader(f)
        keys = [k for k in reader.fieldnames if k not in PROV]
        seen = set()
        missing = Counter()
        count = 0
        duplicates = 0
        dates = []
        sample = []
        for row in reader:
            count += 1
            for k in keys:
                if row[k] in ("", "None", "null", "-"):
                    missing[k] += 1
            digest = hashlib.sha256(
                json.dumps([row[k] for k in keys]).encode()
            ).digest()
            if digest in seen:
                duplicates += 1
            seen.add(digest)
            date = next(
                (
                    row.get(k)
                    for k in [
                        "FlightDate",
                        "time",
                        "date",
                        "report_period",
                        "this_period",
                    ]
                    if row.get(k)
                ),
                None,
            )
            if date:
                dates.append(date)
            if len(sample) < 2:
                sample.append(row)
        if not count:
            continue
        first = sample[0]
        report.append(
            dict(
                dataset=path.stem,
                records=count,
                date_from=min(dates) if dates else None,
                date_to=max(dates) if dates else None,
                missing_percent=round(
                    sum(missing.values()) / (count * len(keys)) * 100, 3
                ),
                missing_by_field={
                    k: round(v / count * 100, 3) for k, v in missing.items()
                },
                duplicate_percent=round(duplicates / count * 100, 3),
                source_name=first["source_name"],
                source_type=first["source_type"],
                source_geography=first["source_geography"],
                source_url=first["source_url"],
                retrieved_at=first["retrieved_at"],
                checksum=first["checksum"],
                granularity="FLIGHT"
                if "bts" in path.stem
                else "HOUR"
                if any(x in path.stem for x in ["weather", "cbp"])
                else "MIXED DAY/MONTH"
                if "caat" in path.stem
                else "AIRPORT",
                sample=sample,
            )
        )
output = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "datasets": report,
    "limitations": [
        "Weather is historical model/reanalysis data from Open-Meteo, not an airport METAR sensor observation.",
        "CBP is US immigration; it cannot validate BKK security service rates directly.",
        "BTS US flights are never shown as BKK schedules.",
        "CAAT daily workbook values are preliminary. Missing dashes stay missing; monthly template dates are normalized to month starts.",
        "No production BKK checkpoint telemetry is available in this repository.",
        "TSA endpoint returned HTTP 403; no TSA observations are fabricated.",
        "CAAT current SharePoint export requires access; historic public workbooks are used instead.",
    ],
}
(ROOT / "data/cache/data-quality.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2)
)
lines = [
    "# Data Quality Report",
    "",
    output["generated_at"],
    "",
    "Source observations, not airport deployment claims. Missing percentages cover business fields; provenance fields excluded. Duplicate rates are within each source extract; revisions across CAAT extracts are retained with lineage and resolved in API aggregates.",
    "",
    "| Dataset | Records | Period | Geography | Missing % | Duplicate % |",
    "|---|---:|---|---|---:|---:|",
]
for r in report:
    lines.append(
        f"| {r['dataset']} | {r['records']:,} | {r['date_from']} — {r['date_to']} | {r['source_geography']} | {r['missing_percent']} | {r['duplicate_percent']} |"
    )
lines += ["", "## Source lineage"]
for r in report:
    lines += [
        "",
        f"- {r['dataset']}: {r['source_url']} · retrieved {r['retrieved_at']} · SHA256 `{r['checksum']}`",
    ]
lines += ["", "## Limitations"] + ["- " + s for s in output["limitations"]]
(ROOT / "docs/data-quality-report.md").write_text("\n".join(lines) + "\n")
print([(r["dataset"], r["records"]) for r in report])
