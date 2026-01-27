.PHONY: all build-soudan build-hdf5 test

all: build-soudan build-hdf5 test

build-soudan:
	python scdms_soudan_minimal_file.py

build-hdf5:
	python scdms_soudan_parser.py

test:
	pytest -q test_minimal_hdf5.py
