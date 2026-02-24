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


def test_generate_fb():
    from tcrpc.generator import generate_fb

    params = {"a": int, "b": float}
    ret_type = bool

    output = generate_fb("my_func", params, ret_type, "python run.py")
    assert "RPC_my_func" in output
    assert "_a : DINT;" in output
    assert "_b : LREAL;" in output
    assert "PROPERTY Result : BOOL" in output


def test_find_file(tmp_path):
    from tcrpc.generator import find_file

    # Create dummy structure
    (tmp_path / "POUs").mkdir()
    target_file = tmp_path / "POUs" / "RPC_my_func.TcPOU"
    target_file.touch()

    found = find_file(tmp_path, "RPC_my_func.TcPOU")
    assert found == target_file

    found_none = find_file(tmp_path, "DOES_NOT_EXIST")
    assert found_none is None


def test_main_cli_generation(tmp_path, monkeypatch):
    from tcrpc.generator import main
    import sys
    from pathlib import Path
    from tcrpc.decorator import _REGISTRY

    _REGISTRY.clear()

    script_path = Path(__file__).parent / "dummy_script.py"
    output_dir = tmp_path / "generated"

    monkeypatch.setattr(
        sys, "argv", ["tcrpc-gen", str(script_path), "-o", str(output_dir)]
    )

    main()

    assert output_dir.exists()
    assert (output_dir / "RPC_dummy_func.TcPOU").exists()


def test_main_cli_plc_update(tmp_path, monkeypatch):
    from tcrpc.generator import main
    import sys
    from pathlib import Path
    from tcrpc.decorator import _REGISTRY

    _REGISTRY.clear()

    script_path = Path(__file__).parent / "dummy_script.py"
    plc_dir = tmp_path / "PLC"
    plc_dir.mkdir()
    (plc_dir / "POUs").mkdir()
    target_file = plc_dir / "POUs" / "RPC_dummy_func.TcPOU"
    target_file.touch()

    monkeypatch.setattr(
        sys, "argv", ["tcrpc-gen", str(script_path), "--plc-project", str(plc_dir)]
    )

    main()

    assert target_file.read_text().startswith(
        "<?xml"
    )  # Verify it actually wrote the jinja template output
