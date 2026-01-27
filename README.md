## Soudan binary parsing and test fixtures

This repo provides a small, deterministic Soudan `.soudan` fixture, a Construct-based parser that converts it to HDF5, and a Kaitai schema that parses the same binary stream. The goal is to keep a tiny file for fast iteration while exercising the full record layout and providing regression tests for both parsing paths.

### How it fits together
- The **spec** defines the minimal binary payload and expected outputs.
- The **generator** builds `minimal_sample.soudan` from the spec.
- The **parser** converts that binary into `minimal_sample.hdf5`.
- The **tests** verify both the HDF5 output and the Kaitai parsing results.
- The **pretty printer** renders the Kaitai parse into Markdown and compares it to a committed snapshot.

### Quickstart
Use the Makefile to regenerate the minimal sample, parse it, and run tests:

```
make all
```

Or run individual steps:

```
make build-soudan
make build-hdf5
make test
make pretty-print
make test-pretty-print
```

### Key files
**Spec and fixtures**
- `scdms_soudan_spec.py`: single source of truth for Construct schema, minimal payload, and expected HDF5 values.
- `minimal_sample.soudan` / `minimal_sample.hdf5`: tiny binary fixture and its parsed HDF5 output.
- `kaitai_pretty_print.md`: snapshot of the Kaitai Markdown dump for regression testing.

**Parsers and generators**
- `scdms_soudan_minimal_file.py`: builds the minimal `.soudan` file from the spec.
- `scdms_soudan_parser.py`: parses `.soudan` into HDF5 using Construct.
- `kaitai/scdms_soudan.ksy`: Kaitai schema for the same binary format.
- `kaitai_pretty_print.py`: Markdown pretty-printer for the Kaitai parse output.

**Tests**
- `test_minimal_hdf5.py`: checks HDF5 datasets, shapes, and values.
- `test_kaitai_minimal.py`: validates the Kaitai parse against the spec.
- `test_pretty_print.py`: compares pretty-print output against `kaitai_pretty_print.md`.

**Notebooks (exploration)**
- `scdms_soudan_minimal_file.ipynb`
- `scdms_soudan_parser.ipynb`
