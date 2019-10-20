import pytest
from board import *

@pytest.fixture
def BOARD():
    return Board()

@ pytest.fixture
def GRID_1():
    b = Board()
    b.manual_build(
                    [
                        [0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0],
                        [3, 0, 0, 2, 0],
                        [0, 0, 0, 0, 1],
                        [3, 0, 0, 0, 0]
                    ]
                  )
    return b

@pytest.fixture
def SOL_1():
    b = Board()
    b.manual_build(
                    [
                        [2, 2, 2, 2, 2],
                        [2, 1, 2, 1, 2],
                        [1, 1, 2, 1, 2],
                        [2, 2, 2, 2, 1],
                        [1, 1, 1, 2, 2]
                    ]
                  )
    return b

def test_is_solved_true(SOL_1):
    assert SOL_1.is_solved(), "Test failed"

def test_is_solved_false(GRID_1):
    assert not GRID_1.is_solved(), "Test failed"


def test_find_unreachable(GRID_1. SOL_1):
    GRID_1.find_unreachable()
    assert GRID_1 == SOL_1, "Test failed"



