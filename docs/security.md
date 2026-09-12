# Security and privacy

The MVP contains only anonymous synthetic passenger identifiers; no passport, national ID, names, contact details, face embeddings, or personal itineraries. Its synthetic itinerary rows are not real personal data.

Local-only Compose binds ports to 127.0.0.1. Secrets come from environment variables; `.env` is ignored. Use a unique local PostgreSQL password. Database persistence stays in a named Docker volume. API and frontend images run as non-root users. Exact CORS origins are configured. Pydantic validates bounds and rejects unknown fields. Process-local rate limit: 300 requests/minute per client address; this is a demo safeguard, not a distributed gateway.

Demo RBAC allows AIRPORT_OPERATOR and ADMIN to mutate; VIEWER, AIRLINE_OPERATOR, and GROUND_HANDLER are read-only. The role header is intentionally forgeable: never expose this demo authentication to the internet. Setting DEMO_MODE=false disables mutations until a production identity provider is installed. Reads contain synthetic records only. Production needs OIDC/JWT validation, tenant/airport scope, per-entity authorization, passenger ownership, centralized rate limits, secure TLS, secret rotation, and restricted audit access.

Accept/reject/override requires a reason. Snapshots contain input versions, engine outputs and provenance; audit includes actor, decision, action and measurement error. Stale data blocks recommendation acceptance and custom simulation. A version guard prevents old recommendations from applying after another action. Double submission returns 409. No operational integration or automatic actuation exists, so service failure cannot stop airport operations.

PDPA is a production governance workstream, not a claim of compliance. Before using personal data: obtain appropriate legal review, define purpose and lawful basis, minimize fields, set retention periods, implement access/erasure workflows as applicable, evaluate processors/transfers, and establish incident response. No legal conclusions are made by this MVP.

Production retention, high availability, backup restores, threat modeling, intrusion monitoring and penetration testing are not validated. Never publish this local demo as a secure multi-user production system.
