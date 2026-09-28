"""Bounded, checksummed public downloads. Failure never fabricates observations."""

import csv, hashlib, json, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = ROOT / "data/external"


def fetch(source, url, name, geography, period, terms, limit=150_000_000, body=None):
    folder = EXTERNAL / source
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / name
    meta = target.with_suffix(target.suffix + ".provenance.json")
    if target.exists() and meta.exists():
        cached = json.loads(meta.read_text())
        if hashlib.sha256(target.read_bytes()).hexdigest() == cached.get("checksum"):
            return target
        raise ValueError(f"Cache checksum mismatch: {target}; review before replacing")
    record = dict(
        source_name=source,
        source_url=url,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        source_geography=geography,
        source_period=period,
        license_or_terms=terms,
        source_type="REAL_PUBLIC",
    )
    temporary = target.with_suffix(target.suffix + ".part")
    try:
        with urllib.request.urlopen(
            urllib.request.Request(
                url,
                headers={
                    "User-Agent": "AirportTimeTwin/0.2 public-data research (one-time local cache)",
                    "Content-Type": "application/json",
                },
                data=json.dumps(body).encode() if body else None,
            ),
            timeout=60,
        ) as r:
            if "login." in r.url or "signin" in r.url:
                raise ValueError("Authentication required; not downloaded")
            size = 0
            digest = hashlib.sha256()
            with temporary.open("wb") as out:
                while chunk := r.read(1024 * 1024):
                    size += len(chunk)
                    if size > limit:
                        raise ValueError("Download exceeds configured byte limit")
                    digest.update(chunk)
                    out.write(chunk)
            if (
                target.suffix in {".zip", ".xlsx"}
                and temporary.read_bytes()[:2] != b"PK"
            ):
                raise ValueError("Expected ZIP/XLSX but received a non-data response")
            record["request_parameters"] = body
            record.update(
                checksum=digest.hexdigest(),
                bytes=size,
                status="CACHED",
                content_type=r.headers.get("Content-Type"),
            )
        temporary.replace(target)
        meta.write_text(json.dumps(record, ensure_ascii=False, indent=2))
        print(source, name, size, flush=True)
        return target
    except Exception as e:
        temporary.unlink(missing_ok=True)
        record.update(status="UNAVAILABLE", source_type=None, error=str(e))
        meta.write_text(json.dumps(record, ensure_ascii=False, indent=2))
        print(source, name, str(e), flush=True)
        return None


def provenance(path):
    return json.loads(path.with_suffix(path.suffix + ".provenance.json").read_text())


def normalized(name, rows, source):
    folder = ROOT / "data/normalized"
    folder.mkdir(exist_ok=True)
    path = folder / (name + ".csv")
    count = 0
    with path.open("w", newline="") as f:
        writer = None
        for row in rows:
            row = {
                **row,
                "source_type": "REAL_PUBLIC",
                "source_name": source["source_name"],
                "source_url": source["source_url"],
                "retrieved_at": source["retrieved_at"],
                "source_geography": source["source_geography"],
                "source_period": source["source_period"],
                "license_or_terms": source["license_or_terms"],
                "checksum": source["checksum"],
            }
            if writer is None:
                writer = csv.DictWriter(f, fieldnames=list(row))
                writer.writeheader()
            writer.writerow(row)
            count += 1
    print(name, "normalized", count, flush=True)
    return path
