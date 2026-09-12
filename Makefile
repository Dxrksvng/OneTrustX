.PHONY: up down test seed evaluate
up:
	docker compose --env-file .env -f infra/docker-compose.yml up --build -d
down:
	docker compose --env-file .env -f infra/docker-compose.yml down
test:
	cd backend && uv run pytest -q
	cd frontend && npm test && npm run lint && npm run build
seed:
	cd backend && uv run python ../scripts/seed_database.py
evaluate:
	cd backend && uv run --extra ml python ../ml/evaluation/evaluate.py
