.PHONY: all setup build-soudan build-hdf5 kaitai-gen test test-kaitai

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

all: setup build-soudan build-hdf5 kaitai-gen test test-kaitai

setup: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

build-soudan:
	$(PYTHON) scdms_soudan_minimal_file.py

build-hdf5:
	$(PYTHON) scdms_soudan_parser.py

kaitai-gen:
	ksc -t python kaitai/scdms_soudan.ksy

test:
	$(PYTEST) -q test_minimal_hdf5.py

test-kaitai:
	$(PYTEST) -q test_kaitai_minimal.py
