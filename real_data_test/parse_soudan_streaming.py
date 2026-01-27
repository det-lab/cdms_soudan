from __future__ import annotations

import collections
import resource
import struct
import time
from pathlib import Path


def _read_u4(f) -> int | None:
    data = f.read(4)
    if len(data) < 4:
        return None
    return struct.unpack('<I', data)[0]


def scan_counts(file_path: Path) -> tuple[collections.Counter[int], int, float]:
    start = time.perf_counter()
    counts: collections.Counter[int] = collections.Counter()

    size = file_path.stat().st_size
    with file_path.open('rb') as f:
        # file_hdr (8) + detector_hdr (8)
        f.seek(8)
        detector_header = f.read(8)
        if len(detector_header) < 8:
            return counts, 0, 0.0
        _, config_record_len = struct.unpack('<II', detector_header)
        repeat_value = (config_record_len // 72) + (config_record_len // 144)

        # skip file_hdr + detector_hdr
        f.seek(16)

        # header list
        for _ in range(repeat_value):
            hdr = _read_u4(f)
            if hdr is None:
                break
            if hdr == 0x10001:
                f.seek(48, 1)
            elif hdr == 0x10002:
                f.seek(36, 1)
            else:
                break

        # logical records
        while f.tell() < size:
            header = _read_u4(f)
            if header is None:
                break
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
                _, num_time_nvt = struct.unpack('<II', base)
                f.seek(4 * num_time_nvt, 1)
                num_veto_mask_words = _read_u4(f)
                if num_veto_mask_words is None:
                    break
                f.seek(4 * num_time_nvt * num_veto_mask_words, 1)
                num_trigger_times = _read_u4(f)
                if num_trigger_times is None:
                    break
                f.seek(4 * num_trigger_times, 1)
                num_trigger_mask_words_per_time = _read_u4(f)
                if num_trigger_mask_words_per_time is None:
                    break
                f.seek(4 * num_trigger_mask_words_per_time * num_trigger_times, 1)
            elif header == 0x00000060:
                length = _read_u4(f)
                if length is None:
                    break
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

    elapsed = time.perf_counter() - start
    return counts, sum(counts.values()), elapsed


def _format_header(header: int) -> str:
    return f"0x{header:08x}"


if __name__ == "__main__":
    data_path = Path(__file__).with_name("01150211_1500_F0026")
    if not data_path.exists():
        raise SystemExit(f"missing data file: {data_path}")

    counts, total, elapsed = scan_counts(data_path)

    print("Python backend (streaming scan)")
    print(f"  file: {data_path.name}")
    print(f"  logical records: {total}")
    max_rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f"  elapsed: {elapsed:.2f}s")
    print(f"  max_rss_kb: {max_rss_kb}")
    print("  header counts:")
    for header, count in counts.most_common():
        print(f"    {_format_header(header)}: {count}")

    print("\nNotes:")
    print("- This is a streaming scan; it avoids building full in-memory objects.")
    print("- Memory usage is expected to be low (bounded by counters and buffers).")
