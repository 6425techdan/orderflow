FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/packages/orderflow_common:/app/apps/order-api

RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin appuser

COPY pyproject.toml README.md ./
COPY packages ./packages
COPY apps ./apps

RUN pip install --no-cache-dir -e . \
    && chown -R appuser:appuser /app

USER 1000

EXPOSE 8080
CMD ["uvicorn", "order_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
