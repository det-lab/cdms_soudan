# Soudan file parse report — `01150211_1500_F0026`

Date: 2026-01-27

## Location
Source data file (Open Science Network):
- `supercdms-data/CDMS/Soudan/R135/Raw/01150211_1500/01150211_1500_F0026.gz`

All real-data test assets live under:
- `cdms_soudan/real_data_test/`

Data file (not committed):
- `cdms_soudan/real_data_test/01150211_1500_F0026`

## Scripts
- Awkward backend (full parse): `cdms_soudan/real_data_test/parse_soudan_awkward.py`
- Awkward backend (first traces): `cdms_soudan/real_data_test/parse_soudan_awkward_first_traces.py`
- Python backend (streaming scan): `cdms_soudan/real_data_test/parse_soudan_streaming.py`

## How to run
From repo root:

Awkward backend:
```bash
.venv/bin/python cdms_soudan/real_data_test/parse_soudan_awkward.py
```

Awkward backend (first N traces):
```bash
.venv/bin/python cdms_soudan/real_data_test/parse_soudan_awkward_first_traces.py --limit 100
```

Python backend (streaming scan):
```bash
.venv/bin/python cdms_soudan/real_data_test/parse_soudan_streaming.py
```

For detailed RSS/CPU stats, wrap with:
```bash
/usr/bin/time -v .venv/bin/python cdms_soudan/real_data_test/parse_soudan_awkward.py
/usr/bin/time -v .venv/bin/python cdms_soudan/real_data_test/parse_soudan_streaming.py
```

---

## Summary
- The file is 124 MB, which makes a full Construct parse memory-heavy.
- A full in-memory Construct parse (`soudan.parse(raw_bytes)`) previously caused an OOM kill (exit code 137).
- The Awkward backend completes after fixing union-field access and flattening.
- The Awkward “first traces” script still loads the full file into Awkward buffers before slicing.
- The Python backend is validated via a streaming scan that avoids materializing records in memory.

---

## Results (latest rerun)

### Performance summary (this machine)
- Awkward backend (full): 36.05s, max RSS 4403.70 MB (4.30 GB)
- Awkward backend (first traces, limit 100): 33.22s, max RSS 4406.48 MB (4.30 GB)
- Python backend (streaming scan): 0.09s, max RSS 19.26 MB (0.02 GB)

### Awkward backend (full parse)
Using `cdms_soudan/real_data_test/parse_soudan_awkward.py`.

Logical record counts (by header):
- Total logical records: 30,156
- `0x00000011`: 28,002
- `0x00000002`: 359
- `0x00000021`: 359
- `0x00000060`: 359
- `0x00000080`: 359
- `0x00000081`: 359
- `0xa9800000`: 323
- `0xa9800100`: 36

Extended stats:
- `trace_len`: min=2096 max=8240 mean=4564.10
- `num_samples`: min=1024 max=4096 mean=2258.05
- `event_size`: min=356848 max=379744 mean=359656.45
- `gps_len` distribution: `{12: 359}`
- `history_buffer_len`: min=96 max=22992 mean=2904.45
- `trigger_len`: min=28 max=28 mean=28.00

Notes:
- No `0x00000022` (detector trigger rates) or `0x00000031` (veto trigger rates) records were observed in this file.

### Awkward backend (first traces)
Using `cdms_soudan/real_data_test/parse_soudan_awkward_first_traces.py --limit 100`.

- Traces parsed: 100
- `trace_len`: min=2096 max=8240 mean=5045.12
- `num_samples`: min=1024 max=4096 mean=2498.56
- `detector_code` counts (top 10):
  - 11005000: 2
  - 11005001: 2
  - 11005002: 2
  - 11005003: 2
  - 11005004: 2
  - 11005005: 2
  - 11005006: 2
  - 11005007: 2
  - 11005008: 2
  - 11005009: 2
- `sample values`: min=1746 max=4095 mean=2189.37

Notes:
- This script still calls `Reader.load`, so it loads the full file before slicing the first N traces.
- For true partial parsing, the shared-library `fill` function would need a streaming/limit mode.

### Python backend (streaming scan)
Using `cdms_soudan/real_data_test/parse_soudan_streaming.py`.

Logical record counts (by header):
- Total logical records: 30,156
- `0x00000011`: 28,002
- `0x00000002`: 359
- `0x00000021`: 359
- `0x00000060`: 359
- `0x00000080`: 359
- `0x00000081`: 359
- `0xa9800000`: 323
- `0xa9800100`: 36

Notes:
- This scan validates record boundaries and lengths consistent with the schema.
- It avoids materializing record contents, so memory usage stays low.

---

## Implementation notes
- The scripts report elapsed wall time internally and print max RSS via `resource.getrusage`.
- For more detailed RSS/CPU stats, use `/usr/bin/time -v` if available on your system.

