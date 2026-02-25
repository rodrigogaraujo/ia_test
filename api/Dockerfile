FROM python:3.11-slim AS base

WORKDIR /app

RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .

COPY scripts/ scripts/
COPY data/ data/

RUN mkdir -p /app/data/vectorstore && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 3456

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3456"]
