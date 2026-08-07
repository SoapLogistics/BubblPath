.PHONY: test install check lint

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	PYTHONPATH=. pytest tests/

check: lint test

lint:
	ruff check .
