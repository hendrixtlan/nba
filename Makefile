.PHONY: install install-ml data train uplift drift explain pipeline test lint run demo validate-cloud

install:
	python -m pip install -e '.[dev]'

install-ml:
	python -m pip install -e '.[dev,ml]'

data:
	python scripts/generate_synthetic_data.py

train:
	python scripts/train_propensity_model.py

uplift:
	python scripts/train_uplift_model.py

drift:
	python scripts/monitor_drift.py

explain:
	python scripts/explain_model.py

pipeline: data train uplift drift test

test:
	pytest -q

lint:
	ruff check src tests scripts

validate-cloud:
	python scripts/validate_cloud_assets.py

run:
	uvicorn nba.api.app:app --reload
