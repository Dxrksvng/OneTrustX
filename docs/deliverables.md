# MVP delivery index

Simulated MVP Result — Not actual airport performance.

| Requested deliverable | Implementation / artifact | Scope |
|---|---|---|
| Working source code | backend/app and frontend/src | Runnable local MVP |
| Docker Compose | infra/docker-compose.yml | PostgreSQL, API, nginx |
| PostgreSQL schema | schema.sql, backend/migrations | Frozen initial SQL; Alembic |
| Seed datasets | data/synthetic, data/seeds | Anonymous SYNTHETIC fixtures |
| Synthetic generator | scripts/generate_synthetic.py | Seed 42, reproducible CSVs |
| Public ingestion | scripts/fetch_public_data.py | OurAirports, Open-Meteo, OpenSky contextual caches |
| REST API | backend/app/main.py, /docs | Validated inputs, generated OpenAPI |
| Queue prediction | backend/app/engine.py | Minute-step fluid forecasts at 15/30/60 |
| Simulation | backend/app/engine.py | Two security queues, FIFO cohorts, horizon drain |
| What-if simulator | What-if lab | Lanes, redirect, staff sensitivity and wave delay |
| Recommendation | compare() | Configurable weighted score, reserve staff constraints |
| Safe Time | journey() | Deadline minus processing/walking/buffer |
| Airport graph | graph(), /api/airport/map | Directed, accessible routes and multiple weights |
| Operations dashboard | Airport now / Operations control | Future map, model attribution, actions |
| Passenger mobile web | Passenger journey | Gate changes, step-free route, status/CTA |
| AI copilot | /api/copilot/query | Structured no-LLM fallback; bounded topics |
| Automated tests | backend/tests, frontend/src tests, frontend/e2e | Unit, API, desktop/mobile and live concurrency |
| Architecture diagram | architecture.md | Mermaid component/data flow |
| ER diagram | er-diagram.md | Generated from normalized schema |
| Data dictionary | data-dictionary.md | Fields, units, relationships, provenance |
| API documentation | api.md, /docs, /openapi.json | Endpoints and error contracts |
| Evaluation report | evaluation.md, evaluation-results.json | Chronological synthetic baseline/candidate comparison |
| Security/privacy | security.md | Demo RBAC, data minimization, production gaps |
| Deployment roadmap | deployment.md | Shadow/support/approval/automation maturity |
| Demo script | demo-script.md, scripts/run_demo.py | Reproducible operator and passenger vignettes |
| Three-minute pitch | pitch.md | Honest simulated impact narrative |
| KPI dashboard | Dashboard metrics, what-if options, decision measurement | Wait/P95/queue/throughput/utilization/time saved/risk proxy |
| Known limitations | assumptions.md | Model scope, uncertainty, auth, integrations |
| Future roadmap | deployment.md | Authorized airport adapters and independent validation |

The root-cause graph now includes primary/secondary contributions from a two-factor model Shapley decomposition. These percentages explain the simulator, not causal evidence about an actual airport.

Scope boundaries remain explicit: live protected airport integrations, individual crowd/discrete-event microsimulation, full terminal geometry, empirical causal validation, calibrated flight-specific missed-boarding probabilities, advanced virtual-queue/boarding-hold execution and production identity are not implemented. They are not required for the demonstrated local decision loop and are not represented as deployed capabilities. Some synthetic evaluation targets, especially 60-minute MAE, remain unmet; no ML candidate is promoted.
