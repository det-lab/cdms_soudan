#!/usr/bin/env python3
import argparse
from pathlib import Path


def _as_int(value):
    if isinstance(value, (bytes, bytearray)):
        return int.from_bytes(value, "little")
    return int(value)


def _fmt_value(value):
    if isinstance(value, (bytes, bytearray)):
        return f"0x{_as_int(value):08x} {list(value)}"
    if isinstance(value, list):
        return "[" + ", ".join(_fmt_value(v) for v in value) + "]"
    return str(value)


def _md_table(rows):
    lines = ["| field | value |", "| --- | --- |"]
    lines.extend([f"| {k} | {v} |" for k, v in rows])
    return "\n".join(lines)


def _record_type(header):
    if (header >> 16) == 0xA980:
        return "event_header", 0xA980
    return {
        0x00000002: "administrative_record",
        0x00000011: "trace_data",
        0x00000021: "soudan_history_buffer",
        0x00000060: "gps_data",
        0x00000080: "trigger_record",
        0x00000081: "tlb_trigger_mask_record",
        0x00000022: "detector_trigger_rates",
        0x00000031: "veto_trigger_rates",
    }.get(header, "unknown"), header


def _render_file(data, max_records):
    out = []
    out.append("# Soudan file dump")

    out.append("\n## File header")
    fh = data.file_hdr
    out.append(
        _md_table(
            [
                ("endian_indicator", _fmt_value(fh.endian_indicator)),
                ("daq_major", fh.data_format.daq_major),
                ("daq_minor", fh.data_format.daq_minor),
                ("data_format_major", fh.data_format.data_format_major),
                ("data_format_minor", fh.data_format.data_format_minor),
            ]
        )
    )

    out.append("\n## Detector header")
    dh = data.detector_hdr
    out.append(
        _md_table(
            [
                ("header_num", dh.header_num),
                ("config_record_len", dh.config_record_len),
                ("repeat_value", dh.repeat_value),
            ]
        )
    )

    out.append(f"\n## Detector configs ({len(data.hdrs)})")
    for i, hdr in enumerate(data.hdrs):
        out.append(f"\n### Header {i}")
        rows = [("header_num", hdr.header_num)]
        if hasattr(hdr, "charge_config"):
            cc = hdr.charge_config
            rows.extend(
                [
                    ("charge_config_len", cc.charge_config_len),
                    ("detector_code", cc.detector_code),
                    ("tower_num", cc.tower_num),
                    ("channel_post_amp", cc.channel_post_amp),
                    ("channel_bias", cc.channel_bias),
                    ("rtf_offset", cc.rtf_offset),
                    ("delta_t", cc.delta_t),
                    ("trigger_time", cc.trigger_time),
                    ("trace_len", cc.trace_len),
                ]
            )
        if hasattr(hdr, "phonon_config"):
            pc = hdr.phonon_config
            rows.extend(
                [
                    ("phonon_config_len", pc.phonon_channel_config_record_len),
                    ("detector_code", pc.detector_code),
                    ("tower_num", pc.tower_num),
                    ("post_amp_gain", pc.post_amp_gain),
                    ("qet_bias", pc.qet_bias),
                    ("squid_bias", pc.squid_bias),
                    ("squid_lockpoint", pc.squid_lockpoint),
                    ("rtf_offset", pc.rtf_offset),
                    ("variable_gain", pc.variable_gain),
                    ("delta_t", pc.delta_t),
                    ("trigger_time", pc.trigger_time),
                    ("trace_len", pc.trace_len),
                ]
            )
        out.append(_md_table([(k, _fmt_value(v)) for k, v in rows]))

    out.append(f"\n## Logical records ({len(data.logical_rcrds)})")
    records = data.logical_rcrds if max_records is None else data.logical_rcrds[:max_records]
    for i, record in enumerate(records):
        header = record.header
        name, _ = _record_type(header)
        out.append(f"\n### Record {i}: {name} (0x{header:08x})")
        section = record.section

        if name == "event_header":
            rows = [
                ("event_size", section.event_size),
                ("event_identifier", section.event_identifier),
                ("event_class", section.event_class),
                ("event_category", section.event_category),
                ("event_type", section.event_type),
            ]
        elif name == "administrative_record":
            rows = [
                ("admin_len", section.admin_len),
                ("series_num_1", section.series_num_1),
                ("series_num_2", section.series_num_2),
                ("event_num_in_series", section.event_num_in_series),
                ("seconds_from_epoch", section.seconds_from_epoch),
                ("time_from_last_event", section.time_from_last_event),
                ("live_time_from_last_event", section.live_time_from_last_event),
            ]
        elif name == "trace_data":
            tr = section.trace_rcrd
            rows = [
                ("trace_len", tr.trace_len),
                ("trace_bookkeeping_header", tr.trace_bookkeeping_header),
                ("bookkeeping_len", tr.bookkeeping_len),
                ("digitizer_base_address", tr.digitizer_base_address),
                ("digitizer_channel", tr.digitizer_channel),
                ("detector_code", tr.detector_code),
                ("timebase_header", tr.timebase_header),
                ("timebase_len", tr.timebase_len),
                ("t0_in_ns", tr.t0_in_ns),
                ("delta_t_ns", tr.delta_t_ns),
                ("num_of_points", tr.num_of_points),
                ("second_trace_header", tr.second_trace_header),
                ("num_samples", tr.num_samples),
                ("sample_data", [s.data_selection for s in section.sample_data]),
            ]
        elif name == "soudan_history_buffer":
            rows = [
                ("history_buffer_len", section.history_buffer_len),
                ("num_time_nvt", section.num_time_nvt),
                ("time_nvt", section.time_nvt),
                ("num_veto_mask_words", section.num_veto_mask_words),
                ("time_n_minus_veto_mask", section.time_n_minus_veto_mask),
                ("num_trigger_times", section.num_trigger_times),
                ("times", section.times),
                ("num_trigger_mask_words_per_time", section.num_trigger_mask_words_per_time),
                ("times_minus_trigger_mask", section.times_minus_trigger_mask),
            ]
        elif name == "gps_data":
            rows = [
                ("len", section.len),
                ("gps_year_day", section.gps_year_day),
                ("gps_status_hour_minute_second", section.gps_status_hour_minute_second),
                ("gps_microsecs_from_gps_second", section.gps_microsecs_from_gps_second),
            ]
        elif name == "trigger_record":
            rows = [
                ("trigger_len", section.trigger_len),
                ("trigger_time", section.trigger_time),
                ("individual_trigger_mask", section.individual_trigger_mask),
            ]
        elif name == "tlb_trigger_mask_record":
            rows = [
                ("tlb_len", section.tlb_len),
                ("tower_mask", section.tower_mask),
            ]
        elif name == "detector_trigger_rates":
            rows = [
                ("len_to_next_header", section.len_to_next_header),
                ("clocking_interval", section.clocking_interval),
                ("tower_num", section.tower_num),
                ("detector_codes", section.detector_codes),
                ("j_codes", section.j_codes),
                ("counter_values", section.counter_values),
            ]
        elif name == "veto_trigger_rates":
            rows = [
                ("len_to_next_header", section.len_to_next_header),
                ("clocking_interval", section.clocking_interval),
                ("num_entries", section.num_entries),
                ("detector_code", section.detector_code),
                ("counter_value_det_code", section.counter_value_det_code),
            ]
        else:
            rows = [("raw", "unhandled record type")]

        out.append(_md_table([(k, _fmt_value(v)) for k, v in rows]))

    if max_records is not None and len(data.logical_rcrds) > max_records:
        out.append(f"\n... {len(data.logical_rcrds) - max_records} more records omitted ...")

    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Pretty print Soudan file (Kaitai)")
    parser.add_argument("input", nargs="?", default="minimal_sample.soudan")
    parser.add_argument("--format", choices=["md", "markdown"], default="md")
    parser.add_argument("--output", default="-")
    parser.add_argument("--max-records", type=int, default=None)
    args = parser.parse_args()

    try:
        from soudan import Soudan
    except Exception as exc:
        raise SystemExit(
            "Missing Kaitai parser. Run `make kaitai-gen` first."
        ) from exc

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"File not found: {input_path}")

    with input_path.open("rb") as infile:
        data = Soudan.from_io(infile)

    output = _render_file(data, args.max_records)
    if args.output == "-":
        print(output, end="")
    else:
        Path(args.output).write_text(output)


if __name__ == "__main__":
    main()
