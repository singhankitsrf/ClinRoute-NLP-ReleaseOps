.PHONY: install data-check baseline test lint typecheck security check api docker
install:
	pip install -e ".[dev]"
data-check:
	python scripts/generate_synthetic_data.py --rows 3000 --seed 42
	python scripts/check_data_contract.py
baseline:
	python training/train_baseline.py
test:
	pytest -q
lint:
	ruff check .
typecheck:
	mypy src
security:
	bandit -q -r src scripts training
check: data-check lint typecheck test
api:
	MODEL_DIR=models/baseline uvicorn clinroute.api:app --reload --port 8000
docker:
	docker build -t clinroute-nlp-releaseops:local .
