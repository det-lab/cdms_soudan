# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: cdms
#     language: python
#     name: python3
# ---

# %%
from construct import *

format_word = Struct(
    "daq_major" / Byte,
    "daq_minor" / Byte,
    "data_format_major" / Byte,
    "data_format_minor" / Byte,
)

two_word_file_header = Struct("endian_indicator" / Int32ul, "data_format" / format_word)

detector_hdr = Struct(
    "header_number" / Int32ul,
    "config_record_len" / Int32ul,
    "repeat_value"
    / Computed(
        lambda this: (this.config_record_len // 72) + (this.config_record_len // 144)
    ),
)

charge_config_header = Struct(
    "charge_config_len" / Int32ul,
    "detector_code" / Int32sl,
    "tower_number" / Int32sl,
    "channel_post_amp" / Int32sl,
    "channel_bias" / Int32sl,
    "rtf_offset" / Int32sl,
    "delta_t" / Int32sl,
    "trigger_time" / Int32sl,
    "trace_len" / Int32sl,
)

phonon_config_header = Struct(
    "phonon_config_len" / Int32ul,
    "detector_code" / Int32sl,
    "tower_number" / Int32sl,
    "post_amp_gain" / Int32sl,
    "qet_bias" / Int32sl,
    "squid_bias" / Int32sl,
    "squid_lockpoint" / Int32sl,
    "rtf_offset" / Int32sl,
    "variable_gain" / Int32sl,
    "delta_t" / Int32sl,
    "trigger_time" / Int32sl,
    "trace_len" / Int32sl,
)

header_list = Struct(
    "header_number" / Int32ul,
    "charge_config"
    / If(lambda this: this.header_number == 0x10002, charge_config_header),
    "phonon_config"
    / If(lambda this: this.header_number == 0x10001, phonon_config_header),
)

event_header = Struct(
    "event_header_word" / Int32ul,
    "event_size" / Int32ul,
    "event_identifier" / Computed(lambda this: (this.event_header_word >> 16) & 0xFFFF),
    # 0x0: Raw, 0x1: Processed, 0x2: Monte Carlo
    "event_class" / Computed(lambda this: (this.event_header_word >> 8) & 0xF),
    # 0x0: Per Trigger, 0x1: Occasional, 0x2: Begin File Series, 0x3: Begin File
    # 0x4: End File, 0x5: End File Series, 0x6: Per Trigger w/ Detectors that Cross Threshold
    "event_category" / Computed(lambda this: (this.event_header_word >> 12) & 0xF),
    # 0x0: Wimp Search, 0x1: 60Co Calibration, 0x2: 60Co Low Energy Calibration,
    # 0x3: Neutron Calibration, 0x4: Random Triggers, 0x5: Pulse Triggers
    # 0x6: Test, 0x7: Data Monitering Event, 0x8: 137Cs Calibration
    "event_type" / Computed(lambda this: (this.event_header_word & 0xFF)),
)

administrative_record = Struct(
    "admin_header" / Int32ul,
    "admin_len" / Int32ul,
    "series_number_1" / Int32ul,
    "series_number_2" / Int32ul,
    "event_number_in_series" / Int32ul,
    "seconds_from_epoch" / Int32ul,
    # Epoch defined as Jan 1st 1904 for SUF (MAC Artifact)
    # Epoch defined as Jan 1st 1970 for Soudan
    "time_from_last_event" / Int32ul,
    "live_time_from_last_event" / Int32ul,
)

trace_record = Struct(
    "trace_header" / Int32ul,
    "trace_len" / Int32ul,
    "trace_bookkeeping_header" / Int32ul,
    "bookkeeping_len" / Int32ul,
    "digitizer_base_address" / Int32ul,
    "digitizer_channel" / Int32ul,
    "detector_code" / Int32ul,
    "timebase_header" / Int32ul,
    "timebase_len" / Int32ul,
    "t0_in_ns" / Int32ul,
    "delta_t_ns" / Int32ul,
    "num_of_points" / Int32ul,
    "second_trace_header" / Int32ul,
    "num_samples" / Int32ul,
    # Should be a power of two (1024, 2048, etc)
)

data_sample = Struct(
    "data_selection" / Int32ul,
    "sample_a" / Computed(lambda this: (this.data_selection >> 16) & 0xFFFF),
    "sample_b" / Computed(lambda this: (this.data_selection & 0xFFFF)),
)


trace_data = Struct(
    "trace_rcrds" / trace_record,
    "sample_data" / Array(this.trace_rcrds.num_samples // 2, data_sample),
)

soudan_history_buffer = Struct(
    "history_buffer_header" / Int32ul,
    "history_buffer_len" / Int32ul,
    "num_time_nvt" / Int32ul,
    "time_nvt" / Array(this.num_time_nvt, Int32ul),
    "num_veto_mask_words" / Int32ul,
    "time_n_minus_veto_mask"
    / Array(this.num_time_nvt * this.num_veto_mask_words, Int32ul),
    "num_trigger_times" / Int32ul,
    "trigger_times" / Array(this.num_trigger_times, Int32ul),
    "num_trigger_mask_words" / Int32ul,
    "trig_times_minus_trig_mask"
    / Array(this.num_trigger_times * this.num_trigger_mask_words, Int32ul),
)

trigger_record = Struct(
    "trigger_header" / Int32ul,
    "trigger_len" / Int32ul,
    "trigger_time" / Int32ul,
    "individual_trigger_masks" / Array(6, Int32ul),
)

tlb_trigger_mask_record = Struct(
    "tlb_mask_header" / Int32ul, "tlb_len" / Int32ul, "tower_mask" / Array(6, Int32ul)
)

gps_data = Struct(
    "tlb_mask_header" / Int32ul,
    "length" / Int32ul,
    "gps_year_day" / If(this.length > 0, Int32ul),
    "gps_status_hour_minute_second" / If(this.length > 0, Int32ul),
    "gps_microsecs_from_gps_second" / If(this.length > 0, Int32ul),
)

detector_trigger_threshold_data = Struct(
    "threshold_header" / Int32ul,
    "len_to_next_header" / Int32ul,
    "minimum_voltage_level" / Int32ul,
    "maximum_voltage_level" / Int32ul,
    "dynamic_range" / Int32ul,
    "tower_number" / Int32ul,
    "detector_codes" / Array(6, Int32ul),
    "operations_codes" / Array(9, Int32ul),
    "adc_values" / Array(54, Int32ul),
)

detector_trigger_rates = Struct(
    "detector_trigger_header" / Int32ul,
    "len_to_next_header" / Int32ul,
    "clocking_interval" / Int32ul,
    "tower_number" / Int32ul,
    "detector_codes" / Array(6, Int32ul),
    "j_codes" / Array(5, Int32ul),
    "counter_values" / Array(30, Int32ul),
)

veto_trigger_rates = Struct(
    "veto_trigger_header" / Int32ul,
    "len_to_next_header" / Int32ul,
    "clocking_interval" / Int32ul,
    "num_entries" / Int32ul,
    "detector_code" / Array(this.num_entries, Int32ul),
    "counter_value_det_code" / Array(this.num_entries, Int32ul),
)


logical_records = Struct(
    "event_hdr" / Peek(Int32ul),  # Peek to check first
    "next_section"
    / Struct(
        "next_header" / Peek(Int32ul),  # Peek without consuming
        "section"
        / Switch(
            lambda this: (
                this.next_header
                if ((this.next_header >> 16) != 0xA980)
                else 0xA980  # Use 0xA980 as identifier for event_header
            ),
            {
                0xA980: event_header,
                0x00000002: administrative_record,
                0x00000011: trace_data,
                0x00000021: soudan_history_buffer,
                0x00000060: gps_data,
                0x00000080: trigger_record,
                0x00000081: tlb_trigger_mask_record,
                0x00000022: detector_trigger_rates,
                0x00000031: veto_trigger_rates,
            },
        ),
    ),
)

# %%
soudan = Struct(
    "file_hdr" / two_word_file_header,
    "detector_hdr" / detector_hdr,
    "hdrs" / Array(this._root.detector_hdr.repeat_value, header_list),
    "logical_rcrds" / GreedyRange(logical_records),
)

# %%
test_file_hdr = {
    "endian_indicator": 1,
    "data_format": {
        "daq_major": 1,
        "daq_minor": 2,
        "data_format_major": 3,
        "data_format_minor": 4,
    },
}
soudan.file_hdr.build(test_file_hdr)

# %%
test_detector_hdr = {
    "header_number": 0x10002,
    "config_record_len": 72 * 2,
}
built_detector_hdr = soudan.detector_hdr.build(test_detector_hdr)

# %%
repeat_value = soudan.detector_hdr.parse(built_detector_hdr).repeat_value
print(repeat_value)

# %%
test_hdrs = []
for i in range(repeat_value - 1):
    test_hdrs.append(
        {
            "header_number": 0x10002,
            "charge_config": {
                "charge_config_len": 72,
                "detector_code": 1,
                "tower_number": 1,
                "channel_post_amp": 1,
                "channel_bias": 1,
                "rtf_offset": 1,
                "delta_t": 1,
                "trigger_time": 1,
                "trace_len": 1,
            },
            "phonon_config": {},
        }
    )
test_hdrs.append(
    {
        "header_number": 0x10001,
        "phonon_config": {
            "phonon_config_len": 72,
            "detector_code": 1,
            "tower_number": 1,
            "post_amp_gain": 1,
            "qet_bias": 1,
            "squid_bias": 1,
            "squid_lockpoint": 1,
            "rtf_offset": 1,
            "variable_gain": 1,
            "delta_t": 1,
            "trigger_time": 1,
            "trace_len": 1,
        },
        "charge_config": {},
    }
)

# %%
soudan_test_hdrs = Struct(
    "hdrs" / Array(repeat_value, header_list),
)

# %%
built_hdrs = soudan_test_hdrs.build({"hdrs": test_hdrs})

# %%
parsed_hdrs = soudan_test_hdrs.parse(built_hdrs)
print(parsed_hdrs)

# %%
test_logical_records = [
    {
        # Event Header Record
        "event_hdr": 0xA9800000,
        "next_section": {
            "next_header": 0xA9800000,
            "section": {
                "event_header_word": 0xA9800000,
                "event_size": 100,
            },
        },
    },
    {
        # Admin Header Record
        "event_hdr": 0x00000002,
        "next_section": {
            # Next Section Header
            "next_header": 0x00000002,
            "section": {
                # Admin Section
                "admin_header": 0x00000002,
                "admin_len": 50,
                "series_number_1": 1,
                "series_number_2": 2,
                "event_number_in_series": 3,
                "seconds_from_epoch": 1000,
                "time_from_last_event": 10,
                "live_time_from_last_event": 5,
            },
        },
    },
    {
        # Trace Header Record
        "event_hdr": 0x00000011,
        "next_section": {
            # Next Section Header
            "next_header": 0x00000011,
            "section": {
                "trace_rcrds": {
                    # Trace Section
                    "trace_header": 0x00000011,
                    "trace_len": 200,
                    "trace_bookkeeping_header": 0x00000011,
                    "bookkeeping_len": 20,
                    "digitizer_base_address": 0x1000,
                    "digitizer_channel": 1,
                    "detector_code": 1,
                    "timebase_header": 0x00000011,
                    "timebase_len": 10,
                    "t0_in_ns": 100,
                    "delta_t_ns": 10,
                    "num_of_points": 1000,
                    "second_trace_header": 0x00000011,
                    "num_samples": 4,  # This should agree with the number of elements in sample_data
                },
                "sample_data": [
                    {"data_selection": 0x00010001, "sample_a": 1, "sample_b": 1},
                    {"data_selection": 0x00020002, "sample_a": 2, "sample_b": 2},
                ],
            },
        },
    },
    {
        # History Buffer Header Record
        "event_hdr": 0x00000021,
        "next_section": {
            # Next Section Header
            "next_header": 0x00000021,
            "section": {
                # History Buffer Section
                "history_buffer_header": 0x00000021,
                "history_buffer_len": 100,
                "num_time_nvt": 2,
                "time_nvt": [100, 200],
                "num_veto_mask_words": 2,
                "time_n_minus_veto_mask": [300, 400, 500, 600],
                "num_trigger_times": 2,
                "trigger_times": [500, 600],
                "num_trigger_mask_words": 2,
                "trig_times_minus_trig_mask": [700, 800, 900, 1000],
            },
        },
    },
    {
        # TLB Mask Header Record
        "event_hdr": 0x00000060,
        "next_section": {
            # Next Section Header
            "next_header": 0x00000060,
            "section": {
                # TLB Mask Section
                "tlb_mask_header": 0x00000060,
                "length": 10,
                "gps_year_day": 2021365,
                "gps_status_hour_minute_second": 123456,
                "gps_microsecs_from_gps_second": 789,
            },
        },
    },
    {
        # Trigger Header Record
        "event_hdr": 0x00000080,
        "next_section": {
            # Next Section Header
            "next_header": 0x00000080,
            "section": {
                # Trigger Section
                "trigger_header": 0x00000080,
                "trigger_len": 50,
                "trigger_time": 1000,
                "individual_trigger_masks": [1, 2, 3, 4, 5, 6],
            },
        },
    },
    {
        # TLB Mask Header Record
        "event_hdr": 0x00000081,
        "next_section": {
            # Next Section Header
            "next_header": 0x00000081,
            "section": {
                # TLB Mask Section
                "tlb_mask_header": 0x00000081,
                "tlb_len": 50,
                "tower_mask": [1, 2, 3, 4, 5, 6],
            },
        },
    },
    {
        # Detector Trigger Header Record
        "event_hdr": 0x00000022,
        "next_section": {
            # Next Section Header
            "next_header": 0x00000022,
            "section": {
                # Detector Trigger Section
                "detector_trigger_header": 0x00000022,
                "len_to_next_header": 50,
                "clocking_interval": 100,
                "tower_number": 1,
                "detector_codes": [1, 2, 3, 4, 5, 6],
                "j_codes": [1, 2, 3, 4, 5],
                "counter_values": [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8,
                    9,
                    10,
                    11,
                    12,
                    13,
                    14,
                    15,
                    16,
                    17,
                    18,
                    19,
                    20,
                    21,
                    22,
                    23,
                    24,
                    25,
                    26,
                    27,
                    28,
                    29,
                    30,
                ],
            },
        },
    },
    {
        # Veto Trigger Header Record
        "event_hdr": 0x00000031,
        "next_section": {
            # Next Section Header
            "next_header": 0x00000031,
            "section": {
                # Veto Trigger Section
                "veto_trigger_header": 0x00000031,
                "len_to_next_header": 50,
                "clocking_interval": 100,
                "num_entries": 2,
                "detector_code": [1, 2],
                "counter_value_det_code": [3, 4],
            },
        },
    },
]

# %%
# Build the logical records
built_logical_records = soudan.logical_rcrds.build(test_logical_records)

# Parse the built logical records
parsed_logical_records = soudan.logical_rcrds.parse(built_logical_records)

print(parsed_logical_records)

# %%
complete_test_file = {
    "file_hdr": test_file_hdr,
    "detector_hdr": test_detector_hdr,
    "hdrs": test_hdrs,
    "logical_rcrds": test_logical_records,}

# %%
# Build the complete test file
built_complete_test_file = soudan.build(complete_test_file)

# Write the built file to a binary file
with open('minimal_sample.soudan', 'wb') as f:
    f.write(built_complete_test_file)

# %%
import os
os.system('ls -lah minimal_sample.soudan')

# %%
