# Data sources and provenance matrix

Documentation checked 2026-09-12. Retrieval timestamps are captured by `scripts/fetch_public_data.py`; a documentation check is not a dataset retrieval. The default app consumes deterministic synthetic data, without public-network dependencies.

| Dataset / value | Provenance | Source / boundary |
|---|---|---|
| Airport metadata fetched by adapter | REAL_PUBLIC | [OurAirports](https://ourairports.com/data/); public-domain airport CSV; no guarantee of accuracy |
| Optional weather forecasts | REAL_PUBLIC | [Open-Meteo](https://open-meteo.com/en/docs); model forecasts, not airport sensor observations; preserve units and timestamps |
| Optional aircraft state vectors | REAL_PUBLIC | [OpenSky REST API](https://openskynetwork.github.io/opensky-api/rest.html); position, speed, callsign, heading, airborne status where available |
| Airports fixture | SYNTHETIC | TWT/ZZTW are illustrative fixture identifiers, not asserted registered codes; approximate coordinates are assumptions |
| Flights, queues, lanes, passengers, baggage, handling, gates | SYNTHETIC | Seeded local records; never described as actual airline or airport records |
| Terminal topology, rates, deadlines, staff limit | ASSUMPTION | Illustrative directed layout and operating assumptions |
| Queue forecasts, intervention outcomes, Safe Time, KPI proxies | SIMULATED | Deterministic engine; every response/UI carries the MVP result notice |
| Weather risk score or transformed feature | DERIVED | Must retain source lineage and formula; synthetic seed risk remains synthetic |
| Driver relationships and confidence | ASSUMPTION | Operational mechanism assumptions; no causal proof or calibrated probability |

OpenSky is not used for passenger counts, boarding status, complete commercial schedules, cancellation reasons, or queues. Public adapter failures keep the last cache with a stale marker, or return an empty SYNTHETIC fallback; they never relabel synthetic data as real. Public context is separate from the operational simulation and cannot silently raise operational confidence.

Cached raw public JSON includes `source_type`, `source_url`, `retrieved_at`, `stale`, and `payload`. Recheck access terms, quotas, attribution, credentials, and commercial permissions before deployment. OpenSky token is optional through the environment; no token is bundled. Open-Meteo coordinates in the request are explicit approximate demo assumptions.

No SKY ICT product capability is asserted. Airport TimeTwin is positioned as a decision and simulation layer that can sit on top of existing airport intelligence infrastructure. It does not claim to replace Smart Flows.
