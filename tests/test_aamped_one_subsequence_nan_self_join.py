import numpy as np
import numpy.testing as npt
import pandas as pd
from stumpy import core, aamped
from dask.distributed import Client, LocalCluster
import pytest
import warnings
import naive


@pytest.fixture(scope="module")
def dask_cluster():
    cluster = LocalCluster(n_workers=2, threads_per_worker=2)
    yield cluster
    cluster.close()


test_data = [
    (
        np.array([9, 8100, -60, 7], dtype=np.float64),
        np.array([584, -11, 23, 79, 1001, 0, -19], dtype=np.float64),
    ),
    (
        np.random.uniform(-1000, 1000, [8]).astype(np.float64),
        np.random.uniform(-1000, 1000, [64]).astype(np.float64),
    ),
]

substitution_locations = [0, -1, slice(1, 3), [0, 3]]


@pytest.mark.filterwarnings("ignore:numpy.dtype size changed")
@pytest.mark.filterwarnings("ignore:numpy.ufunc size changed")
@pytest.mark.filterwarnings("ignore:numpy.ndarray size changed")
@pytest.mark.filterwarnings("ignore:\\s+Port 8787 is already in use:UserWarning")
@pytest.mark.parametrize("T_A, T_B", test_data)
@pytest.mark.parametrize("substitution_location_B", substitution_locations)
def test_aamped_one_subsequence_nan_self_join(
    T_A, T_B, substitution_location_B, dask_cluster
):
    with Client(dask_cluster) as dask_client:
        m = 3

        T_B_sub = T_B.copy()
        T_B_sub[substitution_location_B] = np.nan

        zone = int(np.ceil(m / 4))
        left = naive.aamp(T_B_sub, m)
        right = aamped(dask_client, T_B_sub, m, ignore_trivial=True)
        naive.replace_inf(left)
        naive.replace_inf(right)
        npt.assert_almost_equal(left, right)
