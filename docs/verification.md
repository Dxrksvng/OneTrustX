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
