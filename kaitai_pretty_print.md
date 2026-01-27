# Soudan file dump

## File header
| field | value |
| --- | --- |
| endian_indicator | 0x00000001 [1, 0, 0, 0] |
| daq_major | 1 |
| daq_minor | 2 |
| data_format_major | 3 |
| data_format_minor | 4 |

## Detector header
| field | value |
| --- | --- |
| header_num | 65538 |
| config_record_len | 144 |
| repeat_value | 3 |

## Detector configs (3)

### Header 0
| field | value |
| --- | --- |
| header_num | 65538 |
| charge_config_len | 72 |
| detector_code | 10001001 |
| tower_num | 1 |
| channel_post_amp | 1 |
| channel_bias | 1 |
| rtf_offset | 1 |
| delta_t | 1 |
| trigger_time | 1 |
| trace_len | 2 |

### Header 1
| field | value |
| --- | --- |
| header_num | 65538 |
| charge_config_len | 72 |
| detector_code | 10001001 |
| tower_num | 1 |
| channel_post_amp | 1 |
| channel_bias | 1 |
| rtf_offset | 1 |
| delta_t | 1 |
| trigger_time | 1 |
| trace_len | 2 |

### Header 2
| field | value |
| --- | --- |
| header_num | 65537 |
| phonon_config_len | 72 |
| detector_code | 10001002 |
| tower_num | 1 |
| post_amp_gain | 1 |
| qet_bias | 1 |
| squid_bias | 1 |
| squid_lockpoint | 1 |
| rtf_offset | 1 |
| variable_gain | 1 |
| delta_t | 1 |
| trigger_time | 1 |
| trace_len | 2 |

## Logical records (9)

### Record 0: event_header (0xa9800004)
| field | value |
| --- | --- |
| event_size | 100 |
| event_identifier | 43392 |
| event_class | 0 |
| event_category | 0 |
| event_type | 4 |

### Record 1: administrative_record (0x00000002)
| field | value |
| --- | --- |
| admin_len | 50 |
| series_num_1 | 1 |
| series_num_2 | 2 |
| event_num_in_series | 1 |
| seconds_from_epoch | 1700000000 |
| time_from_last_event | 1 |
| live_time_from_last_event | 1 |

### Record 2: trace_data (0x00000011)
| field | value |
| --- | --- |
| trace_len | 200 |
| trace_bookkeeping_header | 17 |
| bookkeeping_len | 20 |
| digitizer_base_address | 4096 |
| digitizer_channel | 1 |
| detector_code | 10001002 |
| timebase_header | 17 |
| timebase_len | 10 |
| t0_in_ns | 100 |
| delta_t_ns | 10 |
| num_of_points | 1000 |
| second_trace_header | 17 |
| num_samples | 2 |
| sample_data | [65538] |

### Record 3: soudan_history_buffer (0x00000021)
| field | value |
| --- | --- |
| history_buffer_len | 40 |
| num_time_nvt | 1 |
| time_nvt | [100] |
| num_veto_mask_words | 1 |
| time_n_minus_veto_mask | [300] |
| num_trigger_times | 1 |
| times | [500] |
| num_trigger_mask_words_per_time | 1 |
| times_minus_trigger_mask | [700] |

### Record 4: gps_data (0x00000060)
| field | value |
| --- | --- |
| len | 1 |
| gps_year_day | 2024001 |
| gps_status_hour_minute_second | 10101 |
| gps_microsecs_from_gps_second | 1 |

### Record 5: trigger_record (0x00000080)
| field | value |
| --- | --- |
| trigger_len | 50 |
| trigger_time | 1000 |
| individual_trigger_mask | [1, 2, 3, 4, 5, 6] |

### Record 6: tlb_trigger_mask_record (0x00000081)
| field | value |
| --- | --- |
| tlb_len | 50 |
| tower_mask | [1, 2, 3, 4, 5, 6] |

### Record 7: detector_trigger_rates (0x00000022)
| field | value |
| --- | --- |
| len_to_next_header | 50 |
| clocking_interval | 100 |
| tower_num | 1 |
| detector_codes | [10001001, 10001002, 0, 0, 0, 0] |
| j_codes | [1, 2, 3, 4, 5] |
| counter_values | [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30] |

### Record 8: veto_trigger_rates (0x00000031)
| field | value |
| --- | --- |
| len_to_next_header | 50 |
| clocking_interval | 100 |
| num_entries | 2 |
| detector_code | [10001001, 10001002] |
| counter_value_det_code | [3, 4] |
