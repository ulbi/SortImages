import pytest

from math_utils import add


def test_add_returns_sum_of_two_integers():
    assert add(2, 3) == 5


def test_add_handles_zero():
    assert add(0, 7) == 7
    assert add(7, 0) == 7


def test_add_handles_negative_integers():
    assert add(-2, 5) == 3
    assert add(-4, -6) == -10


def test_add_accepts_only_integers():
    with pytest.raises(TypeError):
        add(1.5, 2.5)


def test_add_raises_on_none():
    with pytest.raises(TypeError):
        add(1, None)
