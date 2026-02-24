import ctypes

import pyads
import pytest

from tcrpc.generator import map_type
from tcrpc.types import REAL, UINT


def test_map_standard_types():
    assert map_type(int) == "DINT"
    assert map_type(float) == "LREAL"
    assert map_type(bool) == "BOOL"
    assert map_type(str) == "STRING(255)"


def test_map_custom_st_types():
    assert map_type(REAL) == "REAL"
    assert map_type(UINT) == "UINT"


def test_map_ctypes_array():
    # pyads uses ctypes arrays
    arr_type = pyads.PLCTYPE_INT * 5
    assert map_type(arr_type) == "ARRAY [0..4] OF INT"

    arr_type_2 = ctypes.c_double * 10
    assert map_type(arr_type_2) == "ARRAY [0..9] OF LREAL"


def test_unsupported_type():
    class UnknownType:
        pass

    with pytest.raises(ValueError, match="Unsupported Python type"):
        map_type(UnknownType)
