import argparse
import importlib.util
import os
import sys
from pathlib import Path

import pyads

from tcrpc.decorator import get_registry
from tcrpc.types import TYPE_MAPPING


def map_ads_type(python_type):
    """Retrieve the corresponding PyADS PLC type for a given Python type."""
    if hasattr(python_type, "_length_") and hasattr(python_type, "_type_"):
        return python_type

    if (
        hasattr(python_type, "__module__")
        and hasattr(python_type, "__name__")
        and python_type.__module__ == "_ctypes"
    ):
        return python_type

    try:
        return TYPE_MAPPING[python_type][1]
    except KeyError:
        pass

    raise ValueError(f"Unsupported Python type for PyADS mapping: {python_type}")


def load_module(file_path: Path):
    """Dynamically load the user's python file."""
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    module_name = file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        print(f"Error: Could not load module from {file_path}", file=sys.stderr)
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    # Add to sys.path so it can find its own local imports
    sys.path.insert(0, str(file_path.parent))

    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error executing module {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Run a @tc_callable Python function, reading/writing via PyADS."
    )
    parser.add_argument(
        "python_file", help="The Python file containing the @tc_callable function."
    )
    parser.add_argument("--run", required=True, help="The name of the function to run.")
    parser.add_argument(
        "--instance-path", required=True, help="The ADS path of the FB instance."
    )
    parser.add_argument(
        "--ams-net-id",
        default=None,
        help="The AMS Net ID of the target PLC (default: local).",
    )
    parser.add_argument(
        "--ads-port",
        type=int,
        default=851,
        help="The ADS port of the target PLC (default: 851).",
    )

    args = parser.parse_args()

    load_module(Path(args.python_file))

    registry = get_registry()
    func_name = args.run

    if func_name not in registry:
        print(
            f"Error: Function '{func_name}' is not registered as @tc_callable.",
            file=sys.stderr,
        )
        sys.exit(1)

    metadata = registry[func_name]
    func = metadata["func"]
    params = metadata["params"]
    return_type = metadata["return_type"]

    instance_path = args.instance_path

    # Determine the NetID to connect to
    net_id = args.ams_net_id if args.ams_net_id else pyads.PORT_LOCAL

    try:
        plc = pyads.Connection(net_id, args.ads_port)
        plc.open()

        # 1. Read input parameters from TwinCAT (internal ZCore state variables are prefixed with _)
        kwargs = {}
        for param_name, param_type in params.items():
            ads_type = map_ads_type(param_type)
            symbol_name = f"{instance_path}._{param_name}"
            try:
                val = plc.read_by_name(symbol_name, ads_type)
                kwargs[param_name] = val
            except Exception as e:
                print(
                    f"Failed to read input parameter '{symbol_name}': {e}",
                    file=sys.stderr,
                )
                # Signal error to PLC internal state
                plc.write_by_name(f"{instance_path}._bError", True, pyads.PLCTYPE_BOOL)
                plc.write_by_name(f"{instance_path}._bDone", True, pyads.PLCTYPE_BOOL)
                plc.close()
                sys.exit(1)

        # 2. Execute the python function
        try:
            result = func(**kwargs)
        except Exception as e:
            print(f"Error executing function '{func_name}': {e}", file=sys.stderr)
            plc.write_by_name(f"{instance_path}._bError", True, pyads.PLCTYPE_BOOL)
            plc.write_by_name(f"{instance_path}._bDone", True, pyads.PLCTYPE_BOOL)
            plc.close()
            sys.exit(1)

        # 3. Write result back to TwinCAT internal state
        try:
            ads_ret_type = map_ads_type(return_type)
            plc.write_by_name(f"{instance_path}._result", result, ads_ret_type)
        except Exception as e:
            print(
                f"Failed to write result to '{instance_path}._result': {e}",
                file=sys.stderr,
            )
            plc.write_by_name(f"{instance_path}._bError", True, pyads.PLCTYPE_BOOL)
            plc.write_by_name(f"{instance_path}._bDone", True, pyads.PLCTYPE_BOOL)
            plc.close()
            sys.exit(1)

        # 4. Set _bDone flag
        plc.write_by_name(f"{instance_path}._bDone", True, pyads.PLCTYPE_BOOL)

    except Exception as e:
        print(f"PyADS connection error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        try:
            plc.close()
        except:
            pass


if __name__ == "__main__":
    main()
