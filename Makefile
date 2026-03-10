.PHONY: init test lint format check

init::
	python -m pip install --upgrade pip
	python -m pip install pip-tools
	python -m piptools compile requirements/dev-requirements.in
	python -m piptools compile requirements/requirements.in
	python -m piptools sync requirements/dev-requirements.txt requirements/requirements.txt

test:
	python -m pytest

lint:
	python -m flake8 src tests

format:
	python -m isort src tests
	python -m black src tests

check:
	python -m isort --check-only src tests
	python -m black --check src tests
	python -m flake8 src tests
	python -m pytest
