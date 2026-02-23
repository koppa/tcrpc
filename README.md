# TwinCAT 3 Python RPC Wrapper (`tcrpc`)

`tcrpc` is a framework that allows TwinCAT 3 Structured Text (ST) code to seamlessly call Python functions on-demand. 

Instead of running a background polling daemon, `tcrpc` uses TwinCAT's `NT_StartProcess` to launch a Python instance only when exactly needed. Data is passed transparently using PyADS, mapping Python type hints to TwinCAT memory objects via `{attribute 'instance-path'}`.

## Features
- **Zero background overhead**: Python is only executed when your PLC explicitly triggers it.
- **Type-safe generation**: Annotate Python functions with standard (`int`, `str`, `float`) or explicit TwinCAT (`REAL`, `UINT`, etc.) types.
- **Auto-generated ST**: A command-line tool parses your Python script and generates ready-to-import `.TcPOU` XML files containing the necessary PLC integration logic.

## Installation

Install the package directly into your environment:
```bash
pip install -e .
```
*(Requires `pyads` and `jinja2`)*

## Usage Guide

### 1. Annotate your Python functions

Create a Python script (e.g., `example.py`) and use the `@tc_callable` decorator to mark functions you want to call from TwinCAT. You *must* include parameter and return type hints.

```python
from tcrpc.decorator import tc_callable
from tcrpc.types import REAL, UINT

@tc_callable
def calculate_sum(a: int, b: int) -> int:
    """A simple function to add two integers."""
    return a + b

@tc_callable
def scale_value(value: REAL, factor: REAL) -> REAL:
    """A simple function using custom REAL types."""
    return value * factor
```

### 2. Generate the TwinCAT Code

Run the code generator CLI against your Python script:
```bash
tcrpc-gen example.py -o generated/
```

This will create TwinCAT `.TcPOU` files inside the `generated/` directory (e.g., `FB_calculate_sum.TcPOU`, `FB_scale_value.TcPOU`).

### 3. Import and Use in TwinCAT

1. Right-click on your TwinCAT PLC project tree, select **Add -> Existing Item...**, and select the generated `.TcPOU` files. 
2. Instantiate and call the Function Block in your ST code.

```iecst
PROGRAM MAIN
VAR
    fbCalc : FB_calculate_sum;
    myResult: DINT;
END_VAR

// Trigger the Python execution
fbCalc(a := 10, b := 20, bExecute := TRUE);

// Wait for completion
IF fbCalc.bDone THEN
    fbCalc(bExecute := FALSE);
    myResult := fbCalc.result; // This will now hold the value 30
END_IF
```

## How it works under the hood

When `bExecute` is set to `TRUE` in the generated Function Block:
1. The FB copies your input parameters internally.
2. It uses `NT_StartProcess` to execute the `tcrpc-run` CLI, passing the Python file, function name, and its own ADS `{attribute 'instance-path'}`.
3. The Python runner connects back to the PLC via PyADS, reads the input variables using the provided instance path, executes the decorated python function, writes the `result` back to the PLC instance path, and sets `bDone` to `TRUE`.
4. The TwinCAT FB finishes its polling cycle, clearing its `bBusy` flag and outputting the result.

## Advanced Configuration

* **Network IDs**: By default, the `tcrpc-run` process connects to the local ADS port (`851`). If you need to span multiple machines, you can adjust the `sCmdLine` generation inside the ST Template to pass specific `--ams-net-id` and `--ads-port` arguments.
