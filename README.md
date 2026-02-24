# TwinCAT 3 Python RPC Wrapper (`tcrpc`)

`tcrpc` is a framework that allows TwinCAT 3 Structured Text (ST) code to seamlessly call Python functions on-demand. 

Instead of running a background polling daemon, `tcrpc` uses TwinCAT's `NT_StartProcess` to launch a Python instance only when exactly needed. Data is passed transparently using PyADS, mapping Python type hints to TwinCAT memory objects via `{attribute 'instance-path'}`.

## Features
- **Zero background overhead**: Python is only executed when your PLC explicitly triggers it.
- **Zeugwerk Framework Pattern**: The ST output generates OOP interfaces that extend `ZCore.Object`, seamlessly integrating into Zeugwerk automation workflows (`RunAsync`, `Result`, etc.).
- **Built-in Timeouts**: Native TON timeout implemented in the PLC to prevent hanging processes.
- **Type-safe generation**: Annotate Python functions with standard (`int`, `str`), explicit TwinCAT (`REAL`, `UINT`), or explicit PyADS array types (`pyads.PLCTYPE_INT * 10`).
- **Auto-generated ST**: A command-line tool parses your Python script and generates ready-to-import `.TcPOU` XML files containing the necessary PLC integration logic.
- **PLC Project Updates**: Automatically update existing function block signatures inline by pointing the CLI at your TwinCAT directory.

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

This will create TwinCAT `.TcPOU` files inside the `generated/` directory (e.g., `RPC_calculate_sum.TcPOU`, `RPC_scale_value.TcPOU`).

**Update Existing Projects In-Place:**
Instead of a separate generated folder, point the CLI at your TwinCAT project directory to find existing RPC files and update their signatures:
```bash
tcrpc-gen example.py --plc-project C:\TwinCAT\MyProject\PLC
```

### 3. Import and Use in TwinCAT

1. Right-click on your TwinCAT PLC project tree, select **Add -> Existing Item...**, and select the generated `.TcPOU` files. 
2. Instantiate and call the Function Block in your ST code utilizing standard Zeugwerk OOP conventions (`RunAsync()`, `.Busy`, `.Done`, `.Result`).

```iecst
PROGRAM MAIN
VAR
    rpcCalc : RPC_calculate_sum;
    myResult: DINT;
END_VAR

// Trigger the Python execution
rpcCalc.RunAsync(a := 10, b := 20);

// Call cyclically to run the internal PLC state-machine
rpcCalc();

// Wait for completion
IF rpcCalc.Done THEN
    myResult := rpcCalc.Result; // This will now hold the value 30
ELSIF rpcCalc.Error THEN
    // Handle python runtime execution errors
END_IF
```

## How it works under the hood

When `RunAsync()` is called on the generated Zeugwerk Object:
1. The FB copies your input parameters into internal, underscored PyADS mapped variables (e.g. `_a`).
2. It sets its internal `State` to `Busy`.
3. It uses `NT_StartProcess` to execute the `tcrpc-run` CLI, passing the Python file, function name, and its own ADS `{attribute 'instance-path'}`.
4. The Python runner connects back to the PLC via PyADS, reads the input variables using the provided instance path, executes the decorated python function.
5. It writes the result back to `_result`, sets `_bDone` to `TRUE`, and the TwinCAT cyclically updating FB triggers `SetIdle()` to clear its `.Busy` flags.
6. A safety `TON` timer runs inside the PLC FB while `Busy`. If Python hangs longer than the FB's native `Timeout` variable, the PLC will autonomously hit `Abort()` to clear the execution cycle and throw an error.

## Advanced Configuration

* **Network IDs**: By default, the `tcrpc-run` process connects to the local ADS port (`851`). If you need to span multiple machines, you can adjust the `sCmdLine` generation inside the ST Template to pass specific `--ams-net-id` and `--ads-port` arguments.
