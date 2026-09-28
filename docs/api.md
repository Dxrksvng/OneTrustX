# REST API

Interactive OpenAPI: http://localhost:8000/docs. Machine schema: `/openapi.json`. Generated endpoint schemas are authoritative for field constraints. JSON bodies reject unknown properties. Mutations require `X-Demo-Role: AIRPORT_OPERATOR` or `ADMIN`; this is local demo auth, not production security.

| Method | Endpoint | Contract |
|---|---|---|
| GET | /health | Database readiness and modes |
| GET | /api/overview | Versioned scenario, checkpoint forecasts, assumptions, passenger view; persists forecast snapshot |
| GET | /api/public/context | Labelled, freshness-checked public cache; never passenger intelligence |
| GET | /api/flights | SYNTHETIC flight fixtures |
| GET | /api/flights/{id} | One flight or 404 |
| GET | /api/checkpoints | Two simulated security checkpoints |
| GET | /api/checkpoints/{id}/status | Queue, lanes and horizons |
| GET | /api/checkpoints/{id}/forecast | +15/+30/+60 with uncertainty bands |
| GET | /api/passenger-flow | Seeded historical synthetic flow, chronological |
| GET | /api/airport/map | Directed illustrative graph; accessible query flag |
| GET | /api/airport/risk | Forecast risks |
| GET | /api/root-causes | Model-only driver attribution with primary/secondary contributions |
| POST | /api/simulation | `lanes:0..5, redirect:0..0.3, staff:0..4, flight_delay:0..30` |
| POST | /api/simulation/intervention | Alias of simulation |
| GET | /api/recommendations | Four comparable options, score/reason, persistent recommendation IDs |
| POST | /api/recommendations/score | Nonnegative weights: wait, minutes, risk, staff, walking, cost |
| POST | /api/recommendations/{id}/accept | Decision body, default accept |
| POST | /api/recommendations/{id}/decision | `decision:accept/reject/override, reason:string`; override requires intervention |
| GET | /api/passenger/{id}/journey | accessible, current, weight=distance/travel_time/congestion |
| GET | /api/passenger/{id}/safe-time | Alias of journey |
| POST | /api/copilot/query | `question:string`; structured fallback explanation |
| GET | /api/kpi | Network wait, P95, queue, utilization, throughput, risk proxy |
| GET | /api/audit | Latest 100 audit entries with full event snapshots |
| GET | /api/results | Predicted/observed synthetic intervention outcomes |
| POST | /api/results/{id}/measure | `actual_average_wait:0..600, source_type:SIMULATED`; append once |
| POST | /api/demo/event | reset/peak/lane-closure/gate-change/stale/refresh |

Errors: 403 missing mutation role; 404 missing entity; 409 stale, duplicate or superseded action; 422 invalid/infeasible input; 429 rate limited; 503 unready database or unconfigured non-demo identity. GET analytics may persist predictions: this is intentional for MVP auditability, and should move to scheduled materialization at scale.

Every simulated response is labelled. UUID IDs identify predictions, recommendations, events and results. Opaque fixture strings identify synthetic flights and passengers. A decision never commands an airport system. Decision approval and state change commit in one PostgreSQL transaction with a row lock.

Additional experience endpoints:

- `GET /api/flights/{id}/operations`: flight plus stored ground handling,
  baggage events and gate events; 404 for an unknown flight.
- `GET /api/evaluation`: bundled offline synthetic evaluation report; 503 if missing.

Simulation series expose `arrivals_a`, `arrivals_b`, `served_a`, `served_b` and
`served` (actual simulated departures that minute, not available capacity).
