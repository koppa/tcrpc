import pytest

from tcrpc.decorator import get_registry, tc_callable


def test_missing_param_type():
    with pytest.raises(ValueError, match="missing a type hint"):

        @tc_callable
        def func1(a, b: int) -> int:
            return a + b


def test_missing_return_type():
    with pytest.raises(ValueError, match="missing a return type hint"):

        @tc_callable
        def func2(a: int, b: int):
            return a + b


def test_successful_registration():
    registry_before = len(get_registry())

    @tc_callable
    def func3(a: int) -> str:
        return "test"

    registry = get_registry()
    assert len(registry) == registry_before + 1
    assert "func3" in registry
    assert registry["func3"]["params"] == {"a": int}
    assert registry["func3"]["return_type"] == str
    assert registry["func3"]["name"] == "func3"
