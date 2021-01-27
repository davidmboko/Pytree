"""Assignment 2 - Tests

=== CSC148 Fall 2020 ===
Daniel Zingaro, Diane Horton, and David Liu
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains sample tests for Assignment 2, Tasks 1 and 2.
Note that the data set here is a pretty small one, but should be enough to
give you an idea of how we could test your code.

NOTES:
    - If using PyCharm, go into your Settings window, and go to
      Editor -> General.
      Make sure the "Ensure line feed at file end on Save" is NOT checked.
      Then, make sure none of the example files have a blank line at the end.
      (If they do, the data size will be off.)

    - os.listdir behaves differently on different
      operating systems, so these tests have been updated
      to work on the *Teaching Lab machines*.
      Please do your testing there - otherwise,
      you might get inaccurate test failures!
"""
import os

import pytest
from hypothesis import given
from hypothesis.strategies import integers

from tree_data import FileSystemTree

# This should be the path to the "B" folder in the sample data.
# You may need to modify this, depending on where you downloaded and
# extracted the files.
from tree_data import AbstractTree

EXAMPLE_PATH = os.path.join('example-data', 'B')


def test_single_file() -> None:
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'f4.txt'))
    assert tree._root == 'f4.txt'
    assert tree._subtrees == []
    assert tree._parent_tree is None

    assert tree.data_size == 10

    # Check colours
    for i in range(3):
        assert tree.colour[i] >= 0
        assert tree.colour[i] <= 255


def test_example_data_basic() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    assert tree._root == 'B'
    assert tree._parent_tree is None

    assert tree.data_size == 40

    # Check colours
    for i in range(3):
        assert tree.colour[i] >= 0
        assert tree.colour[i] <= 255


def test_example_data_parent_tree_of_subtrees() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)

    assert len(tree._subtrees) == 2

    for subtree in tree._subtrees:
        # Note the use of is rather than ==.
        # This checks ids rather than values.
        assert subtree._parent_tree is tree


def test_example_data_subtree_order() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)

    assert len(tree._subtrees) == 2
    first, second = tree._subtrees

    assert first._root == 'A'
    assert len(first._subtrees) == 3
    assert first.data_size == 30

    assert second._root == 'f4.txt'
    assert second._subtrees == []
    assert second.data_size == 10


@given(integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000),
       integers(min_value=100, max_value=1000))
def test_single_file(x: int, y: int, width: int, height: int) -> None:
    tree = FileSystemTree(os.path.join(EXAMPLE_PATH, 'f4.txt'))
    rects = tree.generate_treemap((x, y, width, height))

    # This should be just a single rectangle and colour returned.
    assert len(rects) == 1
    rect, colour = rects[0]
    assert rect == (x, y, width, height)

    for i in range(3):
        assert colour[i] >= 0
        assert colour[i] <= 255


def test_example_data() -> None:
    tree = FileSystemTree(EXAMPLE_PATH)
    _sort_subtrees(tree)

    rects = tree.generate_treemap((0, 0, 800, 1000))

    # This should be one rectangle per file in 'B'.
    assert len(rects) == 4

    # Here, we illustrate the correct order of the returned rectangles.
    # Note that this corresponds to the folder contents always being
    # sorted in alphabetical order.
    rect_f1 = rects[0][0]  # f1.txt
    rect_f2 = rects[1][0]  # f2.txt
    rect_f3 = rects[2][0]  # f3.txt
    rect_f4 = rects[3][0]  # f4.txt

    # The 'A' rectangle is (0, 0, 800, 750).
    assert rect_f1 == (0, 0, 400, 750)
    # Note the rounding down on f2.
    assert rect_f2 == (400, 0, 133, 750)
    # Note the adjustment to f3 to bring the total width to 800.
    assert rect_f3 == (533, 0, 267, 750)

    # The 'f4.txt' rectangle.
    assert rect_f4 == (0, 750, 800, 250)


##############################################################################
# Helper to sort subtrees alphabetically
##############################################################################
def _sort_subtrees(tree: AbstractTree) -> None:
    """Sort the subtrees of <tree> in alphabetical order.

    This is recursive, and affects all levels of the tree.

    @type tree: AbstractTree
    @rtype: None
    """
    if not tree.is_empty():
        for subtree in tree._subtrees:
            _sort_subtrees(subtree)

        tree._subtrees.sort(key=lambda t: t._root)


if __name__ == '__main__':
    pytest.main(['a2_test.py'])
