# Public-data cache
Run from the repository root with `backend/.venv/bin/python`. Install optional ingestion/ML dependencies with `cd backend && uv sync --extra ingestion --extra ml`.

1. `scripts/data/fetch_ourairports.py`
2. `scripts/data/fetch_caat.py` and `scripts/data/fetch_caat_history.py`
3. `scripts/data/fetch_bts.py`, `scripts/data/fetch_cbp.py`, `scripts/data/fetch_weather.py`
4. `scripts/data/normalize_history.py` (includes cached UK CAA normalization)
5. `scripts/data/build_quality_report.py`
6. `scripts/data/calibrate_benchmarks.py`
7. `docker compose --env-file .env -f infra/docker-compose.yml exec api /app/.venv/bin/python -m app.ingest_public`

Inspect each fetch script's configured period before scheduled refresh. AOT and TSA connectors record unavailability; they do not synthesize observations. UK CAA files currently have source manifests and normalization but acquisition must use the exact official download URLs in those manifests. There is no account-gated dependency.

Raw source SHA256, URL, retrieval timestamp and geography are preserved. Cache checksum mismatch stops acquisition for review. PostgreSQL import is idempotent per source revision. CAAT overlapping releases are retained; the API chooses the latest published extract for each date/airport/category. Completeness reports describe source rows, not long-form SQL metric rows.

Open-Meteo historical weather is reanalysis/model data published by that provider, not direct airport sensor telemetry. CBP is US immigration, not security. The empirical benchmark does not calibrate BKK service capacity and no candidate is promoted into the operational simulator.
