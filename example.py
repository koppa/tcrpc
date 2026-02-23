from tcrpc.decorator import tc_callable

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
