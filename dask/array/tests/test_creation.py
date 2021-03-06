import numpy as np
from numpy.testing import assert_array_almost_equal
import pytest

import dask.array as da


def eq(a, b):
    """a is a dask array, b is a numpy array. Checks dtype, shape and value. No
    `assert` needed.
    """
    a = np.array(a)
    assert a.shape == b.shape
    assert a.dtype == b.dtype
    assert_array_almost_equal(a, b)


def test_linspace():
    darr = da.linspace(6, 49, blocksize=5)
    nparr = np.linspace(6, 49)
    eq(darr, nparr)

    darr = da.linspace(1.4, 4.9, blocksize=5, num=13)
    nparr = np.linspace(1.4, 4.9, num=13)
    eq(darr, nparr)

    darr = da.linspace(6, 49, blocksize=5, dtype=float)
    nparr = np.linspace(6, 49, dtype=float)
    eq(darr, nparr)

    darr = da.linspace(1.4, 4.9, blocksize=5, num=13, dtype=int)
    nparr = np.linspace(1.4, 4.9, num=13, dtype=int)
    eq(darr, nparr)


def test_arange():
    darr = da.arange(77, blocksize=13)
    nparr = np.arange(77)
    eq(darr, nparr)

    darr = da.arange(2, 13, blocksize=5)
    nparr = np.arange(2, 13)
    eq(darr, nparr)

    darr = da.arange(4, 21, 9, blocksize=13)
    nparr = np.arange(4, 21, 9)
    eq(darr, nparr)

    # negative steps
    darr = da.arange(53, 5, -3, blocksize=5)
    nparr = np.arange(53, 5, -3)
    eq(darr, nparr)

    darr = da.arange(77, blocksize=13, dtype=float)
    nparr = np.arange(77, dtype=float)
    eq(darr, nparr)

    darr = da.arange(2, 13, blocksize=5, dtype=int)
    nparr = np.arange(2, 13, dtype=int)
    eq(darr, nparr)


def test_arange_working_float_step():
    """Sometimes floating point step arguments work, but this could be platform
    dependent.
    """
    darr = da.arange(3.3, -9.1, -.25, blocksize=3)
    nparr = np.arange(3.3, -9.1, -.25)
    eq(darr, nparr)


@pytest.mark.xfail(reason="Casting floats to ints is not supported since edge"
                          "behavior is not specified or guaranteed by NumPy.")
def test_arange_cast_float_int_step():
    darr = da.arange(3.3, -9.1, -.25, blocksize=3, dtype='i8')
    nparr = np.arange(3.3, -9.1, -.25, dtype='i8')
    eq(darr, nparr)


@pytest.mark.xfail(reason="arange with a floating point step value can fail"
                          "due to numerical instability.")
def test_arange_float_step():
    darr = da.arange(2., 13., .3, blocksize=4)
    nparr = np.arange(2., 13., .3)
    eq(darr, nparr)

    darr = da.arange(7.7, 1.5, -.8, blocksize=3)
    nparr = np.arange(7.7, 1.5, -.8)
    eq(darr, nparr)
