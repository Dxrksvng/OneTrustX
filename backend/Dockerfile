FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache
COPY . .
RUN useradd --uid 10001 --create-home onetrustx && chown -R onetrustx:onetrustx /app
USER onetrustx
EXPOSE 8000
CMD ["sh", "-c", "uv run --no-sync alembic upgrade head && uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port 8000"]
