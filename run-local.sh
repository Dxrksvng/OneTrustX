#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export DATABASE_URL="${DATABASE_URL:-sqlite:///$PROJECT_DIR/backend/onetrustx.db}"
export DEMO_MODE=true
cd "$PROJECT_DIR/backend"
uv sync --frozen
uv run --no-sync alembic upgrade head
uv run --no-sync uvicorn app.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!
trap 'kill "$API_PID" 2>/dev/null || true' EXIT INT TERM
cd "$PROJECT_DIR/frontend"
if [[ ! -d node_modules ]]; then npm ci; fi
npm run dev
