import dask
import dask.array as da
from dask.array import Array
from dask.array.slicing import slice_array, _slice_1d, take
from operator import getitem
import numpy as np
from toolz import merge


def eq(a, b):
    if isinstance(a, da.Array):
        a = a.compute(get=dask.get)
    if isinstance(b, da.Array):
        b = b.compute(get=dask.get)

    c = a == b
    if isinstance(c, np.ndarray):
        c = c.all()
    return c


def test_slice_1d():
    expected = {0: slice(10, 25, 1), 1: slice(None, None, None), 2: slice(0, 1, 1)}
    result = _slice_1d(100, [25]*4, slice(10, 51, None))
    assert expected == result

    #x[100:12:-3]
    expected = {0: slice(-2, -8, -3),
                1: slice(-1, -21, -3),
                2: slice(-3, -21, -3),
                3: slice(-2, -21, -3),
                4: slice(-1, -21, -3)}
    result = _slice_1d(100, [20]*5, slice(100, 12, -3))
    assert expected == result

    #x[102::-3]
    expected = {0: slice(-2, -21, -3),
                1: slice(-1, -21, -3),
                2: slice(-3, -21, -3),
                3: slice(-2, -21, -3),
                4: slice(-1, -21, -3)}
    result = _slice_1d(100, [20]*5, slice(102, None, -3))
    assert expected == result

    #x[::-4]
    expected = {0: slice(-1, -21, -4),
                1: slice(-1, -21, -4),
                2: slice(-1, -21, -4),
                3: slice(-1, -21, -4),
                4: slice(-1, -21, -4)}
    result = _slice_1d(100, [20]*5, slice(None, None, -4))
    assert expected == result

    #x[::-7]
    expected = {0: slice(-5, -21, -7),
                1: slice(-4, -21, -7),
                2: slice(-3, -21, -7),
                3: slice(-2, -21, -7),
                4: slice(-1, -21, -7)}
    result = _slice_1d(100, [20]*5, slice(None, None, -7))
    assert expected == result

    #x=range(115)
    #x[::-7]
    expected = {0: slice(-7, -24, -7),
                1: slice(-2, -24, -7),
                2: slice(-4, -24, -7),
                3: slice(-6, -24, -7),
                4: slice(-1, -24, -7)}
    result = _slice_1d(115, [23]*5, slice(None, None, -7))
    assert expected == result

    #x[79::-3]
    expected = {0: slice(-1, -21, -3),
                1: slice(-3, -21, -3),
                2: slice(-2, -21, -3),
                3: slice(-1, -21, -3)}
    result = _slice_1d(100, [20]*5, slice(79, None, -3))
    assert expected == result

    #x[-1:-8:-1]
    expected = {4: slice(-1, -8, -1)}
    result = _slice_1d(100, [20, 20, 20, 20, 20], slice(-1, 92, -1))
    assert expected == result

    #x[20:0:-1]
    expected = {0: slice(-1, -20, -1),
                1: slice(-20, -21, -1)}
    result = _slice_1d(100, [20, 20, 20, 20, 20], slice(20, 0, -1))
    assert expected == result

    #x[:0]
    expected = {}
    result = _slice_1d(100, [20, 20, 20, 20, 20], slice(0))
    assert expected == result

    #x=range(99)
    expected = {0: slice(-3, -21, -3),
                1: slice(-2, -21, -3),
                2: slice(-1, -21, -3),
                3: slice(-2, -20, -3),
                4: slice(-1, -21, -3)}
    #This array has non-uniformly sized blocks
    result = _slice_1d(99, [20, 20, 20, 19, 20], slice(100, None, -3))
    assert expected == result

    #x=range(104)
    #x[::-3]
    expected = {0: slice(-1, -21, -3),
                1: slice(-3, -24, -3),
                2: slice(-3, -28, -3),
                3: slice(-1, -14, -3),
                4: slice(-1, -22, -3)}
    #This array has non-uniformly sized blocks
    result = _slice_1d(104, [20, 23, 27, 13, 21], slice(None, None, -3))
    assert expected == result

    #x=range(104)
    #x[:27:-3]
    expected = {1: slice(-3, -16, -3),
                2: slice(-3, -28, -3),
                3: slice(-1, -14, -3),
                4: slice(-1, -22, -3)}
    #This array has non-uniformly sized blocks
    result = _slice_1d(104, [20, 23, 27, 13, 21], slice(None, 27, -3))
    assert expected == result

    #x=range(104)
    #x[100:27:-3]
    expected = {1: slice(-3, -16, -3),
                2: slice(-3, -28, -3),
                3: slice(-1, -14, -3),
                4: slice(-4, -22, -3)}
    #This array has non-uniformly sized blocks
    result = _slice_1d(104, [20, 23, 27, 13, 21], slice(100, 27, -3))
    assert expected == result


