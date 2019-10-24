import pytest
from board import *

@pytest.fixture
def BOARD():
    return Board()

@ pytest.fixture
def GRID_1():
    b = Board()
    b.build(
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

@pytest.fixture
def GRID_2():
    b = Board()
    b.build(
                [
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                    [0, 1, 0, 0, 0],
                    [0, 0, 3, 0, 0],
                    [0, 0, 0, 0, 0]
                ]
            )
    return b


def test_is_solved_true(SOL_1):
    assert SOL_1.is_solved(), "is_solved_true failed"

def test_is_solved_false(GRID_1):
    assert not GRID_1.is_solved(), "is_solved_false failed"


def test_find_reach_white(GRID_2):
    result = {(1,4), (2,3), (2,4), (3,2), (3,3), (3,4), (4,3)}
    region = [r for r in GRID_2.white_regions if r.size == 3][0] #the only region of size 3
    assert {cell.coords for cell in GRID_2.find_reach_white(region)} == result, "find_reach_white failed"


def test_find_unreachable(GRID_1, SOL_1):
    GRID_1.find_unreachable()
    assert GRID_1 == SOL_1, "find_unreachable failed"



