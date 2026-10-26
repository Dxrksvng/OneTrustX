# Review: Baggage Disruption Recovery direction + source check

2026-10-07 · Audience: team, before building the Preliminary Pitch deck (due 20 Oct 2026, pitch 22 Oct 2026)

## What changed

- Reviewed the round-1 deck (`../SKY .pdf`, 3 pages) against the narrowed direction and the kick-off insight.
- Checked the opening incident and the SITA figures against published sources (list below).
- Recommends merging the two 7 Oct outlines into one framing (below). No pitch file was edited in this pass.

## Verdict

Direction is strong enough to pitch, with three fixes:

1. **One framing, not two.** `onetrustx-pitch.md` (disruption recovery) and `preliminary-pitch-th.md` (delayed departure baggage, stage view) disagree on scope. Use: *baggage backlog during irregular operations*. The stage view is the screen; disruption is the trigger.
2. **Detect from data SKY already holds.** Compute per-stage throughput from BRS scans against the AODB schedule. Ground-handler staff/equipment data becomes an optional input for cause, not a prerequisite. This removes the weakest feasibility point (data SKY does not own).
3. **Do not scope to "departure" only.** The Sept 2026 incident was mostly arrival and transfer baggage. Scope by handoff stage, both directions.

## Source check

| Claim | Status | Use |
|---|---|---|
| SITA 2025: 24M mishandled bags, 4.9 per 1,000 pax, USD 6.3B/year, USD 260/bag, transfers 39% | Confirmed (SITA Baggage IT Insights 2026 press release) | Headline figure |
| Round-1 deck: "$60.3B / Year" baggage mishandling | **Wrong by 10x.** 24M x $260 = ~$6.3B | Fix before reuse |
| Round-1 deck: "$9.8B Passengers / Year" | Passenger count carrying a dollar sign; SITA's release uses 5B travellers (different counting basis) | Remove "$", name the source |
| Sept 2026 BKK incident: 10,000+ bags accumulated 26-29 Sep; ~8,000 outstanding 30 Sep; 1,092 left by 3-4 Oct | Confirmed (The Star/Bernama, The Nation) | Opening incident |
| "~5,000 bags" on 29 Sep | Thai Airways CEO statement as reported by The Nation; Reuters page itself could not be opened | Cite The Nation, or open Reuters manually |
| Cause: flood stopped Thai Airways ground-handling staff reaching work + baggage vehicle breakdowns | Confirmed (The Nation) | Causal chain |
| Response: 131 military personnel (100 RTAF + 31 Army), cargo acceptance suspended 30 Sep-6 Oct, flights reduced | Confirmed (The Star, The Nation) | Shows recovery was manual load-shedding |
| SKY BRS: tracks check-in, sorting, loading, transfer; integrates AODB and BHS; alerts on no-show passenger bags and bags in the wrong container | Confirmed (SKY product page) | Differentiation: BRS alerts are bag-level reconciliation, not flow capacity |
| BRS deployed at BKK, DMK, HKT | From kick-off talk only; not on the product page | Say "as presented at kick-off" |
| Khaosod English article | Appears in search results; page returned 403 | Open manually before citing |

## Round-1 deck items that must not carry over

- 86% / 100% / 100% / 117.39B THB and the loss-exposure chart: no source in repo.
- "18s -> 7s, 61%" printed under two different metrics; 61% vs 78% both labelled coordination time.
- ChatGPT logo in the AI box: README says the copilot is no-LLM. Pick one and make slide and repo agree.
- "Blockchain's Ledger": expect "why blockchain?". Call it a shared, auditable event log unless the team can defend the ledger.
- Seven stakeholder groups and the "every sector" platform text: this is the breadth the mentor asked to cut.
- Demo link points to the passenger-queue prototype, not baggage.

## Hardest judge questions

1. In the Sept incident everyone knew staff could not reach work. What would a screen have changed? — It does not create staff. It ranks which flights and transfer bags to handle first with reduced capacity, and shows when backlog growth exceeds recovery capacity so load-shedding (flight cuts, cargo suspension) is decided earlier. Not claimed: that the real incident would have ended sooner.
2. BRS already alerts. What is new? — BRS alerts are per-bag reconciliation exceptions. We measure flow per stage against the flight schedule.
3. Ground-handler data belongs to another company. — Detection needs only BRS + AODB; handler data is optional.
4. Overlap with A-CDM and the flight-delay team. — A-CDM coordinates flight milestones; we feed it one input it lacks: baggage readiness risk per flight.
5. How is the recommendation produced, and who is accountable? — Rule-based ranking by departure time and connection window; operator approves; every decision logged.
6. What will be measured in the prototype phase? — Time to locate the bottleneck stage, time to decision, bags at risk, on labelled synthetic scenarios with expert review.

## What's next

- Merge the two outlines into `preliminary-pitch-th.md` using the framing above, then build the deck PDF and the Q&A sheet.
- Ask the mentor: which handlers feed BRS at BKK, and whether BRS scan timestamps are available per stage.
- Open the Reuters and Khaosod pages manually.

## Sources

- https://www.sita.aero/about-us/pressroom/news-releases/tech-drove-down-mishandled-bag-rates-by-23-in-2025-but-mishandling-still-costs-the-industry-$6.3-billion-a-year
- https://www.thestar.com.my/aseanplus/aseanplus-news/2026/10/01/thailand039s-suvarnabhumi-airport-baggage-backlog-expected-to-clear-within-3-4-days
- https://www.nationthailand.com/news/general/40071553
- https://www.nationthailand.com/business/corporate/40071613
- https://www.nationthailand.com/business/corporate/40071851
- https://www.skyict.co.th/en/project-showcase/brs
