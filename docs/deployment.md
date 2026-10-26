# Deployment and integration roadmap

## Local Compose

1. Install Docker Desktop and start its daemon.
2. From repository root run `python3 scripts/configure_local.py` to create an ignored `.env` with a generated local database password. Existing files are preserved.
3. Run `make up`. Compose starts PostgreSQL, applies Alembic migration 001, seeds once, and starts FastAPI and nginx.
4. Open http://localhost:8080 and http://localhost:8000/docs.
5. Run `make down` to stop without deleting the database volume.

Do not run `docker compose down -v` unless intentionally discarding all local data. Reset Demo preserves audit history; it does not reset storage.

## Development

Backend: `cd backend && uv sync && uv run alembic upgrade head && uv run uvicorn app.main:app --reload` (SQLite default for convenience; set DATABASE_URL to PostgreSQL for parity). Frontend: `cd frontend && npm ci && npm run dev`.

Tests: `make test`; browser tests require a running stack: `cd frontend && npx playwright install chromium && npm run test:e2e`.

Synthetic exports: `cd backend && uv run python ../scripts/generate_synthetic.py`. Evaluation: `make evaluate`. Public context fetch: `cd backend && uv run python ../scripts/fetch_public_data.py`. Public mode does not replace protected synthetic operations.

## Production maturity

| Phase | Gate | Responsibility |
|---|---|---|
| Shadow mode | Replay validated real telemetry; no advice acted on; baseline comparison and calibration | Airport data owner and operations analyst |
| Decision support | Human reviewed recommendations; safe failure and audited overrides; role-based authorization | Airport operator |
| Human-approved integration | Confirm signed command, eligibility, readiness, acknowledgement and rollback; partner sandbox testing | Authorized airport integration team |
| Controlled automation | Formal operational safety case, change control, monitoring, bounded actions and kill switch | Airport accountable authority |

Conceptual integration contracts (no protected APIs available): AODB/FIDS flight and gate events; CUPPS/CUSS/DCS processing/boarding aggregates; BRS/BHS baggage milestones; passenger validation and Smart Flow/CCTV analytics aggregated flow; gate readiness and handling events; weather; ATC/A-CDM interfaces only where authorized. These are proposed adapters, not claims of existing integrations or vendor capabilities.

Each adapter needs source timestamps, airport/terminal identity, sequence/version, units, schema version, lineage, quality flags, duplicate handling, replay checkpoints and an agreed freshness SLA. Private systems must retain their own operational continuity if One TrustX fails. Existing airport intelligence → One TrustX simulation and decision layer → operator-approved intervention → measured result → optional passenger guidance.

Before rollout: workload-test PostgreSQL, add immutable archival audit storage, OIDC, TLS, observability, backup/restore, distributed rate limiting, retention partitions, input drift monitoring and a calibrated uncertainty model. Validate routes with actual airport accessibility teams. No production-readiness claim is made.
