# Acceptance criteria

## Functional gates

- Queue balance conserves initial + incoming = processed + remaining; no negative queue or capacity.
- Deterministic peak fixture produces current wait 12 and +30 wait 39 at A.
- Default peak combined intervention has lower P95 and positive passenger-minutes saved against No Action.
- Options account for both checkpoints, walking and finite reserve staff; infeasible actions do not execute.
- Accessible routing excludes the shorter inaccessible E7 edge. Default gate-change vignette reproduces 34→11.
- Human accept, reject, override and measurement are persistent, versioned and auditable; duplicate decisions fail.
- Stale recommendations and simulations fail safely; passenger warning remains visible.
- No cloud LLM or public feed required to complete the pitch.
- UI exposes provenance, uncertainty caveat, loading/error states and a mobile passenger layout.

## Model targets (configurable MVP aspirations)

Queue MAE ≤5 minutes; congestion recall ≥80%; onset warning lead ≥15 minutes. These are not industry standards or achieved real-airport results. Evaluation reports all baselines and candidate models with chronological split and embargo. Promotion requires improvement over persistence and fluid baselines plus independent validation; no ML candidate is promoted in this release.

The sample acceptance configuration is `data/seeds/acceptance.json`. It is a review gate, not a mechanism that changes simulation outputs to pass a target.

See `verification.md` for checks actually executed and `evaluation.md` for computed synthetic results.

## Computed target assessment

Run `python3 scripts/assess_acceptance.py` after evaluation. See [acceptance-results.json](acceptance-results.json). The fluid baseline meets the configured 30-minute targets on this synthetic benchmark; 15-minute median lead (14 min) and 60-minute MAE (10.34 min) miss the sample targets. No target is silently relaxed and no ML model is promoted.
