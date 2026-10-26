# ADR: Baggage view is computed from sourced scenarios, not fixed values

2026-10-08

## What changed

- `backend/app/baggage_flow.py`: a synthetic baggage flow simulator (`simulate`) and a separate assessment (`assess`) that reads only aggregate scan counts, the schedule with on-block times and expected bag counts, and an optional ground-handler feed.
- `backend/app/baggage_calibration.json`: every driving parameter with tier (REAL_PUBLIC / BENCHMARK / DERIVED / ASSUMPTION), source and URL, plus the Sept 2026 reference incident and real BKK rainfall.
- Five scenarios: normal, flood staff shortage, sortation fault, late inbound connections, stale loading feed.
- API: `/api/trustx/baggage/{scenarios,control,calibration,evaluation}`. `shared-state.baggage_control` now returns the computed flood view.
- UI: `/trustx` is mounted (it was never routed before; `main.tsx` sent every path to the queue app). Scenario and time pickers, stage row with queue and oldest-bag wait, flights in priority order, cause shown as REPORTED or UNKNOWN.
- `scripts/experiments/run_baggage_evaluation.py`: exports scan CSVs to `data/synthetic/baggage_flow/` and scores 30 seeds per scenario into `backend/app/baggage_evaluation.json`.
- `scripts/data/fetch_weather_incident.py`: cached Open-Meteo hourly weather for 22 Sept-3 Oct 2026.

## Why

The previous view returned one hard-coded dictionary for every scenario, so it could never show "normal", which is what the SKY buddy asked for. SKY owns BRS and AODB, so location of the bottleneck is derived from those two alone; handler data only names the cause.

## Evaluation (30 seeds, SIMULATED)

| Scenario | Bags missed, plan order | Bags missed, priority order | Flight precision | Flight recall | Alert share |
|---|---|---|---|---|---|
| Normal | 0 | 0 | n/a | n/a | 0% |
| Flood staff shortage | 297.5 | 142.5 | 0.91 | 0.84 | 59% |
| Sortation fault | 7 | 0 | 0.33 | 0.58 | 13% |
| Late inbound | 16.5 | 7.5 | 0.63 | 1.00 | 28% |
| Stale loading feed | 0 | 0 | n/a | n/a | 0% |

Medians. Full ranges and definitions are in the JSON.

## Limits to state when presenting

- Flights, bags, scans and capacities are synthetic. Staffing ratio 0.55, bags per passenger, transfer share and all thresholds are assumptions.
- The baseline "plan order" is an assumed policy; a real handler may already do better, which would shrink the gap.
- Alerts and truth come from the same simulation.
- Sortation-fault precision is low (0.33): two of three flagged flights did not miss bags.
- The flood scenario does not reproduce the real incident's arrival-side backlog; arrival stays within threshold in this model.
- 170 passengers per movement is derived from figures reported in the press; check the AOT Annual Report 2025 before citing.

## Not changed

Events, Conflicts, Intelligence and the fixture KPIs still use the single-flight TT401 fixture with constant values. The Performance page now labels them as constants. The landing page still links to the queue app, not `/trustx`.

## What's next

- Confirm thresholds, hold-close time and the baseline policy with a baggage operations expert.
- Ask the mentor whether BRS scan timestamps per stage can be exported.
- Update `data-provenance-th.md` sections 8 and 12.5 to describe the computed view.

## Update, later on 2026-10-08: page moved into the main app

- `frontend/src/components/TrustXPages.tsx` and `trustx.css` were deleted on the owner's instruction. They were a separate shell that was never linked from onetrustx.vercel.app.
- The baggage view is now `frontend/src/components/BaggageControl.tsx`, a **Baggage** item in the main navigation at `/baggage`, using the existing `executive.css` components (metrics, panels, priority badges, data tables), language switch and provenance bar. `/trustx` redirects to it.
- All existing pages are unchanged.
- Backend baggage endpoints are unchanged (`/api/trustx/baggage/*`). The older single-flight endpoints remain but no page uses them.
- Not deployed: the live site and `backend-mauve-six-34.vercel.app` do not have the new page or endpoints until commit, push and deploy.
- Known, pre-existing: the header overflows 81px at 390px width on every page.

## Update, 2026-10-08: deployed to production

- Owner asked for the Baggage page on Vercel. Deployed with the Vercel CLI, not via git: `backend` project first, then `airport-timetwin-frontend`.
- `onetrustx.vercel.app` is a manually set alias. A new production deployment does not move it; run `vercel alias set <deployment>.vercel.app onetrustx.vercel.app` from `frontend/` after each deploy. Current target: `airport-timetwin-frontend-9drl3b0in.vercel.app`. Previous (pre-baggage) target for rollback: `airport-timetwin-frontend-72mipagqy.vercel.app`.
- Fixed a crash that already existed on the live Data & sources page (`benchmark.results` is absent on the server; `PublicContext.tsx` now guards it).
- Verified on the live domain: 14 pages including `/baggage` render with no console errors; baggage API returns 200.
- GitHub is still at `386d911`. Nothing has been committed or pushed, so the deployed code exists only on this machine and on Vercel.
- Report restructured into Part A (whole system), Part B (baggage only), Part C (appendix); rendered by `scripts/render_report_html.py` + `frontend/scripts/print-pdf.mjs`.

## Update, 2026-10-08: every reported value is measured

- `backend/app/baggage_metrics.py` adds a scorecard in the original Trust / Intelligence / Operation pillars. Trust is measured by fault injection (duplicate, late, corrupt, unknown-flight records and whole missing scan blocks) against `verify()`, which also reconciles counts along the stage chain.
- Results (30 seeds): record faults caught 7,636/7,636, clean records rejected 0/87,890; status silently wrong 40.5% without verification vs 6.6% with it, exact agreement 62.2%; flood bags left behind 9,082 -> 4,227 (-53.5%); priority order never worse in 90 runs.
- Percentages are now computed from 30-run totals, not medians. Late-inbound reduction is 36.7% on totals (54.5% on medians); use totals.
- Still not measurable in simulation: human coordination time, flight delay minutes. The report states the protocol to measure each.
- Known weakness found: the "oldest waiting bag" measure reacts to a single lost scan, which is why exact status agreement is only 62%. A tolerance for a few unscanned bags is the next fix; not applied yet because it changes every published figure.
- Backend on Vercel was not redeployed after this change; the live evaluation endpoint does not yet include `scorecard`.
