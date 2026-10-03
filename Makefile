.PHONY: install data train test lint run demo

install:
	python -m pip install -e '.[dev]'

data:
	python scripts/generate_synthetic_data.py

train: data
	python scripts/train_propensity_model.py

test:
	pytest -q

lint:
	ruff check src tests scripts

run:
	uvicorn nba.api.app:app --reload
