# Realism, data and visual upgrade review

## Changes

- Isolated, deterministic fresh demo sessions; explicit stale test with recovery.
- Stable prediction/recommendation IDs and one reviewed decision lifecycle, including simulated measurement.
- Modelled DEMO401–404 use real airport codes and distinct gates with a shared checkpoint.
- Conserved end-to-end representative flow with explicit domestic immigration bypass.
- Resource efficiency uses actual simulator staff/lane/walking metrics and clearly states its denominator.
- Public-data ingestion, normalized PostgreSQL tables and aggregate APIs; offline demo never depends on source availability.
- Real external CBP benchmark evaluation with chronological split; no unsupported model promotion.
- Compact executive header/KPI spacing, airport process layers, historical context charts, contextual demo drawer and readable guided presentation.
- Remembered Thai/English across all main routes; model/data identifiers remain unmodified.

Migrations: `002_demo_sessions`, `003_public_data`. Core changes are under backend/app, scripts/data, frontend/src/components, i18n/locales and executive.css. See git diff for exact files; existing working implementation was preserved.

## Known limits

- Public BKK security queues, lane telemetry, staffing and commercial schedules were not acquired. They remain modelled assumptions.
- CAAT coverage is uneven; AOT published-report download returned 404 and TSA returned 403. No fabricated replacement records are imported.
- CBP is immigration, not security. Current benchmark only checks external plausibility, not calibrated BKK service rates or forward warning lead time.
- Existing generated hero and illustrative terminal assets remain to preserve the approved composition. A licensed real historical BKK photograph was added to Sources; the hero is not claimed to be a real BKK photograph. The UI is closer in density, but not pixel-identical to the reference.
- The temporary public tunnel depends on the Mac and Docker staying online. Demo role headers are not production authentication.

## Field validation

1. Historical replay/backtesting with governed operational data.
2. Shadow mode at two checkpoints with no equipment control.
3. Human decision-support pilot with approval/rejection/override.
4. Controlled integration after governance, calibration and operational acceptance.

Measure MAE, precision/recall/F1, false alarms, warning lead time, P95 wait, passenger-minutes, staff/lane minutes, resource utilization and high-risk journey share. Do not infer missed-flight probability or emissions savings from these proxies.

## Verified checks

- Backend: 23 Pytest tests passed; Ruff passed.
- Frontend: TypeScript/Vite build, ESLint and 2 Vitest tests passed.
- Browser: 7 Playwright tests passed, including all main routes, remembered Thai/English, mobile layout, stale recovery, approved lifecycle without duplicate rows, gate recomputation and nine-step measured demo.
- PostgreSQL: migrations through 003 applied; all 22 source extracts imported; second import did not add duplicate rows. Aggregate API checked against the imported data.
- Desktop screenshots captured for 11 application routes; no browser page errors recorded. Visual pass reduced header/KPI spacing and added readable process layers. Existing hero remains an explicitly illustrative/generated asset.
- New temporary preview URL verified HTTP 200: https://selected-enquiries-celebrities-golf.trycloudflare.com/overview . Previous Quick Tunnel expired and was replaced.
