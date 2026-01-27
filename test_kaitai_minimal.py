from scdms_soudan_spec import complete_test_file


def _as_int(value):
    if isinstance(value, (bytes, bytearray)):
        return int.from_bytes(value, "little")
    return int(value)


def _list_int(values):
    return [_as_int(v) for v in values]


def test_kaitai_minimal_file():
    from soudan import Soudan

    with open("minimal_sample.soudan", "rb") as infile:
        data = Soudan.from_io(infile)
    spec = complete_test_file

    assert _as_int(data.file_hdr.endian_indicator) == spec["file_hdr"]["endian_indicator"]
    df = data.file_hdr.data_format
    df_spec = spec["file_hdr"]["data_format"]
    assert df.daq_major == df_spec["daq_major"]
    assert df.daq_minor == df_spec["daq_minor"]
    assert df.data_format_major == df_spec["data_format_major"]
    assert df.data_format_minor == df_spec["data_format_minor"]

    assert data.detector_hdr.header_num == spec["detector_hdr"]["header_number"]
    assert data.detector_hdr.config_record_len == spec["detector_hdr"]["config_record_len"]
    assert data.detector_hdr.repeat_value == 3

    assert len(data.hdrs) == len(spec["hdrs"])
    for hdr, hdr_spec in zip(data.hdrs, spec["hdrs"]):
        assert hdr.header_num == hdr_spec["header_number"]
        if hdr_spec["header_number"] == 0x10002:
            cc = hdr.charge_config
            cc_spec = hdr_spec["charge_config"]
            assert cc.charge_config_len == cc_spec["charge_config_len"]
            assert cc.detector_code == cc_spec["detector_code"]
            assert cc.tower_num == cc_spec["tower_number"]
            assert cc.channel_post_amp == cc_spec["channel_post_amp"]
            assert cc.channel_bias == cc_spec["channel_bias"]
            assert cc.rtf_offset == cc_spec["rtf_offset"]
            assert cc.delta_t == cc_spec["delta_t"]
            assert cc.trigger_time == cc_spec["trigger_time"]
            assert cc.trace_len == cc_spec["trace_len"]
            assert not hasattr(hdr, "phonon_config") or hdr.phonon_config is None
        else:
            pc = hdr.phonon_config
            pc_spec = hdr_spec["phonon_config"]
            assert pc.phonon_channel_config_record_len == pc_spec["phonon_config_len"]
            assert pc.detector_code == pc_spec["detector_code"]
            assert pc.tower_num == pc_spec["tower_number"]
            assert pc.post_amp_gain == pc_spec["post_amp_gain"]
            assert pc.qet_bias == pc_spec["qet_bias"]
            assert pc.squid_bias == pc_spec["squid_bias"]
            assert pc.squid_lockpoint == pc_spec["squid_lockpoint"]
            assert pc.rtf_offset == pc_spec["rtf_offset"]
            assert pc.variable_gain == pc_spec["variable_gain"]
            assert pc.delta_t == pc_spec["delta_t"]
            assert pc.trigger_time == pc_spec["trigger_time"]
            assert pc.trace_len == pc_spec["trace_len"]
            assert not hasattr(hdr, "charge_config") or hdr.charge_config is None

    spec_records = spec["logical_rcrds"]
    assert len(data.logical_rcrds) == len(spec_records)

    for record, record_spec in zip(data.logical_rcrds, spec_records):
        header = record.header
        assert header == record_spec["event_hdr"]
        section_spec = record_spec["next_section"]["section"]

        if (header >> 16) == 0xA980:
            section = record.section
            assert section.event_size == section_spec["event_size"]
            assert section.event_identifier == ((header >> 16) & 0xFFFF)
            assert section.event_class == ((header >> 8) & 0xF)
            assert section.event_category == ((header >> 12) & 0xF)
            assert section.event_type == (header & 0xFF)
        elif header == 0x00000002:
            section = record.section
            assert section.admin_len == section_spec["admin_len"]
            assert section.series_num_1 == section_spec["series_number_1"]
            assert section.series_num_2 == section_spec["series_number_2"]
            assert section.event_num_in_series == section_spec["event_number_in_series"]
            assert section.seconds_from_epoch == section_spec["seconds_from_epoch"]
            assert section.time_from_last_event == section_spec["time_from_last_event"]
            assert section.live_time_from_last_event == section_spec["live_time_from_last_event"]
        elif header == 0x00000011:
            section = record.section
            tr = section.trace_rcrd
            tr_spec = section_spec["trace_rcrds"]
            assert tr.trace_len == tr_spec["trace_len"]
            assert tr.trace_bookkeeping_header == tr_spec["trace_bookkeeping_header"]
            assert tr.bookkeeping_len == tr_spec["bookkeeping_len"]
            assert tr.digitizer_base_address == tr_spec["digitizer_base_address"]
            assert tr.digitizer_channel == tr_spec["digitizer_channel"]
            assert tr.detector_code == tr_spec["detector_code"]
            assert tr.timebase_header == tr_spec["timebase_header"]
            assert tr.timebase_len == tr_spec["timebase_len"]
            assert tr.t0_in_ns == tr_spec["t0_in_ns"]
            assert tr.delta_t_ns == tr_spec["delta_t_ns"]
            assert tr.num_of_points == tr_spec["num_of_points"]
            assert tr.second_trace_header == tr_spec["second_trace_header"]
            assert tr.num_samples == tr_spec["num_samples"]
            assert _list_int([s.data_selection for s in section.sample_data]) == [
                s["data_selection"] for s in section_spec["sample_data"]
            ]
        elif header == 0x00000021:
            section = record.section
            assert section.history_buffer_len == section_spec["history_buffer_len"]
            assert section.num_time_nvt == section_spec["num_time_nvt"]
            assert _list_int(section.time_nvt) == section_spec["time_nvt"]
            assert section.num_veto_mask_words == section_spec["num_veto_mask_words"]
            assert _list_int(section.time_n_minus_veto_mask) == section_spec["time_n_minus_veto_mask"]
            assert section.num_trigger_times == section_spec["num_trigger_times"]
            assert _list_int(section.times) == section_spec["trigger_times"]
            assert section.num_trigger_mask_words_per_time == section_spec["num_trigger_mask_words"]
            assert _list_int(section.times_minus_trigger_mask) == section_spec["trig_times_minus_trig_mask"]
        elif header == 0x00000060:
            section = record.section
            assert section.len == section_spec["length"]
            assert section.gps_year_day == section_spec["gps_year_day"]
            assert section.gps_status_hour_minute_second == section_spec["gps_status_hour_minute_second"]
            assert section.gps_microsecs_from_gps_second == section_spec["gps_microsecs_from_gps_second"]
        elif header == 0x00000080:
            section = record.section
            assert section.trigger_len == section_spec["trigger_len"]
            assert section.trigger_time == section_spec["trigger_time"]
            assert _list_int(section.individual_trigger_mask) == section_spec["individual_trigger_masks"]
        elif header == 0x00000081:
            section = record.section
            assert section.tlb_len == section_spec["tlb_len"]
            assert _list_int(section.tower_mask) == section_spec["tower_mask"]
        elif header == 0x00000022:
            section = record.section
            assert section.len_to_next_header == section_spec["len_to_next_header"]
            assert section.clocking_interval == section_spec["clocking_interval"]
            assert section.tower_num == section_spec["tower_number"]
            assert _list_int(section.detector_codes) == section_spec["detector_codes"]
            assert _list_int(section.j_codes) == section_spec["j_codes"]
            assert _list_int(section.counter_values) == section_spec["counter_values"]
        elif header == 0x00000031:
            section = record.section
            assert section.len_to_next_header == section_spec["len_to_next_header"]
            assert section.clocking_interval == section_spec["clocking_interval"]
            assert section.num_entries == section_spec["num_entries"]
            assert _list_int(section.detector_code) == section_spec["detector_code"]
            assert _list_int(section.counter_value_det_code) == section_spec["counter_value_det_code"]
        else:
            raise AssertionError(f"Unexpected record header: {header:#x}")
