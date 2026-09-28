# Architecture and implementation contract

Airport TimeTwin is a decision and simulation layer above airport intelligence. It is a production-oriented demonstrator, not a deployed airport control system. Operations own action approval; passenger guidance is advisory.

```mermaid
flowchart TD
  P[Public contextual adapters: OurAirports / Open-Meteo / OpenSky] --> C[Provenance-labelled cache]
  S[Deterministic synthetic generator] --> DB[(PostgreSQL)]
  DB --> API[FastAPI / demo RBAC / validation]
  API --> F[Minute-step fluid forecast: 15 / 30 / 60]
  F --> Q[Two-checkpoint FIFO cohort simulation]
  Q --> O[Constrained weighted scoring]
  O --> H[Human accept / reject / override]
  H --> D[Versioned demo state]
  D --> F
  F --> G[Directed accessible terminal graph]
  G --> J[Passenger Safe Time and replan]
  O --> A[Audit snapshots and measurements]
  A --> E[Offline evaluation / candidate promotion gate]
  F --> X[Structured copilot fallback]
  API --> UI[React operations and passenger web]
  C --> API
```

## Components and responsibilities

| Component | Decision supported | Evidence | Failure behavior / owner |
|---|---|---|---|
| Forecast | Where to prepare capacity | Frozen synthetic arrival profile, current queue, open lanes | Mark stale; block actions; operator owns response |
| Simulator | Which feasible lane/redirect option to choose | Same cohort and horizon for every comparison | Reject invalid resource requests; retain No Action |
| Scorer | Best benefit against staffing and walking | Public formula, configurable nonnegative weights | No recommendation on stale data |
| Journey | Which eligible path to take now | Directed topology, checkpoint waits, deadline, buffer | No inaccessible path; stale warning; passenger advisory |
| Audit | Did the chosen action help? | Input/output snapshots, human reason, later synthetic observation | Persist transactionally; no automatic model promotion |
| Copilot | Explain engine results | Structured calculations only | No-LLM template layer always available |

Queue dynamics are Q(t+1)=max(0,Q(t)+arrivals−lanes×rate). Time step is one minute. Service is allocated to FIFO cohorts and drained up to 600 minutes so average/P95 waits are not silently horizon-censored; unresolved queues make an option infeasible. The initial queue is a cohort arriving at time zero, so metrics measure remaining wait, not already accrued wait.

Two security checkpoints are simulated. Other processing nodes are assumption-based routing costs, not independent capacity simulations. P95 is passenger-weighted FIFO cohort wait. Passenger-minutes saved is the difference in network queue area plus redirect walking cost. It is not a measured airport benefit. Risk is the share exceeding an assumed 35-minute checkpoint budget, not flight-specific missed-boarding probability.

Scenario time is frozen at 17:00 ICT. Wall-clock freshness is tracked independently with a five-minute threshold. Database row locking and version comparison stop duplicate/superseded decisions from silently overwriting state. Reset preserves audit history and increments the version.

## Initial delivery milestones

1. P0: normalized schema, seed, directed graph, conservation-tested queues and horizons.
2. P0: validated what-if API, resource constraints, deterministic scoring, operations interface.
3. P1: accessible Safe Time, gate changes, decision trail, measurement and KPI proxies.
4. P2: cached public context adapters, chronological baseline/ML evaluation, no-LLM copilot.
5. Verification: lint, tests, migrations, production frontend build, Docker health, desktop/mobile browser checks.

## Repository structure

```text
airport-timetwin/
  backend/app/            # ORM schema, seed, deterministic engines, FastAPI
  backend/migrations/     # Alembic
  backend/tests/          # conservation, decisions, stale-data and API tests
  frontend/src/           # React views, styles, API client
  frontend/e2e/           # browser integration and mobile tests
  data/synthetic/         # generated normalized CSVs and training history
  data/seeds/             # reproducible peak scenario
  data/raw/               # optional public cache, ignored by git
  scripts/                # ingestion, generation, seeding, demo
  ml/evaluation/          # chronological evaluation against baselines
  infra/                  # Docker Compose
  docs/                   # architecture, ERD, dictionary, evaluation, runbooks
```

Modules are intentionally small; a later service split must follow measured scaling needs. PostgreSQL is the supported Compose database; SQLite is used only for isolated tests and optional local development.

## Public-data foundation (September 2026 upgrade)

```mermaid
flowchart LR
  official[CAAT / OurAirports / Open-Meteo / BTS / CBP / UK CAA] --> fetch[Bounded scheduled ingestion]
  fetch --> raw[Checksummed offline source cache]
  raw --> normalize[CSV normalization + source-row lineage]
  normalize --> pg[(PostgreSQL public tables)]
  pg --> aggregate[Server-side historical aggregates]
  aggregate --> ui[Overview / Sources / Performance]
  assumptions[Modelled BKK checkpoint configuration] --> engine[Deterministic queue engine]
  cbp[External CBP benchmark evaluation] -. plausibility only .-> engine
  engine --> options[Simulate + compare feasible options]
  options --> human[Human approval / rejection / override]
  human --> journey[Session-scoped passenger re-plan]
  human --> audit[Idempotent decision lifecycle + replay measurement]
```

No third-party request is made by `/api/data/context` or `/api/data/catalog`. Public data provides historical context and external evaluation; it is not a substitute for missing BKK checkpoint telemetry. Current CBP analysis is concurrent hourly wait estimation, not a forward security forecast. No ML candidate is promoted.

```mermaid
erDiagram
  PUBLIC_DATASETS ||--o{ PUBLIC_OBSERVATIONS : contains
  PUBLIC_DATASETS ||--o{ PUBLIC_FLIGHTS : contains
  PUBLIC_DATASETS ||--o{ PUBLIC_QUEUES : contains
  DEMO_SESSIONS ||--o{ OPERATIONAL_EVENTS : scopes
  OPERATIONAL_EVENTS ||--o{ PREDICTIONS : explains
  PREDICTIONS ||--o{ RECOMMENDATIONS : supports
  RECOMMENDATIONS ||--o| INTERVENTION_RESULTS : measures
```

Demo event/session linkage is recorded in event metadata; public lineage uses normalized foreign keys. Session UUID is a demo isolation mechanism, not a production authentication credential.
