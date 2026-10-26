# ADR: Align pitch to SKY's Preliminary Pitch brief and mentor feedback

2026-10-07

## What changed

- New canonical pitch outline: `docs/preliminary-pitch-th.md`, structured on SKY's 8 recommended sections and a 7-minute budget.
- Problem narrowed again, from "Baggage Disruption Recovery" to one question: **delayed departure baggage — which stage is it stuck at, why, which flights are affected, what to fix first.**
- Solution framed as a stage-by-stage status view (Check-in, Screening, Loading, Transfer, Unloading, Claim) instead of a general coordination layer.
- `docs/onetrustx-pitch.md` is kept as the earlier draft, not deleted.

## Why

- Buddy feedback (Chanapa, 7 Oct): the problem is still unclear; pick one problem, state its causes, who it is for, which data comes from which party, and show a view where a viewer sees at a glance "no problem" or "the problem is in this part". Mention expansion only at the end.
- SKY's kick-off content: BRS exists at BKK/DMK/HKT and SKY itself locates baggage failures at handoffs (check-in, loading, transfer, arrival). The process-flow slide shown has a Hold Baggage line that maps directly onto a stage view.
- Official brief: Preliminary Pitch on 22 Oct 2026, PDF deck due 20 Oct 2026 23:59, **no prototype required** this round.

## What's affected

- Code/UI alignment with the hero scenario (API default `S5`, README headline, "Passenger journey" wording) is no longer urgent; it moves to the prototype phase if the team advances.
- Headline statistic reverts to SITA 2024 (33.4M mishandled bags, ~USD 5B) because SKY cited it at kick-off. The 2025 figure stays out until checked against the source report.
- Simulated percentages (61/78/50) and the unbacked deck numbers (86%, 100%, 100%, 117.39B THB) stay out of the deck.

## What's next

- Confirm the per-stage cause table with the mentor; it is the team's hypothesis.
- Verify the Sept 2026 flood/baggage incident citations before using it as the opening.
- Build the deck PDF from the outline and rehearse to 7 minutes.
