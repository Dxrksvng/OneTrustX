# ADR: One name for the project — One TrustX

2026-10-07

## What changed

The project started as "Airport TimeTwin" and was renamed One TrustX. It is one project, not two prototypes in one repo. The old name was replaced everywhere it was safe to do so:

- Display text in docs, README, HTML report, SQL header comments, seed airport name (`One TrustX Illustrative Terminal`).
- Package names: `backend/pyproject.toml` + `uv.lock` (`onetrustx`), `frontend/package.json` + lockfile (`onetrustx-ui`).
- Browser storage keys: `onetrustx-language`, `onetrustx-session`.
- SQLite file: `onetrustx.db` (default in `backend/app/db.py`, `run-local.sh`); local files renamed.
- Container user in `backend/Dockerfile`, dataset manifest id, public-data User-Agent.
- Stale folder paths in docs (`.../sky ict/airport-timetwin` -> `.../sky ict/onetrustx`).
- Both PDFs regenerated from their Markdown sources.
- Two sentences that described `docs/pitch.md` as a "separate, unrelated prototype" were corrected.

## Deliberately not renamed

| Where | Value | Why |
|---|---|---|
| `infra/docker-compose.yml`, `.env.example`, `.env` | Postgres database and user `timetwin` | An existing Postgres volume was initialised with this user; changing it breaks login unless the volume is recreated. `.env` is also off-limits to edit. |
| `infra/docker-compose.yml` | project name `airport-timetwin` | The volume name derives from it; renaming would start an empty database and orphan the old volume. |
| `docs/team-handoff.md` | container `airport-timetwin-share` | Name of a container that may exist on the machine; Docker was not running, so not checked. |
| `docs/executive-ui.md` | `Airport_TimeTwin_UI_Pages` | Name of a file supplied earlier, cited as a source. |

## What's affected

- A database seeded before this change still holds the old airport name until reseeded.
- Language preference in the browser resets once (new storage key).

## Verified

`uv lock --check`, `ruff check app`, `pytest` (26 passed), `tsc --noEmit`. Docker stack and Playwright tests were not run.

## What's next

To finish the Postgres/compose rename: export the data or accept a fresh database, then change compose, `.env.example` and `.env` together.