def test_slice_singleton_value_on_boundary():
    assert _slice_1d(15, [5, 5, 5], 10) == {2: 0}
    assert _slice_1d(30, (5, 5, 5, 5, 5, 5), 10) == {2: 0}


def test_slice_array_1d():
    #x[24::2]
    expected = {('y', 0): (getitem, ('x', 0), (slice(24, 25, 2),)),
                ('y', 1): (getitem, ('x', 1), (slice(1, 25, 2),)),
                ('y', 2): (getitem, ('x', 2), (slice(0, 25, 2),)),
                ('y', 3): (getitem, ('x', 3), (slice(1, 25, 2),))}
    result, blockdims = slice_array('y', 'x', [[25]*4], [slice(24,None,2)])

    assert expected == result

    #x[26::2]
    expected = {('y', 0): (getitem, ('x', 1), (slice(1, 25, 2),)),
                ('y', 1): (getitem, ('x', 2), (slice(0, 25, 2),)),
                ('y', 2): (getitem, ('x', 3), (slice(1, 25, 2),))}

    result, blockdims = slice_array('y', 'x', [[25]*4], [slice(26,None,2)])
    assert expected == result

    #x[24::2]
    expected = {('y', 0): (getitem, ('x', 0), (slice(24, 25, 2),)),
                ('y', 1): (getitem, ('x', 1), (slice(1, 25, 2),)),
                ('y', 2): (getitem, ('x', 2), (slice(0, 25, 2),)),
                ('y', 3): (getitem, ('x', 3), (slice(1, 25, 2),))}
    result, blockdims = slice_array('y', 'x', [(25,)*4], (slice(24,None,2),))

    assert expected == result

    #x[26::2]
    expected = {('y', 0): (getitem, ('x', 1), (slice(1, 25, 2),)),
                ('y', 1): (getitem, ('x', 2), (slice(0, 25, 2),)),
                ('y', 2): (getitem, ('x', 3), (slice(1, 25, 2),))}

    result, blockdims = slice_array('y', 'x', [(25,)*4], (slice(26,None,2),))
    assert expected == result


def test_slice_array_2d():
    #2d slices: x[13::2,10::1]
    expected = {('y', 0, 0): (getitem,
                               ('x', 0, 0),
                               (slice(13, 20, 2), slice(10, 20, 1))),
                 ('y', 0, 1): (getitem,
                               ('x', 0, 1),
                               (slice(13, 20, 2), slice(None, None, None))),
                 ('y', 0, 2): (getitem,
                               ('x', 0, 2),
                               (slice(13, 20, 2), slice(None, None, None)))}

    result, blockdims = slice_array('y', 'x', [[20], [20, 20, 5]],
                        [slice(13,None,2), slice(10, None, 1)])

    assert expected == result

    #2d slices with one dimension: x[5,10::1]
    expected = {('y', 0): (getitem,
                               ('x', 0, 0),
                               (5, slice(10, 20, 1))),
                 ('y', 1): (getitem,
                               ('x', 0, 1),
                               (5, slice(None, None, None))),
                 ('y', 2): (getitem,
                               ('x', 0, 2),
                               (5, slice(None, None, None)))}

    result, blockdims = slice_array('y', 'x', ([20], [20, 20, 5]),
                        [5, slice(10, None, 1)])

    assert expected == result


def test_slice_optimizations():
    #bar[:]
    expected = {'foo':'bar'}
    result, blockdims = slice_array('foo', 'bar', [[100]], (slice(None,None,None),))
    assert expected == result

    #bar[:,:,:]
    expected = {'foo':'bar'}
    result, blockdims = slice_array('foo', 'bar', [(100,1000,10000)],
                        (slice(None,None,None),slice(None,None,None),
                         slice(None,None,None)))
    assert expected == result


def test_slicing_with_singleton_indices():
    result, blockdims = slice_array('y', 'x', ([5, 5], [5, 5]),
                                    (slice(0, 5), 8))

    expected = {('y', 0): (getitem, ('x', 0, 1), (slice(None, None, None), 3))}

    assert expected == result


def test_slicing_with_newaxis():
    result, blockdims = slice_array('y', 'x', ([5, 5], [5, 5]),
                            (slice(0, 3), None, slice(None, None, None)))

    expected = {
        ('y', 0, 0, 0): (getitem,
                          ('x', 0, 0),
                          (slice(0, 3, 1), None, slice(None, None, None))),
        ('y', 0, 0, 1): (getitem,
                          ('x', 0, 1),
                          (slice(0, 3, 1), None, slice(None, None, None)))
      }

    assert expected == result
    assert blockdims == ((3,), (1,), (5, 5))


