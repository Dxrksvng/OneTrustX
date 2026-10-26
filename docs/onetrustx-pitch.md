# One TrustX pitch — Baggage Disruption Recovery

Scope narrowed 2026-10-07. Previous framing ("One TrustX unifies every aviation stakeholder") was too broad and overlapped directly with SKY ICT's own AODB (flight single source of truth) and BRS (real-time baggage tracking, already linked to AODB/BHS with some alerting) — see [SKY ICT BRS project page](https://www.skyict.co.th/en/project-showcase/brs). This document is the pitch narrative for the narrowed scope: `docs/pitch.md` is the older 3-minute demo script from the passenger-queue simulation phase of this project and is not affected by this change.

This is a **pitch narrative**, not a measured-results document. For what is actually measured vs assumed, see `docs/data-provenance-th.md` (sections 17–18) and `docs/decisions/2026-10-07-baggage-disruption-scope-narrowing.md`.

## Problem statement

**English:** During irregular operations, baggage disruptions can cascade across ground handling, flights, gates and passengers because operational signals are distributed across multiple systems and stakeholders. Operators need earlier visibility of the bottleneck, its downstream impact and the next coordinated action.

**Thai:** เมื่อเกิดเหตุผิดปกติ เช่น น้ำท่วม คนไม่พอ หรืออุปกรณ์เสีย ปัญหากระเป๋าสามารถลุกลามเร็ว แต่ข้อมูลที่ใช้เข้าใจสาเหตุและผลกระทบกระจายอยู่หลายระบบและหลายฝ่าย ทำให้การมองเห็นปัญหาและประสานการแก้ไขอาจไม่ทันสถานการณ์

Reference incident (cited as evidence the problem is real, not as a result of One TrustX): heavy rain/flooding in late September 2026 disrupted ground-staff commutes to Suvarnabhumi; Reuters reported ~5,000 bags stranded at one point (29 Sep 2026); AOT opened a dedicated channel for Thai Airways passengers to check delayed-baggage status, 26–29 Sep; follow-up reporting attributed the cascade to a mix of ground-handling staff shortage and baggage-cart/tug availability. Full citations and the causal-chain model built from this case are in `data/scenarios/scenario_library.json` (`SCN-FLOOD-BAGGAGE-001`, now the hero/default demo scenario).

## 1. Problem / Pain point

> When disruption hits, a baggage problem can become an airport operation problem.

Flood → ground-staff shortage → baggage processing capacity down → backlog → flight delay/cancellation → passenger impact. The Sept 2026 BKK case is the opening reference incident (REAL_PUBLIC, cited above) — explicitly labelled as a reference incident, not a result this system produced.

## 2. Target user

- **Primary:** Baggage / Ground Operations Controller
- **Secondary:** Airline OCC, Airport Operations
- **Beneficiary:** Passenger

## 3. Proposed solution

> **One TrustX — Baggage Disruption Intelligence & Coordination Layer**

Consumes signals from existing systems (BRS/BHS, AODB, ground handling, weather). Does not replace SKY's BRS or AODB.

## 4. How it works

```
BRS/BHS + AODB + Ground + Weather
              |
        Shared Events
              |
   Verify / Detect Conflict
              |
       Operational State
              |
      Detect Bottleneck
              |
       Predict Impact
              |
    Recommend Priority
              |
       Human Decision
```

BRS answers: *"BAG123 has not loaded."*
One TrustX answers: *"That's not an isolated bag — Flight TGxxx's baggage throughput has been declining, ground staff capacity is low, a baggage cart is unavailable, 3 more flights are entering the risk window, and 84 transfer bags carry the highest risk. Recommended priority: reallocate resource to Flight A before B/C."*

## 5. Value & differentiation

Not competing with BRS. Not competing with AODB. Not building a new A-CDM.

> **BRS tracks the bag. One TrustX coordinates the disruption around the bag.**

Safer framing for Q&A (BRS already has some predictive alerting per its own product page, so avoid an absolute claim):

> One TrustX builds on existing BRS/AODB signals and focuses on cross-stakeholder disruption recovery and prioritization.

Versus A-CDM: A-CDM is broader (collaborative airport/flight ops, milestones, turnaround, OTP). This pitch deliberately does not claim to build a new collaborative-decision-making system — it picks one focused operational use case (baggage disruption) and layers exception detection, impact analysis and recovery prioritization on existing systems. Full differentiation Q&A: `docs/decisions/2026-10-07-baggage-disruption-scope-narrowing.md`.

## 6. Feasibility

SKY already operates BRS (linked to AODB/BHS) and AODB. The ask is not "instrument the whole airport with new sensors" — it is "consume signals from infrastructure that already exists, plus add ground/resource/external event feeds." This is the strongest feasibility argument available and should be stated explicitly.

## 7. Expected impact

Do **not** lead with "50% delay reduction" or "61% coordination-time reduction" as headline claims from a single simulation pack — those numbers exist (`docs/evaluation.md`) but are synthetic validation of the mechanism, not a measured operational outcome. State expected KPIs instead:

- Earlier disruption detection
- Faster root-cause identification
- Faster cross-team coordination
- Reduced recovery time
- Fewer bags exposed to missed connections

Measure these for real in the controlled prototype/simulation phase (see `docs/validation-data-contract.md` for what "real" would require).

## 8. Next steps

```
Phase 1 — Validate the baggage-disruption workflow with domain experts
Phase 2 — Build synthetic + public-data scenarios: Normal / Flood / Staff Shortage / BHS Failure
          (already built — see data/scenarios/scenario_library.json, S9/S13)
Phase 3 — Prototype: Detect -> Predict -> Recommend
Phase 4 — Expert validation
Phase 5 — Shadow mode with anonymized operational data
```

## Closing line

> One TrustX helps baggage and ground operations teams detect disruption early by combining baggage, flight, resource and external-event signals into one trusted operational view, then identifies the bottleneck, predicts downstream impact and recommends recovery priorities for human operators.
>
> We start with baggage disruption — but the same trusted coordination layer can later expand to turnaround, gate, passenger and cargo operations.

## Data this scope actually needs (narrower than before)

| Data | Want to know | Used for |
|---|---|---|
| BRS/BHS | Scan/milestone, location, handoff, loading | Baggage status |
| AODB / flight | ETA/ETD, gate, flight status | Deadlines, downstream impact |
| Ground handling | Staff, cart, belt, task readiness | Bottleneck location |
| Connection | Transfer window / connecting flight | Priority ordering |
| External | Weather, flood, disruption | External risk factor |

No passenger name/passport required for the prototype.

## Source accuracy note

Earlier material referenced "33.4 million bags lost (2024)" — **do not use that wording.** SITA's figure is 33.4 million *mishandled* bags in 2024 (~$5B industry cost), not permanently lost. SITA's 2026 report shows 2025 improved to ~24 million mishandled bags (~$6.3B/year industry cost) — use the 2025 figure since it is more recent. See `data/scenarios/scenario_library.json` benchmark_context for both figures with URLs.
