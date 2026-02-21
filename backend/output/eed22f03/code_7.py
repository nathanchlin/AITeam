from src.your_module import add, multiply

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 5) == 4

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(0, 5) == 0

# 使用pytest的参数化功能
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (-1, 5, 4),
    (0, 0, 0)
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected