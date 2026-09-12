# Airport TimeTwin

**Predictive Airport Flow & Passenger Journey Decision Platform**

A runnable airport decision-support MVP: anticipate a queue, compare interventions across two checkpoints, choose a feasible action, and translate the model into accessible passenger guidance.

**Simulated MVP Result — Not actual airport performance.** All operational inputs are synthetic. The terminal is illustrative and does not depict Suvarnabhumi's infrastructure. No live airport equipment is controlled.

## Run

Local preview without Docker: `./run-local.sh` → **http://localhost:5173**. This convenience mode uses SQLite and requires Python/uv and Node.js. PostgreSQL Compose is the intended stack; see verification notes for checks executed on this machine.


```sh
python3 scripts/configure_local.py
make up
```

Open **http://localhost:8080**. API documentation: **http://localhost:8000/docs**. Docker Desktop must be running. `make down` preserves the PostgreSQL volume.

For development and individual services see [deployment](docs/deployment.md).

## Problem, solution, and why now

Passenger journey uncertainty accumulates across multiple processes. Existing airport intelligence can provide a foundation for a separate decision layer: simulate the consequences of an intervention before an operator chooses it. TimeTwin demonstrates that layer with reproducible public/synthetic inputs, transparent queue mechanics, and auditable human decisions. It makes no claim about a named vendor's missing capabilities or proven business outcomes.

**Observe → Predict → Simulate → Optimize → Recommend → Act → Measure → Learn**

React/TypeScript → FastAPI → deterministic forecasting, FIFO cohort simulation, NetworkX routing, scoring → PostgreSQL audit and operational entities. A bounded no-LLM copilot explains structured outputs; it is not a source of operational facts.

## Features

- Airport future map: Now, +15, +30, +60; queue, lanes, risk, assumption bands.
- Four network-aware interventions, configurable what-if controls, transparent weighted recommendations.
- Human accept/reject/override, scenario version checks, audit snapshots and synthetic outcome measurement.
- Mobile Safe Time, accessible routing, gate-change replan, Thai-ready passenger labels.
- Stale-data blocking, role-gated demo mutations, validated input and local rate limit.
- Normalized PostgreSQL schema, Alembic, seed CSVs, public context fetch adapters, chronological ML baseline evaluation.

## Demo

Reset → Start peak event → Compare interventions → Accept action → inspect Decision log. Then Passenger journey → Reset → Simulate gate change. See [demo script](docs/demo-script.md) and [three-minute pitch](docs/pitch.md).

The assumed peak profile yields 12→39 minutes at Security A; the default combined intervention improves the simulated network result. Accessible passenger Safe Time changes 34→11 in the separate reset gate-change vignette. All benefits are calculated, not measured at an airport.

## Data and evaluation

[Source matrix](docs/data-sources.md) distinguishes REAL_PUBLIC, SYNTHETIC, DERIVED, SIMULATED, and ASSUMPTION. Optional OurAirports, Open-Meteo and OpenSky context is cached separately and never used as a substitute for passenger or queue data. Default demo requires no public API.

```sh
cd backend
uv sync
uv run python ../scripts/generate_synthetic.py
uv run --extra ml python ../ml/evaluation/evaluate.py
```

[Evaluation report](docs/evaluation.md) compares persistence, moving average, fluid, linear and random forest models at 15/30/60 minutes. It uses a chronological split and embargo. No ML model is promoted. Confidence is heuristic and uncalibrated; independent real telemetry validation is outstanding.

KPIs include average/P95 remaining cohort wait, peak queue, throughput, utilization, passenger-minutes saved, Safe Time and an explicitly assumed missed-boarding risk proxy. [Acceptance criteria](docs/acceptance.md) are MVP targets, not aviation standards.

## Tests

```sh
make test
cd frontend
npx playwright install chromium
npm run test:e2e
```

Browser tests require the stack. See [verification](docs/verification.md) for actual execution results.

## Design and delivery documents

- [Delivery index](docs/deliverables.md) and [UX design](docs/ux-design.md)
- [Architecture and component diagram](docs/architecture.md)
- [Database ER diagram](docs/er-diagram.md), [schema SQL](schema.sql), [data dictionary](docs/data-dictionary.md)
- [REST API](docs/api.md)
- [Assumptions and known limitations](docs/assumptions.md)
- [Security and privacy](docs/security.md)
- [Deployment and production roadmap](docs/deployment.md)

## Limits and privacy

Two checkpoints have dynamic queues; other process nodes use assumed routing times. Individual flight demand assignment, real sensor integration, full causal attribution, calibrated uncertainty, distributed operations, full Thai localization and production identity are not implemented. The demo uses an intentionally forgeable role header and binds locally. Non-demo mutations fail closed. Do not expose this as a production-authenticated service.

Only anonymous synthetic passenger records are stored. Production PDPA governance, purpose/retention controls and appropriate legal review remain required before using personal data. Future integrations with AODB, FIDS, DCS, BHS/BRS, flow sensors and related systems are conceptual, pending authorized APIs and airport validation.
