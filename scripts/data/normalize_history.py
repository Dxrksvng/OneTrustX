"""Normalize published spreadsheet cells, preserving missing '-' and cell lineage."""

import csv, json
from datetime import datetime
from openpyxl import load_workbook
from common import ROOT, normalized, provenance


def main():
    for path in (ROOT / "data/external/caat").glob("*.xlsx"):
        w = load_workbook(path, read_only=True, data_only=True)
        meta = provenance(path)
        anchor = w["Date"]["E2"].value
        rows = []
        for sheet, metric in [("Daily PAX", "passengers"), ("Daily FMM", "flights")]:
            values = list(w[sheet].values)
            header = next((r for r in values if "BKK" in r and "HKT" in r), None)
            if not header:
                continue
            for ri, row in enumerate(values, 1):
                if len(row) > 1 and row[1] in ["Domestic", "International", "Total"]:
                    for col, airport in enumerate(header):
                        if col < 2 or not airport:
                            continue
                        value = row[col] if col < len(row) else None
                        rows.append(
                            dict(
                                date=anchor.date().isoformat(),
                                airport="TH_TOTAL" if airport == "Total" else airport,
                                category=row[1],
                                metric=metric,
                                value=value if isinstance(value, (float, int)) else "",
                                granularity="DAY",
                                source_sheet=sheet,
                                source_cell=f"{ri}:{col + 1}",
                            )
                        )
        sh = w["30-Day PAX"]
        values = list(sh.values)
        # The current date line is the last datetime row above Domestic, not the stale template row.
        domestic_index = next(i for i, r in enumerate(values) if r[0] == "Domestic")
        dates = next(
            r
            for r in reversed(values[:domestic_index])
            if any(isinstance(v, datetime) for v in r)
        )
        for ri, row in enumerate(values, 1):
            if row[0] in ["Domestic", "International", "Total"]:
                for col, date in enumerate(dates):
                    if isinstance(date, datetime):
                        rows.append(
                            dict(
                                date=date.date().isoformat(),
                                airport="TH_TOTAL",
                                category=row[0],
                                metric="passengers",
                                value=row[col]
                                if isinstance(row[col], (int, float))
                                else "",
                                granularity="DAY",
                                source_sheet="30-Day PAX",
                                source_cell=f"{ri}:{col + 1}",
                            )
                        )
        values = list(w["12-Months PAX"].values)
        dates = next(r for r in values if sum(isinstance(v, datetime) for v in r) > 5)
        for ri, row in enumerate(values, 1):
            if len(row) > 2 and row[2] in ["Domestic", "International", "Pax Total"]:
                for col, date in enumerate(dates):
                    if isinstance(date, datetime):
                        rows.append(
                            dict(
                                date=date.strftime("%Y-%m") + "-01",
                                airport="TH_TOTAL",
                                category="Total" if row[2] == "Pax Total" else row[2],
                                metric="passengers",
                                value=row[col]
                                if isinstance(row[col], (int, float))
                                else "",
                                granularity="MONTH",
                                source_sheet="12-Months PAX",
                                source_cell=f"{ri}:{col + 1}",
                            )
                        )
        normalized("caat_" + path.stem, rows, meta)
    for p in (ROOT / "data/external/uk_caa").glob("Table*.csv"):
        normalized(
            "uk_caa_" + p.stem,
            csv.DictReader(p.open(encoding="utf-8-sig")),
            provenance(p),
        )


if __name__ == "__main__":
    main()
