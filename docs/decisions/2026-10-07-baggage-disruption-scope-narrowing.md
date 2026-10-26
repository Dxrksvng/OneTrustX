# ADR: Narrow One TrustX scope to Baggage Disruption Recovery, differentiate vs AODB/BRS/A-CDM

2026-10-07

## What changed

- New pitch narrative at `docs/onetrustx-pitch.md`: "Baggage Disruption Recovery" is now the hero use case, replacing the broader "One TrustX unifies every aviation stakeholder" framing.
- `data/scenarios/scenario_library.json`: `SCN-FLOOD-BAGGAGE-001` (`flood_baggage_compound`, S9) marked `hero_scenario: true` — the primary/default demo scenario, not just one of 14.
- Added updated SITA mishandled-baggage figures (2024: 33.4M bags / ~$5B; 2025, most recent: ~24M bags / ~$6.3B) with the explicit correction that these are *mishandled*, not *lost*, bags.

## Why

Post-kickoff feedback (mentor + team) identified that the prior One TrustX pitch was too broad. Checking SKY ICT's own public product pages confirms the risk was real: SKY already operates an **AODB** (single source of truth for flight data) and a **BRS** that tracks baggage in real time from check-in through sorting/loading/transfer, links to AODB/BHS, and already has some anomaly alerting — plus SKY's own materials reference A-CDM/TAM and a Unified Data Platform. A judge who knows SKY's product line would reasonably ask "how is this different from AODB/A-CDM/BRS?" — and the broad framing had no sharp answer.

Narrowing to baggage-disruption *coordination* (not baggage *tracking*, which BRS already does) gives a defensible, non-overlapping problem: BRS answers "where is the bag," One TrustX answers "why is the baggage operation becoming disrupted, what will it affect next, and what should operators prioritize." This also happens to be the exact causal chain already modelled in `SCN-FLOOD-BAGGAGE-001` from a real, cited Sept 2026 BKK incident — the scope narrowing and the existing dataset design converge rather than conflict.

## Differentiation Q&A (for judges)

**Q: How is this different from AODB?**
AODB is the system of record for flight/aircraft/schedule data. One TrustX consumes AODB signals (ETA/ETD, gate, flight status) as one of several inputs; it does not replace or duplicate AODB's role as flight-data source of truth.

**Q: How is this different from BRS?**
BRS (per SKY's own product page) tracks baggage milestones — check-in, sorting, loading, transfer — and links to AODB/BHS with some alerting. One TrustX does not re-track the bag. It consumes BRS/BHS signals alongside ground-handling, flight and weather signals to answer a different question: not "where is this bag" but "why is the baggage *operation* degrading, what else will it affect, and what should be fixed first." Short version: **BRS tracks the bag. One TrustX coordinates the disruption around the bag.**
Do not claim BRS *cannot* do this — its own page claims some predictive alerting already. The safe, defensible claim is that One TrustX *builds on* existing BRS/AODB signals for cross-stakeholder disruption recovery and prioritization, not that BRS is incapable of it.

**Q: How is this different from A-CDM?**
A-CDM is broader: collaborative airport/flight operations, milestones, turnaround, on-time performance. This pitch explicitly does not claim to build a new collaborative-decision-making system. It picks one focused operational use case — baggage disruption — and applies exception detection, impact analysis and recovery prioritization using signals from existing systems. If the prototype succeeds, the stated expansion path (turnaround → gate → passenger → cargo → airport-wide) is the honest route toward A-CDM-adjacent territory, stated as future scope, not current scope.

**Q: Isn't this just a dashboard on top of BRS/AODB data?**
The distinguishing claim is the layer BRS/AODB don't provide on their own: cross-system bottleneck detection, downstream impact prediction across multiple flights/transfers, and prioritized recommended action — grounded in the existing trust/reconciliation engine (`trust_service.py`, the validation pack's `ground_truth_state_match` mechanism) rather than a static KPI view.

## What's affected

- `docs/onetrustx-pitch.md` is the canonical pitch narrative going forward for One TrustX. `docs/pitch.md` (the 3-minute demo script for the earlier passenger-queue simulation phase of this same project) was left untouched; it is an older script, not the current pitch.
- `SCN-FLOOD-BAGGAGE-001` is now flagged as the hero/default demo scenario in the scenario library; the other 13 scenarios (including `SCN-SYSTEM-RESILIENCE-001`, directly relevant to "our own BRS/trust pipeline degrading") remain in the validation pack as supporting evidence, not replaced.
- Mishandled-baggage figures corrected to the 2025 SITA numbers (~24M bags, ~$6.3B/year) with an explicit "mishandled, not lost" correction, since the next pitch date should use the most recent industry data available.

## What's next (not done in this pass)

- Verify directly (not just from the product marketing page) what alerting/prediction BRS currently performs in practice, before presenting the differentiation Q&A live — if BRS already does cross-flight bottleneck prediction, the differentiation claim needs tightening further.
- Rework `docs/evaluation.md`'s headline framing so the flood/baggage scenario's numbers are presented first, per the "don't lead with 50%/61% as a single-simulation headline" guidance in `docs/onetrustx-pitch.md` section 7.
- If this scope survives to the next round, draft the Phase-2 expansion scenarios (turnaround, gate) referenced in the pitch's closing vision line.
