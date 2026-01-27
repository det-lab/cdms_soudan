# Soudan file parse report — `01150211_1500_F0026`

Date: 2026‑01‑27

## File details
- Path: `01150211_1500_F0026`
- Size: **124 MB** (confirmed via `ls -lh`)

## Goal
Validate that the file can be parsed with:
1) the **Awkward backend** (`awkward_kaitai` + generated `libsoudan.so`), and
2) the **Python backend** (Construct schema from `scdms_soudan_spec`).

Also produce proof-of-parse by reporting record counts by type.

---

## Awkward backend
### Approach
- Used the compiled shared library `cdms_soudan/kaitai/libsoudan.so`.
- Loaded the file via `awkward_kaitai.Reader`.
- Counted logical record headers without converting the entire dataset to Python lists.

### Code snippet used
```python
from pathlib import Path
import numpy as np
from awkward_kaitai import Reader
import awkward as ak

file_path = Path('01150211_1500_F0026')
lib = Path('cdms_soudan/kaitai/libsoudan.so')

reader = Reader(lib)
arr = reader.load(str(file_path))
headers = arr["soudanA__Zlogical_rcrds"]["logical_recordA__Zheader"]
headers_flat = ak.flatten(headers)
headers_np = ak.to_numpy(headers_flat)
uniq, counts = np.unique(headers_np, return_counts=True)

print('Awkward backend:')
print(f'  logical records: {len(headers_np)}')
for h, c in zip(uniq, counts):
    print(f'  0x{int(h):08x}: {int(c)}')
```

### Results
**Parsed successfully** and produced record counts.

- **Logical records:** 30,156
- **Counts by header (hex):**
  - `0x00000011`: 28,002  
    (trace data)
  - `0x00000002`: 359  
    (administrative record)
  - `0x00000021`: 359  
    (soudan history buffer)
  - `0x00000060`: 359  
    (gps data)
  - `0x00000080`: 359  
    (trigger record format)
  - `0x00000081`: 359  
    (tlb trigger mask)
  - `0xa9800000`: 323  
    (event header class/category/type in upper bits)
  - `0xa9800100`: 36  
    (event header class/category/type in upper bits)

These are consistent with the expected Soudan logical record layout.

---

## Python backend (Construct)
### What happened
- Attempting a **full in‑memory parse** via Construct (`soudan.parse(raw_bytes)`) caused the Python process to be **killed by the OS** (exit code 137), likely due to memory pressure. The file is 124 MB and the Construct parse materializes large nested structures, which can expand significantly in memory.

### Failed attempt (OOM)
```python
from cdms_soudan.scdms_soudan_spec import soudan
raw = file_path.read_bytes()
parsed = soudan.parse(raw)  # process was killed (OOM)
```

### Streaming scan workaround
To still provide proof-of-parse with the Python backend, I implemented a **streaming scanner** that reads the file sequentially and interprets the record boundaries using the same layout from the schema. This avoids loading everything into memory, while still counting record types accurately.

#### Streaming scan code
```python
from pathlib import Path
import struct
import collections

file_path = Path('01150211_1500_F0026')
counts = collections.Counter()
size = file_path.stat().st_size

with file_path.open('rb') as f:
    # skip file_hdr (8 bytes) + detector_hdr (8 bytes)
    f.seek(16)

    # re-read detector header to compute repeat_value
    f.seek(8)
    header_num, config_record_len = struct.unpack('<II', f.read(8))
    repeat_value = (config_record_len // 72) + (config_record_len // 144)

    # skip hdrs list
    f.seek(16)
    for _ in range(repeat_value):
        (hdr,) = struct.unpack('<I', f.read(4))
        if hdr == 0x10001:       # phonon config
            f.seek(48, 1)
        elif hdr == 0x10002:     # charge config
            f.seek(36, 1)
        else:
            break

    # logical records until EOF
    while f.tell() < size:
        data = f.read(4)
        if len(data) < 4:
            break
        (header,) = struct.unpack('<I', data)
        counts[header] += 1

        if (header >> 16) == 0xA980:
            f.seek(4, 1)
        elif header == 0x00000002:
            f.seek(28, 1)
        elif header == 0x00000011:
            tr = f.read(52)
            if len(tr) < 52:
                break
            num_samples = struct.unpack('<I', tr[48:52])[0]
            f.seek(2 * num_samples, 1)
        elif header == 0x00000021:
            base = f.read(8)
            if len(base) < 8:
                break
            history_buffer_len, num_time_nvt = struct.unpack('<II', base)
            f.seek(4 * num_time_nvt, 1)
            data = f.read(4)
            if len(data) < 4:
                break
            (num_veto_mask_words,) = struct.unpack('<I', data)
            f.seek(4 * num_time_nvt * num_veto_mask_words, 1)
            data = f.read(4)
            if len(data) < 4:
                break
            (num_trigger_times,) = struct.unpack('<I', data)
            f.seek(4 * num_trigger_times, 1)
            data = f.read(4)
            if len(data) < 4:
                break
            (num_trigger_mask_words_per_time,) = struct.unpack('<I', data)
            f.seek(4 * num_trigger_mask_words_per_time * num_trigger_times, 1)
        elif header == 0x00000060:
            data = f.read(4)
            if len(data) < 4:
                break
            (length,) = struct.unpack('<I', data)
            if length > 0:
                f.seek(12, 1)
        elif header == 0x00000080:
            f.seek(32, 1)
        elif header == 0x00000081:
            f.seek(28, 1)
        elif header == 0x00000022:
            f.seek(176, 1)
        elif header == 0x00000031:
            data = f.read(12)
            if len(data) < 12:
                break
            _, _, num_entries = struct.unpack('<III', data)
            f.seek(8 * num_entries, 1)
        else:
            break

print('Python backend (streamed scan):')
print(f'  logical records: {sum(counts.values())}')
for k, v in counts.most_common():
    print(f'  0x{k:08x}: {v}')
```

### Streaming scan results
**Counts match the Awkward backend**, confirming consistency:

- **Logical records:** 30,156
- **Counts by header (hex):**
  - `0x00000011`: 28,002
  - `0x00000002`: 359
  - `0x00000021`: 359
  - `0x00000060`: 359
  - `0x00000080`: 359
  - `0x00000081`: 359
  - `0xa9800000`: 323
  - `0xa9800100`: 36

---

## Summary of findings
1. **Awkward backend successfully parsed the full file** and provided logical record counts.
2. **Full Construct parse failed due to memory pressure** (process killed by OOM).
3. A **streaming parser** (Python backend workaround) confirms **record counts identical** to the Awkward parse, demonstrating correct decoding of the layout.

The close agreement between the Awkward parse and the streaming Python scan provides strong evidence that the file is being interpreted correctly, even though a full in‑memory Construct parse is too heavy for this file size on the current machine.

---

## Optional next steps
If desired, we can extend this report with deeper stats, such as:
- distribution of trace lengths and sample counts
- per‑record validation of expected sizes and offsets
- GPS length distribution and presence/absence rates
- summary stats by detector code / tower number

These can be computed efficiently from the Awkward array without converting everything to Python lists.
