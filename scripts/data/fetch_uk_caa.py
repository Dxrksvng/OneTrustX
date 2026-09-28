import json
from common import ROOT, fetch

if __name__ == "__main__":
    for meta in sorted((ROOT / "data/external/uk_caa").glob("*.csv.provenance.json")):
        r = json.loads(meta.read_text())
        fetch(
            "uk_caa",
            r["source_url"],
            meta.name.removesuffix(".provenance.json"),
            r["source_geography"],
            r["source_period"],
            r["license_or_terms"],
        )
