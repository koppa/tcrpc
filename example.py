import pyads

from tcrpc.decorator import tc_callable
from tcrpc.types import REAL, UINT


@tc_callable
def calculate_sum(a: int, b: int) -> int:
    """A simple function to add two integers."""
    print(f"Executing calculate_sum with a={a} and b={b}")
    return a + b


@tc_callable
def greet(name: str) -> str:
    """A simple greeting function."""
    print(f"Executing greet with name={name}")
    return f"Hello, {name}!"


@tc_callable
def scale_value(value: REAL, factor: REAL) -> REAL:
    """A simple function using custom REAL types."""
    print(f"Executing scale_value with value={value} and factor={factor}")
    return value * factor


@tc_callable
def get_unsigned_sum(a: UINT, b: UINT) -> UINT:
    """A simple function using custom UINT types."""
    print(f"Executing get_unsigned_sum with a={a} and b={b}")
    return a + b


@tc_callable
def process_array(data: pyads.PLCTYPE_INT * 10) -> pyads.PLCTYPE_INT * 10:
    """A simple function taking and returning an array."""
    print(f"Executing process_array with data={list(data)}")
    # Just return the array back with values multiplied by 2
    result = (pyads.PLCTYPE_INT * 10)()
    for i in range(10):
        result[i] = data[i] * 2
    return result
