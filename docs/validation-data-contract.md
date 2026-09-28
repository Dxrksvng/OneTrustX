# One TrustX validation data contract

The repository now includes a multi-scenario, multi-seed synthetic validation pack:

- `data/cache/onetrustx-validation-runs.csv`: 3,200 condition runs across 8 scenarios and 100 seeds
- `data/cache/onetrustx-validation-summary.csv`: median, P25 and P75 for each scenario/condition
- `data/cache/onetrustx-validation-manifest.json`: dataset identity and limitations

Every condition uses the same scenario and seed. This makes the comparison paired and avoids giving one condition an easier episode. The pack tests repeatability, sensitivity to scenario type and the direction of the workflow effect. It does not establish airport accuracy or financial benefit.

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
