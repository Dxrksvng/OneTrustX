# Assumptions and known limitations

Simulated MVP Result — Not actual airport performance.

- Frozen demo clock: 2026-09-12 17:00 ICT. Initial queue: Security A 96, B 12; service rate: 2 pax/min/lane; A has 4 of 5 lanes, B has 3. All SYNTHETIC/ASSUMPTION.
- Peak arrivals at A: 15.2 pax/min for 30 minutes, 9 for the next 15, then 5; B receives 3 pax/min. Normal A receives 5. A's peak forecast is exactly (96+30×(15.2−8))/8=39 minutes.
- Four fixture flights and 580 anonymous passenger journey rows provide a story cohort. The queue simulator includes initial passengers plus a 60-minute arrival population, reported separately. These are not claimed to be one-to-one manifests.
- Lane opening needs two staff; reserve pool has four. All redirected passengers in this aggregate model are assumed eligible for B; redirect cap is 30%. Production needs explicit eligibility, transfer lag, wayfinding and sensor confirmation.
- Redirect walking cost is four extra minutes per redirected passenger. Routing graph walking costs are independently specified illustrative edges; aggregate walking penalty is a cost assumption.
- Extra staffing increases service capacity by 0.25 pax/min per staff as a sensitivity assumption. Staff and flight-delay changes are simulation-only. Lane and redirect decisions can modify demo state.
- Accessible gate change adds 23 walking minutes. The base accessible route is Food C→Security B→Immigration→Retail→C8: 12 walk + 8 processing. Safe Time=64−20−10=34. E7 adds 23, giving 11. Non-accessible users may use an 18-minute shortcut from Retail to E7.
- Confidence 80% fresh / 35% stale is a labelled heuristic. Intervals ±(15%×estimate+2 minutes), wider when stale, are assumptions and not predictive guarantees. No validated confidence calibration.
- Flow model is deterministic fluid/FIFO cohort simulation, not an individual discrete-event airport twin. No stochastic lane outages, crowd microsimulation, real-time sensor stream, transfer queue between checkpoints, staffing shifts, or validated flight demand assignment.
- No virtual queue, boarding hold, priority-group execution, or live airport actuation. Gate changes affect the synthetic demo. Route choices are directed and accessible, but no production terminal geometry is available.
- The no-LLM copilot supports bounded English query topics. It reports engine outputs, and declines unsupported topics. Gemini integration is an extension point, not a shipped dependency.
- Thai-ready text structure covers passenger CTA and Safe Time; full Thai localization is not yet complete.
- Demo RBAC is a deliberately impersonable role header for local testing. Non-demo mutations fail closed until production identity integration exists.
- Reset keeps all audit records. History can grow; production needs retention partitions, paging, and archival policies.
- Evaluation history is synthetic and shares queue mechanics with the baseline. Synthetic accuracy is not evidence of airport deployment performance. ML candidates are not promoted automatically.

Root-cause contribution percentages use a two-factor Shapley decomposition of simulated +30 wait relative to normal demand/five lanes. This is model counterfactual attribution, not empirical causal proof. The reference counterfactual does not imply staffing feasibility as an action.
