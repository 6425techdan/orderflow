.PHONY: help install test lint typecheck up down logs e2e demo-order drill-payment-fail kind-up kind-down clean

help:
	@echo "OrderFlow targets: install test lint typecheck up down e2e demo-order kind-up kind-down"

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

lint:
	python -m ruff check packages apps tests

typecheck:
	python -m mypy packages/orderflow_common/orderflow_common

up:
	docker compose -f deploy/compose/docker-compose.yml up -d --build

down:
	docker compose -f deploy/compose/docker-compose.yml down -v

logs:
	docker compose -f deploy/compose/docker-compose.yml logs -f --tail=100

e2e:
	python scripts/demo/e2e_order.py

demo-order: e2e

drill-payment-fail:
	python scripts/drills/payment_failure.py

kind-up:
	@echo "Use: pwsh scripts/demo/kind-up.ps1 -LoadImages   OR   bash scripts/demo/kind-up.sh"

kind-down:
	@echo "Use: pwsh scripts/demo/kind-down.ps1   OR   bash scripts/demo/kind-down.sh"

clean:
	docker compose -f deploy/compose/docker-compose.yml down -v --remove-orphans || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache **/__pycache__
