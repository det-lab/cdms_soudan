import h5py
import numpy as np

from scdms_soudan_spec import EXPECTED_HDF5


def _normalize_value(value):
    if isinstance(value, np.ndarray):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def _read_dataset(dataset):
    value = dataset[()]
    return _normalize_value(value)


def test_minimal_hdf5_values():
    with h5py.File("minimal_sample.hdf5", "r") as h5f:
        for path, spec in EXPECTED_HDF5.items():
            assert path in h5f, f"Missing dataset: {path}"
            dataset = h5f[path]

            dtype_kind = spec.get("dtype_kind")
            if dtype_kind is not None:
                assert (
                    dataset.dtype.kind == dtype_kind
                ), f"Unexpected dtype for {path}: {dataset.dtype}"

            if "shape" in spec:
                expected_shape = tuple(spec["shape"])
                assert dataset.shape == expected_shape, (
                    f"Unexpected shape for {path}: "
                    f"{dataset.shape} != {expected_shape}"
                )
                value = _read_dataset(dataset)
                np.testing.assert_array_equal(value, np.array(spec["values"]))
            else:
                value = _read_dataset(dataset)
                expected_value = spec["value"]
                if isinstance(value, np.ndarray):
                    np.testing.assert_array_equal(value, np.array(expected_value))
                else:
                    assert value == expected_value, (
                        f"Unexpected value for {path}: {value} != {expected_value}"
                    )

