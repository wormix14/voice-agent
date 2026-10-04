FROM python:3.12

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

ENV UV_PROJECT_ENVIRONMENT="/opt/venv"

ENV PATH="/opt/venv/bin:$PATH"

RUN uv sync --frozen --no-install-project

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]