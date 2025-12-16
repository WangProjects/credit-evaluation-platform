.PHONY: install dev test lint run-api train-demo clean

install:
	pip install -e ".[api]"

dev:
	pip install -e ".[api,dev]"

test:
	pytest

lint:
	ruff check .

run-api:
	uvicorn services.api.app:app --reload --port 8000

train-demo:
	python scripts/train_baseline.py

clean:
	rm -rf artifacts .pytest_cache .ruff_cache


