from __future__ import annotations

import collections
import resource
import time
from pathlib import Path

import awkward as ak
import numpy as np

from awkward_kaitai import Reader


def _format_header(header: int) -> str:
    return f"0x{header:08x}"


def _flatten(array):
    return ak.flatten(array, axis=None)


def _stats(array) -> tuple[float, float, float] | None:
    flat = _flatten(array)
    if ak.count(flat) == 0:
        return None
    return float(ak.min(flat)), float(ak.max(flat)), float(ak.mean(flat))


def _project_union(array, field_name: str):
    layout = ak.to_layout(array)
    if isinstance(layout, ak.contents.UnionArray):
        matches = []
        for idx, content in enumerate(layout.contents):
            if isinstance(content, ak.contents.RecordArray) and field_name in content.fields:
                matches.append(idx)
        if len(matches) == 1:
            return ak.Array(layout.project(matches[0]))
    return array


def summarize(file_path: Path, lib_path: Path) -> None:
    start = time.perf_counter()

    reader = Reader(lib_path)
    arr = reader.load(str(file_path))

    records = ak.flatten(arr["soudanA__Zlogical_rcrds"])
    headers_arr = records["logical_recordA__Zheader"]
    headers = ak.to_numpy(headers_arr)
    uniq, counts = np.unique(headers, return_counts=True)

    elapsed = time.perf_counter() - start

    print("Awkward backend", flush=True)
    print(f"  file: {file_path.name}", flush=True)
    print(f"  logical records: {len(headers)}", flush=True)
    max_rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f"  elapsed: {elapsed:.2f}s", flush=True)
    print(f"  max_rss_kb: {max_rss_kb}", flush=True)
    print("  header counts:", flush=True)
    for header, count in zip(uniq, counts):
        print(f"    {_format_header(int(header))}: {int(count)}", flush=True)

    # Extended stats
    print("\nExtended stats:", flush=True)

    def _print_stats(label: str, values) -> None:
        stats = _stats(values)
        if stats is None:
            return
        min_v, max_v, mean_v = stats
        print(f"  {label}: min={min_v:g} max={max_v:g} mean={mean_v:.2f}", flush=True)

    # Trace record stats (header 0x11)
    trace_records = records[headers_arr == 0x00000011]
    trace_section = _project_union(
        trace_records["logical_recordA__Zsection"], "trace_dataA__Ztrace_rcrd"
    )
    trace = trace_section["trace_dataA__Ztrace_rcrd"]
    _print_stats("trace_len", trace["trace_recordA__Ztrace_len"])
    _print_stats("num_samples", trace["trace_recordA__Znum_samples"])

    # Event header stats (A980)
    event_records = records[(headers_arr >> 16) == 0xA980]
    event_section = _project_union(
        event_records["logical_recordA__Zsection"], "event_headerA__Zevent_size"
    )
    event = event_section["event_headerA__Zevent_size"]
    _print_stats("event_size", event)

    # GPS data stats
    gps_records = records[headers_arr == 0x00000060]
    gps_section = _project_union(gps_records["logical_recordA__Zsection"], "gps_dataA__Zlen")
    gps_len = ak.to_numpy(gps_section["gps_dataA__Zlen"])
    if len(gps_len):
        uniq_gps, counts_gps = np.unique(gps_len, return_counts=True)
        gps_counts = dict(zip(uniq_gps.tolist(), counts_gps.tolist()))
        print(f"  gps_len distribution: {gps_counts}", flush=True)

    # Soudan history buffer stats
    hb_records = records[headers_arr == 0x00000021]
    hb_section = _project_union(
        hb_records["logical_recordA__Zsection"], "soudan_history_bufferA__Zhistory_buffer_len"
    )
    hb = hb_section["soudan_history_bufferA__Zhistory_buffer_len"]
    _print_stats("history_buffer_len", hb)

    # Trigger record stats
    trigger_records = records[headers_arr == 0x00000080]
    trigger_section = _project_union(
        trigger_records["logical_recordA__Zsection"], "trigger_record_formatA__Ztrigger_len"
    )
    trigger_len = trigger_section["trigger_record_formatA__Ztrigger_len"]
    _print_stats("trigger_len", trigger_len)

    # Detector trigger rates stats
    dtr_records = records[headers_arr == 0x00000022]
    if len(dtr_records):
        dtr_section = _project_union(
            dtr_records["logical_recordA__Zsection"],
            "detector_trigger_ratesA__Zlen_to_next_header",
        )
        dtr = dtr_section["detector_trigger_ratesA__Zlen_to_next_header"]
        _print_stats("detector_trigger_rates len_to_next_header", dtr)

    # Veto trigger rates stats
    vtr_records = records[headers_arr == 0x00000031]
    if len(vtr_records):
        vtr_section = _project_union(
            vtr_records["logical_recordA__Zsection"],
            "veto_trigger_ratesA__Zlen_to_next_header",
        )
        vtr = vtr_section["veto_trigger_ratesA__Zlen_to_next_header"]
        _print_stats("veto_trigger_rates len_to_next_header", vtr)

    print("\nNotes:", flush=True)
    print("- Memory usage depends on Awkward buffers and the size of the file.", flush=True)
    print("- For precise RSS, run under /usr/bin/time -v or a profiler.", flush=True)


if __name__ == "__main__":
    data_path = Path(__file__).with_name("01150211_1500_F0026")
    lib_path = Path(__file__).parents[1] / "kaitai" / "libsoudan.so"

    if not data_path.exists():
        raise SystemExit(f"missing data file: {data_path}")
    if not lib_path.exists():
        raise SystemExit(f"missing shared library: {lib_path}")

    summarize(data_path, lib_path)
