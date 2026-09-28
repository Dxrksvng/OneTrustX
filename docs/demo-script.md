# Reproducible demo

Simulated MVP Result — Not actual airport performance.

1. Open Airport now and click Reset demo. Clock is 17:00 ICT; A has 96 queued passengers, 4 lanes, 12-minute virtual wait. Normal demand clears over time.
2. Click Start peak event. A is forecast at 39 minutes at +30; select Now/+15/+30/+60 to inspect pressure. Four synthetic flight fixtures accompany the assumed arrival wave. There are 580 anonymous journey fixtures, not a measured affected population.
3. Click Compare interventions. The four options share the same input snapshot. Compare No Action, Open A5, Redirect 20%, and Open A5 + redirect 12%. Network wait and passenger-minutes include B and extra walking.
4. Inspect P95, staffing, score, and cost assumptions. Change custom sliders and run simulation. The combined option is recommended in the default peak fixture.
5. Enter an operator reason and Accept action. State updates only in the demo; a human decision is recorded. Reject/override are available. A stale recommendation cannot be accepted.
6. Open Decision log and record a synthetic observed mean wait. The audit reports signed prediction error; no actual airport outcome is claimed.
7. Open Passenger journey, Reset demo, and observe Safe Time 34 minutes. Click Simulate gate change: C8→E7 adds 23 accessible walking minutes; Safe Time becomes 11; LEAVE NOW / Proceed now appears. This separate reset makes the exact passenger vignette reproducible; retaining the peak scenario produces different, model-derived times.
8. Test stale feed. Passenger guidance is marked stale; simulation and recommendation actions are blocked. Refresh feed or Reset demo restores the synthetic source freshness.

CLI: `cd backend && uv run python ../scripts/run_demo.py` while the API is running. This performs the peak decision, resets the passenger vignette, and prints calculated before/after values.

## Guided website walkthrough

Open `/demo` and choose **Start / restart guided demo**. The approximately
three-minute sequence uses nine stages with 20-second dwell periods. Pause or
use Next step for a live presentation. It runs real deterministic APIs and
records the synthetic accepted decision. A separate reset before the passenger
stages restores the reproducible Safe Time 34 → 11 scenario; the UI states this
reset explicitly. Audit history survives both resets. Shared demo users can
interfere with the scenario; version/stale checks stop invalid acceptance.
