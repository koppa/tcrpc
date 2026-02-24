import ctypes

import pyads
import pytest

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


def test_load_module(tmp_path):
    from tcrpc.runner import load_module
    import sys

    script_path = tmp_path / "dummy_runner_script.py"
    script_path.write_text("x = 42\n")

    load_module(script_path)
    assert sys.modules["dummy_runner_script"].x == 42


def test_main_success(tmp_path, monkeypatch):
    from tcrpc.runner import main
    import sys
    from unittest.mock import MagicMock
    from tcrpc.decorator import _REGISTRY

    _REGISTRY.clear()

    # Create the script
    script_path = tmp_path / "dummy_rpc_script.py"
    script_path.write_text(
        "from tcrpc.decorator import tc_callable\n"
        "@tc_callable\n"
        "def my_func(a: int) -> int:\n"
        "    return a * 2\n"
    )

    # Set arguments
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tcrpc-run",
            str(script_path),
            "--run",
            "my_func",
            "--instance-path",
            "MAIN.fbRpc",
        ],
    )

    # Mock PyADS connection
    mock_conn_class = MagicMock()
    mock_conn = mock_conn_class.return_value
    mock_conn.read_by_name.side_effect = lambda name, typ: 10 if "_a" in name else 0
    monkeypatch.setattr("pyads.Connection", mock_conn_class)

    # Run
    main()

    # Assert
    mock_conn.write_by_name.assert_any_call(
        "MAIN.fbRpc._result", 20, pyads.PLCTYPE_DINT
    )
    mock_conn.write_by_name.assert_any_call(
        "MAIN.fbRpc._bDone", True, pyads.PLCTYPE_BOOL
    )
