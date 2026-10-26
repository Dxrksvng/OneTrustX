# ADR: Disaster/compound scenario dataset + Demo/Prototype track tagging

2026-10-03

## What changed

- Added `data/scenarios/scenario_library.json`: 6 new disaster/compound scenario definitions (flood+baggage backlog, geopolitical airspace closure, terminal fire, health-screening disruption, our own BHS/trust-pipeline outage, terminal power disruption), each with a causal chain, provenance tier, source citations, and explicitly tagged ASSUMPTION parameters.
- Extended `scripts/experiments/generate_validation_pack.py` (v2 → v3) with scenarios S9–S14 wired to that library, plus a deterministic `failure_injected`/`failure_type` draw (missing/late/duplicate/contradictory/stale) and a `ground_truth_state_match` field, held identical across all 4 conditions per (scenario, seed) for a paired comparison. Regenerated `data/cache/onetrustx-validation-*` (5,600 episodes, 14 scenarios).
- Added `data/dataset_manifest.json` tagging every file under `data/` as DEMO track (REAL_PUBLIC, `data/external` etc.) or PROTOTYPE track (SYNTHETIC/SIMULATED, `data/synthetic`, `data/scenarios`, `data/cache` etc.), per the two-phase language on `SKY .pdf` page 2.
- Updated `docs/data-sources.md`, `docs/evaluation.md`, `docs/validation-data-contract.md` to reference the above.

## Why

The user is using this dataset for a real company hackathon submission and does not want results to deviate from what `SKY .pdf` claims. Auditing the deck against the repo found two separate problems:

1. **Unbacked claims.** The deck's Impact slide (86% Risk Detection Accuracy, 100% AI Recommendation Accuracy, 100% Data Consistency, 117.39B THB/3yr, the 2025–2030 loss curve) trace to no script, model, or dataset anywhere in the repo — they exist only in the deck. The repo's own measured numbers (61.0% coordination-time reduction, 78.0% reconciliation-time reduction, 85.7% event verification, 100% traceability, 50% delay-risk-proxy reduction) are a *different* set of metrics, already honestly labelled synthetic.
2. **Scenario coverage.** The existing 8-scenario validation pack covers operational disruption types but not the disaster-class events the user wants covered explicitly: flood/baggage backlog (a real Sept 2026 Bangkok case), war/airspace closure, fire, pandemic/health screening, and — the user's specific concern — damage to **our own** baggage-tracking/trust pipeline, not just the airport's systems.

## What's affected

- `ground_truth_state_match` on the failure-injected subset (1,784 of 5,600 episodes) is the closest the repo now comes to a defensible "risk detection" number: BASELINE median 0.0, ONE_TRUSTX_AI median 0.91. This is still a **modelled reconciliation-success proxy from a generator formula**, not a measured detection rate against real labelled incidents — it must be cited with that caveat, never as "86% accuracy."
- All previously-cited percentages in `docs/evaluation.md` (61.0%/78.0%/74%/100%/85.7%/50%) are unchanged by this expansion: each condition's reduction is a fixed multiplier of that episode's own baseline, so adding scenarios changes absolute seconds, not the cited ratios. Verified by recomputation after regenerating the pack.
- The deck's AI-Recommendation-Accuracy (100%), Data-Consistency (100%), and the 117.39B THB loss-benchmark curve remain **unbacked** — explicitly flagged as such in `docs/evaluation.md` and `data/dataset_manifest.json`'s `known_gap` field, pending real labelled outcomes per `docs/validation-data-contract.md`.

## What's next (not done in this pass)

- A cost model that turns the measured reductions into a THB figure, with an explicit, auditable formula (CAAT passenger volume × SITA $260/bag benchmark × measured delay-risk-proxy reduction), so the deck's financial claim either gets replaced by a derived-and-labelled number or is explicitly retired.
- A real Data-Consistency metric computed from `trust_service.py`'s existing `data-consistency` KPI definition (currently defined but not emitted by the validation pack).
- If real airport/ground-handler telemetry becomes available, swap the scenario library's ASSUMPTION parameters for calibrated ones per `docs/validation-data-contract.md`.
