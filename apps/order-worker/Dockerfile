FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/packages/orderflow_common:/app/apps/order-worker

RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin appuser

COPY pyproject.toml README.md ./
COPY packages ./packages
COPY apps ./apps

RUN pip install --no-cache-dir -e . \
    && chown -R appuser:appuser /app

USER 1000

CMD ["python", "-m", "order_worker.main"]
