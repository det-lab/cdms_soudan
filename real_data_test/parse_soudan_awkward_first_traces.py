from __future__ import annotations

import argparse
import time
from pathlib import Path

import awkward as ak
import numpy as np

from awkward_kaitai import Reader


def _safe_numpy(array) -> np.ndarray:
    return ak.to_numpy(ak.flatten(array))


def summarize_first_traces(file_path: Path, lib_path: Path, limit: int = 1000) -> None:
    start = time.perf_counter()

    reader = Reader(lib_path)
    arr = reader.load(str(file_path))

    records = ak.flatten(arr["soudanA__Zlogical_rcrds"])
    headers = records["logical_recordA__Zheader"]
    trace_records = records[headers == 0x00000011][:limit]

    trace_meta = trace_records["logical_recordA__Zsection"]["trace_dataA__Ztrace_rcrd"]
    trace_len = _safe_numpy(trace_meta["trace_recordA__Ztrace_len"])
    num_samples = _safe_numpy(trace_meta["trace_recordA__Znum_samples"])
    detector_code = _safe_numpy(trace_meta["trace_recordA__Zdetector_code"])

    sample_records = trace_records["logical_recordA__Zsection"]["trace_dataA__Zsample_data"]
    sample_a = _safe_numpy(sample_records["data_sampleA__Zsample_a"])
    sample_b = _safe_numpy(sample_records["data_sampleA__Zsample_b"])
    if len(sample_a) or len(sample_b):
        samples_arr = np.concatenate([sample_a, sample_b]).astype(np.int64, copy=False)
    else:
        samples_arr = np.array([], dtype=np.int64)

    elapsed = time.perf_counter() - start

    print("Awkward backend (first traces)")
    print(f"  file: {file_path.name}")
    print(f"  traces: {len(trace_len)}")
    print(f"  elapsed: {elapsed:.2f}s")
    if len(trace_len):
        print(f"  trace_len: min={trace_len.min()} max={trace_len.max()} mean={trace_len.mean():.2f}")
    if len(num_samples):
        print(f"  num_samples: min={num_samples.min()} max={num_samples.max()} mean={num_samples.mean():.2f}")
    if len(detector_code):
        uniq, counts = np.unique(detector_code, return_counts=True)
        print("  detector_code counts (top 10):")
        for code, count in sorted(zip(uniq, counts), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    {int(code)}: {int(count)}")
    if len(samples_arr):
        print(
            f"  sample values: min={samples_arr.min()} max={samples_arr.max()} mean={samples_arr.mean():.2f}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse first N traces using Awkward backend")
    parser.add_argument("--limit", type=int, default=1000, help="number of trace records to parse")
    parser.add_argument("--file", type=Path, default=Path(__file__).with_name("01150211_1500_F0026"))
    parser.add_argument("--lib", type=Path, default=Path(__file__).parents[1] / "kaitai" / "libsoudan.so")
    args = parser.parse_args()

    if not args.file.exists():
        raise SystemExit(f"missing data file: {args.file}")
    if not args.lib.exists():
        raise SystemExit(f"missing shared library: {args.lib}")

    summarize_first_traces(args.file, args.lib, limit=args.limit)
