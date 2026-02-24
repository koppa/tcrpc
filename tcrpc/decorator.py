import inspect
from typing import Any, Callable, Dict

# Registry to hold all decorated functions
_REGISTRY: Dict[str, Dict[str, Any]] = {}


def get_registry() -> Dict[str, Dict[str, Any]]:
    """Return the global registry of tcrpc functions."""
    return _REGISTRY


def tc_callable(func: Callable) -> Callable:
    """
    Decorator to mark a Python function as callable from TwinCAT.
    The function must have full type hints (parameters and return).
    """
    sig = inspect.signature(func)

    # Extract parameter names and types
    params = {}
    for name, param in sig.parameters.items():
        if param.annotation == inspect.Parameter.empty:
            raise ValueError(
                f"Function {func.__name__} parameter '{name}' is missing a type hint."
            )
        params[name] = param.annotation

    # Extract return type
    return_type = sig.return_annotation
    if return_type == inspect.Signature.empty:
        raise ValueError(f"Function {func.__name__} is missing a return type hint.")

    _REGISTRY[func.__name__] = {
        "func": func,
        "params": params,
        "return_type": return_type,
        "name": func.__name__,
        "doc": inspect.getdoc(func),
    }

    return func
