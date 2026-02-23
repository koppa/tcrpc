import pytest
import pyads
import ctypes
from tcrpc.runner import map_ads_type
from tcrpc.types import REAL, UINT


def test_map_standard_ads_types():
    assert map_ads_type(int) == pyads.PLCTYPE_DINT
    assert map_ads_type(float) == pyads.PLCTYPE_LREAL
    assert map_ads_type(bool) == pyads.PLCTYPE_BOOL
    assert map_ads_type(str) == pyads.PLCTYPE_STRING


def test_map_custom_ads_types():
    assert map_ads_type(REAL) == pyads.PLCTYPE_REAL
    assert map_ads_type(UINT) == pyads.PLCTYPE_UINT


def test_map_ctypes_array():
    arr_type = pyads.PLCTYPE_INT * 5
    mapped = map_ads_type(arr_type)
    assert issubclass(mapped, ctypes.Array)
    assert mapped._length_ == 5
    assert mapped._type_ == pyads.PLCTYPE_INT


def test_unsupported_ads_type():
    class UnknownType:
        pass

    with pytest.raises(ValueError, match="Unsupported Python type"):
        map_ads_type(UnknownType)
