# Aviation Executive Operations

The September 2026 redesign follows the user-provided Airport_TimeTwin_UI_Pages
references, including the two consolidated page sheets. Reference metrics,
airline branding, real-airport identities and deployment claims are not copied.

## Experiences

- `/`: premium aviation landing with a locally bundled generated terminal image.
- `/overview`: executive header, four model-backed KPIs and terminal outlook.
- `/future`: segmented Current/+15/+30/+60 forecasts with uncertainty and drivers.
- `/operations`: prioritised operational situations and an accessible detail drawer.
- `/simulator`: strategy radio selection, baseline/proposed table and human submission.
- `/flights`: flight filters, search and an accessible ground-timeline drawer.
- `/passenger-flow`: selected-horizon network demand flow with data-scaled widths.
- `/performance`: simulated passenger-hours saved and separate model evaluation.
- `/journey`: passenger Safe Time and a restrained gate-change notice.
- `/demo`: scenario timeline alongside the actual operational workspace.

Previous `/app/...` and `/passenger/TT401` URLs remain supported. Audit and sources
remain available under More; Ask TimeTwin is a contextual top-navigation action.
Submitting a recommendation records human approval and updates only synthetic
state. Real equipment is never controlled.

## Visual assets and data

`frontend/public/images/aviation-terminal.png` is an original AI-generated
illustration made on 2026-09-13. It depicts a fictional airport, not Suvarnabhumi;
its visual provenance is ASSUMPTION/illustrative. The hero visibly labels this.
No commercial Flynext source, photography or fonts were copied. The interactive
terminal is code-native SVG so forecast states remain readable and accessible.

Nav, surfaces and type use navy, warm white and slate. Gold is reserved for brand
and passenger CTA accents; risk states retain amber/red/green plus text labels.
Continuous map motion is removed. Drawers and page transitions are brief, and
prefers-reduced-motion suppresses them. Data confidence remains explicitly
heuristic. Flight timeline fixture times are planned, not completed activities.

## Fidelity and presentation pass

`terminal-twin.png` is a second original generated architectural illustration.
Checkpoint labels, selection, routing lines, forecasts and ranges remain rendered
components above it; neither image is an actual surveyed airport. Visual gaps
from the reference are the generated rather than exact photographic assets and
model-grounded numbers instead of invented reference statistics.

User-requested presentation features are preserved under expandable Presentation
tools: Future Time Slider, optional route motion and draggable Before/After.
The default executive layout continues using segmented controls and a comparison
table. `/sources` is canonical with `/trust` and `/app/sources` aliases. Guided
Demo now changes the actual right-side workspace to match its active stage.