def test_take():
    blockdims, dsk = take('y', 'x', [(20, 20, 20, 20)], [5, 1, 47, 3], axis=0)
    expected = {('y', 0):
            (getitem,
              (np.concatenate, (list,
                [(getitem, ('x', 0), ([1, 3, 5],)),
                 (getitem, ('x', 2), ([7],))]),
               0),
             ([2, 0, 3, 1],))}
    assert dsk == expected
    assert blockdims == ((4,),)

    blockdims, dsk = take('y', 'x', [(20, 20, 20, 20), (20, 20)], [5, 1, 47, 3], axis=0)
    expected = dict((('y', 0, j),
            (getitem,
              (np.concatenate, (list,
                [(getitem, ('x', 0, j), ([1, 3, 5], slice(None, None, None))),
                 (getitem, ('x', 2, j), ([7], slice(None, None, None)))]),
                0),
              ([2, 0, 3, 1], slice(None, None, None))))
            for j in range(2))
    assert dsk == expected
    assert blockdims == ((4,), (20, 20))


    blockdims, dsk = take('y', 'x', [(20, 20, 20, 20), (20, 20)], [5, 1, 37, 3], axis=1)
    expected = dict((('y', i, 0),
            (getitem,
              (np.concatenate, (list,
                [(getitem, ('x', i, 0), (slice(None, None, None), [1, 3, 5])),
                 (getitem, ('x', i, 1), (slice(None, None, None), [17]))]),
                1),
             (slice(None, None, None), [2, 0, 3, 1])))
           for i in range(4))
    assert dsk == expected
    assert blockdims == ((20, 20, 20, 20), (4,))


def test_take_sorted():
    blockdims, dsk = take('y', 'x', [(20, 20, 20, 20)], [1, 3, 5, 47], axis=0)
    expected = {('y', 0): (getitem, ('x', 0), ([1, 3, 5],)),
                ('y', 1): (getitem, ('x', 2), ([7],))}
    assert dsk == expected
    assert blockdims == ((3, 1),)

    blockdims, dsk = take('y', 'x', [(20, 20, 20, 20), (20, 20)], [1, 3, 5, 37], axis=1)
    expected = merge(
            dict((('y', i, 0),
                  (getitem, ('x', i, 0), (slice(None, None, None), [1, 3, 5])))
                  for i in range(4)),
            dict((('y', i, 1),
                  (getitem, ('x', i, 1), (slice(None, None, None), [17])))
                  for i in range(4)))
    assert dsk == expected
    assert blockdims == ((20, 20, 20, 20), (3, 1))


def test_slice_lists():
    y, blockdims = slice_array('y', 'x', ((3, 3, 3, 1), (3, 3, 3, 1)),
                                ([2, 1, 9], slice(None, None, None)))
    assert y == \
        dict((('y', 0, i), (getitem,
                       (np.concatenate,
                        (list,
                         [(getitem,
                           ('x', 0, i),
                           ([1, 2], slice(None, None, None))),
                          (getitem,
                           ('x', 3, i),
                           ([0], slice(None, None, None))),
                           ]),
                        0),
                       ([1, 0, 2], slice(None, None, None))))
                for i in range(4))

    assert blockdims == ((3,), (3, 3, 3, 1))


def test_slicing_blockdims():
    result, blockdims = slice_array('y', 'x', ([5, 5], [5, 5]),
                                    (1, [2, 0, 3]))
    assert blockdims == ((3,),)

    result, blockdims = slice_array('y', 'x', ([5, 5], [5, 5]),
                                    (slice(0, 7), [2, 0, 3]))
    assert blockdims == ((5, 2), (3,))

    result, blockdims = slice_array('y', 'x', ([5, 5], [5, 5]),
                                    (slice(0, 7), 1))
    assert blockdims == ((5, 2),)


def test_slicing_with_numpy_arrays():
    a, bd1 = slice_array('y', 'x', ((3, 3, 3, 1), (3, 3, 3, 1)),
                         ([1, 2, 9], slice(None, None, None)))
    b, bd2 = slice_array('y', 'x', ((3, 3, 3, 1), (3, 3, 3, 1)),
                         (np.array([1, 2, 9]), slice(None, None, None)))

    assert bd1 == bd2
    assert a == b

    i = [False, True, True, False, False,
         False, False, False, False, True, False]
    c, bd3 = slice_array('y', 'x', ((3, 3, 3, 1), (3, 3, 3, 1)),
                         (i, slice(None, None, None)))
    assert bd1 == bd3
    assert a == c


def test_slicing_and_blockdims():
    o = da.ones((24, 16), blockdims=((4, 8, 8, 4), (2, 6, 6, 2)))
    t = o[4:-4, 2:-2]
    assert t.blockdims == ((8, 8), (6, 6))


def test_slice_stop_0():
    # from gh-125
    a = da.ones(10, blockshape=(10,))[:0].compute()
    b = np.ones(10)[:0]
    assert eq(a, b)


def test_slice_list_then_None():
    x = da.zeros(shape=(5, 5), blockshape=(3, 3))
    y = x[[2, 1]][None]

    assert eq(y, np.zeros((1, 2, 5)))
