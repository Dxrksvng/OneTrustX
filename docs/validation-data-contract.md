# One TrustX validation data contract

The repository now includes a multi-scenario, multi-seed synthetic validation pack:

- `data/cache/onetrustx-validation-runs.csv`: 5,600 condition runs across 14 scenarios and 100 seeds
- `data/cache/onetrustx-validation-summary.csv`: median, P25 and P75 for each scenario/condition
- `data/cache/onetrustx-validation-manifest.json`: dataset identity and limitations

Every condition uses the same scenario and seed. This makes the comparison paired and avoids giving one condition an easier episode. The pack tests repeatability, sensitivity to scenario type and the direction of the workflow effect. It does not establish airport accuracy or financial benefit.

## Scenario families (v3)

Scenarios S1-S8 are the original operational set (normal turnaround, baggage bottleneck, gate conflict, weather, multi-factor, data conflict, missing/late data, scale test). S9-S14 are a disaster/compound family defined in [`data/scenarios/scenario_library.json`](../data/scenarios/scenario_library.json): flood+baggage backlog (calibrated against the Sept 2026 Bangkok flood/Thai Airways baggage case, see sources in that file), geopolitical airspace closure, terminal fire, health-screening disruption, our own BHS/trust-pipeline outage, and terminal power disruption. Each scenario in the library carries its own provenance tier (REAL_PUBLIC facts cited by URL, BENCHMARK industry figures, or ASSUMPTION operating parameters) — these are design inputs for the generator, not claims about a specific airport's or airline's real operations.

Every episode also carries a deterministic, condition-independent `failure_injected`/`failure_type` draw (MISSING_EVENT, LATE_EVENT, DUPLICATE_EVENT, CONTRADICTORY_EVENT, STALE_SOURCE) and a `ground_truth_state_match` field: whether the condition's resulting shared state matches the scenario's defined ground truth. On the failure-injected subset, BASELINE's median `ground_truth_state_match` is 0.0 (no reconciliation mechanism exists to prefer ground truth over a stale/contradictory source) and ONE_TRUSTX_AI's is 0.91 — this is a *modelled reconciliation-success proxy*, not a measured detection-accuracy percentage from production data, and must not be cited as "accuracy" without that caveat.

## To measure real usage

An authorized airport data owner must provide de-identified event records with at least:

`episode_id`, `event_id`, `source_system`, `stakeholder_type`, `event_type`, `event_time`, `ingestion_time`, `entity_id_hash`, `ground_truth_label`, `decision_time`, `action`, and `observed_outcome`.

The evaluation must then:

1. Freeze the schema, source permissions and label rules before looking at test results.
2. Split episodes chronologically into development, validation and test periods.
3. Keep a pre-One-TrustX baseline and the same events for the proposed workflow.
4. Report sample count, missingness, median/P90 latency, precision/recall/F1, calibration, false alarms and confidence intervals.
5. Measure operational outcomes such as readiness delay, baggage exception resolution and coordination time only when an independently recorded outcome exists.
6. Start in shadow mode with human review; do not claim causal savings from an uncontrolled before/after comparison.

Until those records exist, the CSV pack must be described as **synthetic prototype validation**, never as real airport performance.
