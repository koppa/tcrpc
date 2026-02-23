import argparse
import sys
import os
import importlib.util
from pathlib import Path
import pyads

from tcrpc.decorator import get_registry
from tcrpc.types import REAL, SINT, INT, DINT, LINT, USINT, UINT, UDINT, ULINT, BYTE, WORD, DWORD, LWORD

# Mapping from Python types to pyads constants
ADS_TYPE_MAPPING = {
    int: pyads.PLCTYPE_DINT,
    float: pyads.PLCTYPE_LREAL,
    bool: pyads.PLCTYPE_BOOL,
    str: pyads.PLCTYPE_STRING,
    REAL: pyads.PLCTYPE_REAL,
    SINT: pyads.PLCTYPE_SINT,
    INT: pyads.PLCTYPE_INT,
    DINT: pyads.PLCTYPE_DINT,
    LINT: pyads.PLCTYPE_LINT,
    USINT: pyads.PLCTYPE_USINT,
    UINT: pyads.PLCTYPE_UINT,
    UDINT: pyads.PLCTYPE_UDINT,
    ULINT: pyads.PLCTYPE_ULINT,
    BYTE: pyads.PLCTYPE_BYTE,
    WORD: pyads.PLCTYPE_WORD,
    DWORD: pyads.PLCTYPE_DWORD,
    LWORD: getattr(pyads, 'PLCTYPE_LWORD', pyads.PLCTYPE_ULINT),
}

def map_ads_type(python_type):
    """Retrieve the corresponding PyADS PLC type for a given Python type."""
    if python_type in ADS_TYPE_MAPPING:
        return ADS_TYPE_MAPPING[python_type]
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
    parser = argparse.ArgumentParser(description="Run a @tc_callable Python function, reading/writing via PyADS.")
    parser.add_argument("python_file", help="The Python file containing the @tc_callable function.")
    parser.add_argument("--run", required=True, help="The name of the function to run.")
    parser.add_argument("--instance-path", required=True, help="The ADS path of the FB instance.")
    parser.add_argument("--ams-net-id", default=None, help="The AMS Net ID of the target PLC (default: local).")
    parser.add_argument("--ads-port", type=int, default=851, help="The ADS port of the target PLC (default: 851).")
    
    args = parser.parse_args()
    
    load_module(Path(args.python_file))
    
    registry = get_registry()
    func_name = args.run
    
    if func_name not in registry:
        print(f"Error: Function '{func_name}' is not registered as @tc_callable.", file=sys.stderr)
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
        
        # 1. Read input parameters from TwinCAT
        kwargs = {}
        for param_name, param_type in params.items():
            ads_type = map_ads_type(param_type)
            symbol_name = f"{instance_path}.{param_name}"
            try:
                val = plc.read_by_name(symbol_name, ads_type)
                kwargs[param_name] = val
            except Exception as e:
                print(f"Failed to read input parameter '{symbol_name}': {e}", file=sys.stderr)
                # Signal error to PLC
                plc.write_by_name(f"{instance_path}.bError", True, pyads.PLCTYPE_BOOL)
                plc.write_by_name(f"{instance_path}.bDone", True, pyads.PLCTYPE_BOOL)
                plc.close()
                sys.exit(1)
                
        # 2. Execute the python function
        try:
            result = func(**kwargs)
        except Exception as e:
            print(f"Error executing function '{func_name}': {e}", file=sys.stderr)
            plc.write_by_name(f"{instance_path}.bError", True, pyads.PLCTYPE_BOOL)
            plc.write_by_name(f"{instance_path}.bDone", True, pyads.PLCTYPE_BOOL)
            plc.close()
            sys.exit(1)
            
        # 3. Write result back to TwinCAT
        try:
            ads_ret_type = map_ads_type(return_type)
            plc.write_by_name(f"{instance_path}.result", result, ads_ret_type)
        except Exception as e:
            print(f"Failed to write result to '{instance_path}.result': {e}", file=sys.stderr)
            plc.write_by_name(f"{instance_path}.bError", True, pyads.PLCTYPE_BOOL)
            plc.write_by_name(f"{instance_path}.bDone", True, pyads.PLCTYPE_BOOL)
            plc.close()
            sys.exit(1)
            
        # 4. Set bDone flag
        plc.write_by_name(f"{instance_path}.bDone", True, pyads.PLCTYPE_BOOL)
        
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
