# Verification record

Verification date: 2026-09-13 (Asia/Bangkok). All scenario benefits are simulated.

| Check | Actual result |
|---|---|
| Python Ruff lint and format | Passed |
| Backend behavior and API tests | 16 passed (SQLite isolation) |
| Frontend ESLint and Prettier | Passed |
| Frontend unit/API-client tests | 2 passed |
| TypeScript and Vite production build | Passed |
| Browser: full demo and action audit | Passed against production frontend and PostgreSQL API |
| Browser: mobile passenger, gate change, stale data | Passed at 390 × 844 |
| Browser: selectable airport map, horizons, zoom and what-if | Passed |
| Browser: source provenance and model attribution | Passed with explicit public/synthetic and causal-assumption labels |
| Synthetic outcome persistence | PostgreSQL measurement and signed error verified |
| Browser console | No page errors in the end-to-end demo |
| Responsive overflow | No horizontal overflow in tested passenger mobile viewport |
| SQLite Alembic migration | Passed |
| PostgreSQL concurrent decisions | Exactly one accept succeeds (200); duplicate returns 409 |
| Public ingestion | OurAirports, Open-Meteo, OpenSky retrieved 2026-09-12 around 17:07 UTC; source metadata retained |
| npm dependency audit | 0 reported vulnerabilities |
| CLI reproducible demo | Combined action selected; 10,770.72 passenger-minutes saved; separate accessible gate vignette 34→11 |
| PostgreSQL / Docker | Build/start passed; PostgreSQL migration, normalized tables and JSONB metadata verified; API healthy |

Simulated MVP Result — Not actual airport performance.

The default peak comparison has positive network passenger-minutes saved and lower cohort P95 than No Action. The terminal geometry, rates, staffing, demand, risk budgets and uncertainty bands are assumptions. Synthetic ML evaluation is in evaluation.md; no model is promoted. Some horizon/accuracy targets are not met.

Test screenshots: [Operations](screenshots/operations-desktop.png), [What-if](screenshots/what-if-desktop.png), [Passenger mobile](screenshots/passenger-mobile.png).

Known test environment warnings: upstream Starlette/httpx test adapter deprecations; no application assertion failure. Production authentication, real airport integration, WCAG certification, load testing, retention enforcement and high availability are outside the verified MVP.

## Relocated project / expanded aviation experience — 2026-09-13

Verified from the Desktop project directory:

- Backend: 18 passing tests, including actual departure counter conservation.
- Frontend unit: 2 passing tests; ESLint and production TypeScript/Vite build pass.
- Browser: 10 passing tests on the Docker frontend, including automated timer
  progression, manual demo controls, flight details, evaluation, comparison
  reveal, keyboard modal dismissal, mobile overflow and reduced motion.
- PostgreSQL Alembic current: 001 (head).
- Live integration: concurrent acceptance 200/409; persisted synthetic
  measurement; Safe Time 34 → 11; stale action blocking; reset.
- Local Markdown links and git diff whitespace checks pass.
- Screenshots under docs/screenshots include desktop/mobile landing and product.

This verifies a runnable expanded MVP, not airport production integration or
achievement of all aspirational forecast accuracy targets. See acceptance-results.json.

## Executive fidelity and public preview — 2026-09-13

Final local browser suite: 13 passed. Public URL suite: 2 passed (full decision
journey and landing/forecast/copilot). Public health and team report: HTTP 200.
A disk-full failure was diagnosed and unused build cache reclaimed (5.559 GB),
without removing database volumes. PostgreSQL recovered and the full suite was
rerun successfully. Public preview limitations and operational instructions are
in [team handoff](team-handoff.md).


## Landing language update
- Added Thai / English controls covering all landing page text, document language/title, and persisted selection. Other application routes retain their existing language.
- Frontend build and lint passed; public browser checks passed for switching, reload persistence, and 390px mobile overflow.
- Built assets copied to the running frontend container; source is included in subsequent Docker builds.
