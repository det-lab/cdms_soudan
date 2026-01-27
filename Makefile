.PHONY: all setup build-soudan build-hdf5 kaitai-gen test test-kaitai pretty-print test-pretty-print

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
KSC ?= ksc
SAMPLE_SOU := minimal_sample.soudan
SAMPLE_H5 := minimal_sample.hdf5
KSC_PY := soudan.py
PRETTY_MD := kaitai_pretty_print.md

all: setup build-soudan build-hdf5 kaitai-gen test test-kaitai test-pretty-print

setup: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	touch $(VENV)/bin/activate

$(SAMPLE_SOU): $(VENV)/bin/activate scdms_soudan_minimal_file.py scdms_soudan_spec.py
	$(PYTHON) scdms_soudan_minimal_file.py

build-soudan: $(SAMPLE_SOU)

$(SAMPLE_H5): $(VENV)/bin/activate $(SAMPLE_SOU) scdms_soudan_parser.py
	$(PYTHON) scdms_soudan_parser.py

build-hdf5: $(SAMPLE_H5)

$(KSC_PY): kaitai/scdms_soudan.ksy
	$(KSC) -t python kaitai/scdms_soudan.ksy

kaitai-gen: $(KSC_PY)

test: $(SAMPLE_H5)
	$(PYTEST) -q test_minimal_hdf5.py

test-kaitai: $(SAMPLE_SOU) $(KSC_PY)
	$(PYTEST) -q test_kaitai_minimal.py

$(PRETTY_MD): $(SAMPLE_SOU) $(KSC_PY) kaitai_pretty_print.py
	$(PYTHON) kaitai_pretty_print.py $(SAMPLE_SOU) --output $(PRETTY_MD)

pretty-print: $(PRETTY_MD)

test-pretty-print: $(SAMPLE_SOU) $(KSC_PY) $(PRETTY_MD)
	$(PYTEST) -q test_pretty_print.py
