import argparse
import importlib.util
import os
import sys
from pathlib import Path

import jinja2

from tcrpc.decorator import get_registry
from tcrpc.types import CTYPES_TO_ST, TYPE_MAPPING


def map_type(python_type) -> str:
    """Map a Python type to a TwinCAT ST type."""
    if hasattr(python_type, "_length_") and hasattr(python_type, "_type_"):
        inner_st_type = map_type(python_type._type_)
        return f"ARRAY [0..{python_type._length_ - 1}] OF {inner_st_type}"

    if (
        hasattr(python_type, "__module__")
        and hasattr(python_type, "__name__")
        and python_type.__module__ in ("_ctypes", "ctypes")
    ):
        try:
            return CTYPES_TO_ST[python_type]
        except KeyError:
            pass
    try:
        return TYPE_MAPPING[python_type]
    except KeyError:
        # For now, custom types or unsupported types fallback to STRING or raise an error
        raise ValueError(f"Unsupported Python type for TwinCAT mapping: {python_type}")


# Setup jinja2 environment
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), "templates")
    ),
    trim_blocks=True,
    lstrip_blocks=True,
)


def generate_fb(func_name: str, params: dict, return_type, script_path: str) -> str:
    """Generate the Function Block string that orchestrates the RPC call."""
    template = env.get_template("fb.st.jinja2")
    return template.render(
        func_name=func_name,
        params=params,
        return_type=return_type,
        script_cmd=script_path,
        map_type=map_type,
    )


def find_file(plc_dir: Path, filename: str) -> Path:
    """Recursively search for an existing file in the PLC project."""
    for path in plc_dir.rglob(filename):
        return path
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate or update TwinCAT ST code for decorated Python functions."
    )
    parser.add_argument(
        "python_file", help="The Python file containing @tc_callable functions."
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="Directory to save the generated ST files (default mode).",
    )
    parser.add_argument(
        "--plc-project",
        default=None,
        help="Path to a TwinCAT PLC project directory. If provided, the generator will look for existing FB files, verify them, and update them.",
    )

    args = parser.parse_args()

    file_path = Path(args.python_file)
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)

    # Dynamically import the provided module
    module_name = file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        print(f"Error: Could not load module from {file_path}")
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    # Add the file's dir to sys.path so it can import its own local modules if needed
    sys.path.insert(0, str(file_path.parent))

    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error executing module: {e}")
        sys.exit(1)

    registry = get_registry()
    if not registry:
        print("No @tc_callable functions found.")
        sys.exit(0)

    plc_mode = bool(args.plc_project)
    if plc_mode:
        plc_dir = Path(args.plc_project)
        if not plc_dir.exists() or not plc_dir.is_dir():
            print(
                f"Error: PLC project directory {plc_dir} does not exist or is not a directory."
            )
            sys.exit(1)
        print(f"Running in PLC update mode: {plc_dir}")
    else:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    for func_name, metadata in registry.items():
        print(f"Processing: {func_name}")
        params = metadata["params"]
        ret_type = metadata["return_type"]

        # In a real scenario, we use the `tcrpc-run` entry point and pass the module.
        script_cmd = f"{file_path.resolve()} --run {func_name}"

        fb_code = generate_fb(func_name, params, ret_type, script_cmd)
        filename = f"RPC_{func_name}.TcPOU"

        if plc_mode:
            pou_path = find_file(plc_dir, filename)
            if not pou_path:
                print(f"Error: Could not find {filename} in PLC project {plc_dir}")
                print(
                    f"Make sure you have created the FB manually or generated it once before updating."
                )
                sys.exit(1)

            print(f"  Updating existing POU: {pou_path.relative_to(plc_dir)}")
            with open(pou_path, "w") as f:
                f.write(fb_code)
        else:
            out_file = output_dir / filename
            with open(out_file, "w") as f:
                f.write(fb_code)
            print(f"  Generated: {out_file}")

    print("Generation/Update complete.")


if __name__ == "__main__":
    main()
