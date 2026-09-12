# UX and motion design

Reference reviewed 2026-09-13: [MotionSites](https://motionsites.ai/) and its public [animation workflow](https://motionsites.ai/lesson/build-animated-website-with-motionsites). No paid prompts, templates, or assets copied. The implementation is original React, CSS and SVG.

The visual direction is a calm airport control workspace: forest-green navigation, warm neutral panels, a dimensional terminal diagram, clear risk labels, and restrained motion that draws attention to a changed forecast. A topology illustration establishes airport context without claiming to be a real airport floor plan.

Operations: orient using the airport map, select a horizon, inspect a checkpoint, compare intervention outcomes, provide a human decision reason, then measure the result. Map checkpoint buttons work with keyboard activation and have pressed states. A zoom control supports closer inspection. Scenario controls are grouped in a collapsible studio, separate from intervention decisions.

Passenger: a boarding-pass card puts boarding deadline, gate, Safe Time and the next action first. Step-free routing is selected by default. A gate change updates the route and shows the previous Safe Time. A top-level Operations/Passenger switch complements the sidebar.

Motion: subtle workspace entry, forecast-value transitions, and animated SVG route dashes. All are disabled with prefers-reduced-motion. No autoplay background video, heavy 3D runtime, or imagery download is required. Typography uses a fallback font stack when external fonts are unavailable.

Accessibility: text labels accompany conventional green/yellow/orange/red statuses, visible keyboard focus, native buttons and range controls, labelled forms, error/status regions, and a mobile navigation drawer. Automated browser checks cover mobile overflow and interaction; a full WCAG audit remains outstanding.

Provenance and uncertainty remain visible throughout. Simulated action acceptance never sends commands to airport equipment. Stale data disables actionable recommendations and displays a passenger warning.
