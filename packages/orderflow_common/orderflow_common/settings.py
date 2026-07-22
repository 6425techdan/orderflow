from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "orderflow"
    service_version: str = "0.1.0"
    log_level: str = "INFO"
    database_url: str = "postgresql://orderflow:orderflow@localhost:5432/orderflow"
    redis_url: str = "redis://localhost:6379/0"
    orders_stream: str = "orders"
    orders_group: str = "order-workers"
    dead_letter_stream: str = "orders-dlq"
    payment_url: str = "http://localhost:8082"
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    otel_enabled: bool = True
    db_pool_min: int = 1
    db_pool_max: int = 10
    fault_payment_latency_ms: int = 0
    fault_payment_fail_rate: float = 0.0
    fault_db_exhaust: bool = False
    menu_version: str = "2026.07.01"
    stale_menu_reject: bool = False
