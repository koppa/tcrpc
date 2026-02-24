from tcrpc.decorator import tc_callable


@tc_callable
def dummy_func(a: int) -> int:
    return a * 2
