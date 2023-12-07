.PHONY: all venv install test clean

PYTHON := $(shell echo $$PY)
PYTHON ?= python3
VENVPATH := .venv/bin/
CLEAN_DIRS := .pytest_cache build *.egg-info dist __pycache__

all: venv install test

venv:
	$(PYTHON) -m venv .venv
	$(VENVPATH)pip install -r requirements-dev.txt

install:
	$(VENVPATH)python setup.py install

test: install
	$(VENVPATH)pytest tests

clean:
	rm -rf $(CLEAN_DIRS)