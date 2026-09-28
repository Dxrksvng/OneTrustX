# Aviation design direction

Updated 2026-09-13 following the user's Flynext reference:
https://elements.envato.com/flynext-private-airlines-charters-html-template-3VFRLE6

Flynext is a visual reference only. No template code, photographs, commercial
claims, testimonials or airline branding are copied into TimeTwin.

The brand uses deep navy, white and slate, with restrained champagne accents.
Space, clear typography and consistent alignment establish an aviation identity.
Operational red, amber and green retain their risk meanings and text labels.
Avoid neon, decorative alert pulses, fake CCTV feeds and unsubstantiated KPIs.

The implemented aviation.css layer updates the existing operations workspace
without changing simulation behaviour. The broader requested redesign remains
in progress: cinematic landing, URL-based product views, guided demo, contextual
copilot, future slider and draggable simulation comparison. These must use
structured engine results, preserve stale-data safeguards and support reduced
motion. Passenger guidance stays simple and prominently shows Safe Time.

Landing-page motion can introduce the decision story. Operational motion must
explain a changed forecast, selected route or simulation result. Public airport
metadata does not imply operational deployment or endorsement.

## Implemented experience update

- `/`: original code-native terminal illustration and restrained aviation landing.
- `/demo`: guided scenario with pause, restart and manual step controls; nine
  steps at 20-second intervals (approximately three minutes including API work).
  Starting is explicit consent to reset and accept a synthetic demo action.
- `/app`, `/app/future`, `/app/operations`, `/app/simulator`: operations views,
  discrete 0/15/30/60 forecast slider, model-derived comparison reveal.
- `/app/flights`: searchable synthetic flights and stored ground handling details.
- `/app/flow`: network flow widths use per-checkpoint simulated arrivals.
- `/app/performance`: current scenario benefit separate from offline model quality.
- `/app/audit`, `/app/sources`: decisions, measurements and provenance.
- `/passenger/TT401`: accessible journey and animated Safe Time with reduced motion.
- Copilot opens in a native modal side panel with keyboard Escape and focus handling.

No licensed Envato assets or fabricated airport photography are included. The
landing terminal is an illustrative SVG, not a surveyed airport model. Public
cache files are present under data/raw; operational CSVs under data/synthetic
are generator output. No additional user operational dataset was found in the
relocated project directory during the 2026-09-13 inspection.

## Superseding executive reference update

The newer consolidated reference sheets supersede the initial sidebar/slider
layout above. Current canonical routes, generated visual provenance, top
navigation, segmented forecast controls and strategy comparison are documented
in [Executive UI](executive-ui.md). The old route aliases continue to work.
