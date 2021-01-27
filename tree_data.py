"""Assignment 2: Trees for Treemap

=== CSC148 Fall 2020 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""

from __future__ import annotations
import os
from random import randint
import math
from typing import Tuple, List, Optional


class AbstractTree:
    """A tree that is compatible with the treemap visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you adding and implementing
    new public *methods* for this interface.

    === Public Attributes ===
    data_size: the total size of all leaves of this tree.
    colour: The RGB colour value of the root of this tree.
        Note: only the colours of leaves will influence what the user sees.

    === Private Attributes ===
    _root: the root value of this tree, or None if this tree is empty.
    _subtrees: the subtrees of this tree.
    _parent_tree: the parent tree of this tree; i.e., the tree that contains
        this tree
        as a subtree, or None if this tree is not part of a larger tree.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - colour's elements are in the range 0-255.

    - If _root is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - _subtrees IS allowed to contain empty subtrees (this makes deletion
      a bit easier).

    - if _parent_tree is not empty, then self is in _parent_tree._subtrees
    """
    data_size: int
    colour: (int, int, int)
    _root: Optional[object]
    _subtrees: List[AbstractTree]
    _parent_tree: Optional[AbstractTree]

    def __init__(self: AbstractTree, root: Optional[object],
                 subtrees: List[AbstractTree], data_size: int = 0) -> None:
        """Initialize a new AbstractTree.

        If <subtrees> is empty, <data_size> is used to initialize this tree's
        data_size. Otherwise, the <data_size> parameter is ignored, and this
        tree's data_size is computed from the data_sizes of the subtrees.

        If <subtrees> is not empty, <data_size> should not be specified.

        This method sets the _parent_tree attribute for each subtree to self.

        A random colour is chosen for this tree.

        Precondition: if <root> is None, then <subtrees> is empty.
        """
        self._root = root
        self._subtrees = subtrees
        self._parent_tree = None

        # 1. Initialize self.colour and self.data_size,
        # according to the docstring.
        # 2. Properly set all _parent_tree attributes in self._subtrees
        self.colour = randint(0, 255), randint(0, 255), randint(0, 255)

        if not self._subtrees:
            self.data_size = data_size
        else:
            # Sets Data Size for current tree root
            self.data_size = self.get_data_size()
            self.set_parent()

    def is_empty(self: AbstractTree) -> bool:
        """Return True if this tree is empty."""
        return self._root is None

    def generate_treemap(self: AbstractTree, rect: Tuple[int, int, int, int]) \
            -> List[Tuple[Tuple[int, int, int, int], Tuple[int, int, int]]]:
        """Run the treemap algorithm on this tree and return the rectangles.

        Each returned tuple contains a pygame rectangle and a colour:
        ((x, y, width, height), (r, g, b)).

        One tuple should be returned per non-empty leaf in this tree.

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: list[((int, int, int, int), (int, int, int))]
        """
        # Read the handout carefully to help get started identifying base cases,
        # and the outline of a recursive step.
        #
        # Programming tip: use "tuple unpacking assignment" to easily extract
        # coordinates of a rectangle, as follows.
        # x, y, width, height = rect
        if self.data_size == 0:
            return []
        if not self._subtrees and self.data_size > 0:
            return [(rect, self.colour)]
        x, y, width, height = rect
        if self._subtrees[-1].data_size == 0:
            self._subtrees = self._subtrees[:-1]
        final_lst = []
        width_counter = 0
        height_counter = 0
        if width > height:
            for tree in self._subtrees:
                if tree != self._subtrees[-1]:
                    percent = tree.data_size / self.data_size
                    new_width = int(percent * width)
                    new_rect = (x, y, new_width, height)
                    final_lst.extend(tree.generate_treemap(new_rect))
                    x += new_width
                    width_counter += new_width
                else:
                    new_width = width - width_counter
                    new_rect = (x, y, new_width, height)
                    final_lst.extend(tree.generate_treemap(new_rect))
            return final_lst
        for tree in self._subtrees:
            if tree != self._subtrees[-1]:
                percent = tree.data_size / self.data_size
                new_height = int(percent * height)
                new_rect = (x, y, width, new_height)
                final_lst.extend(tree.generate_treemap(new_rect))
                y += new_height
                height_counter += new_height
            else:
                new_height = height - height_counter
                new_rect = (x, y, width, new_height)
                final_lst.extend(tree.generate_treemap(new_rect))
        return final_lst

    def selected(self, coord: Tuple[int, int],
                 rects:
                 List[Tuple[Tuple[int, int, int, int], Tuple[int, int, int]]],
                 ) \
            -> Optional[AbstractTree]:
        """Selects or deselects a rectangle"""

        leaves = self.get_leaves()
        if not leaves:
            return None
        x, y = coord
        for index, value in enumerate(leaves):
            old_x = rects[index][0][0]
            old_y = rects[index][0][1]
            width = rects[index][0][2]
            height = rects[index][0][3]

            if x < width + old_x and y < height + old_y:
                return value
        return None

    def selected_text(self) -> str:
        """Gets path of leaf """
        lst = [str(self._root)]
        if self._parent_tree:
            lst.extend(self._parent_tree.selected_text_helper())
        lst.reverse()
        path = ""
        for value in lst:
            path += value + self.get_separator()
        return path + " " + "(" + str(self.data_size) + ")"

    def selected_text_helper(self) -> List[str]:
        """finds parents """
        if not self._parent_tree:
            return [str(self._root)]
        lst = [str(self._root)]
        if self._parent_tree:
            lst.extend(self._parent_tree.selected_text_helper())
        return lst

    def get_leaves(self) -> List[AbstractTree]:
        """Gets all leaves of trees"""
        if self.data_size == 0:
            return []
        if not self._subtrees:
            return [self]
        lst = []
        for tree in self._subtrees:
            lst.extend(tree.get_leaves())
        return lst

    def get_path(self, leaf: AbstractTree) -> str:
        """Gets path of leaf """
        lst = [str(leaf._root)]
        while leaf._parent_tree:
            lst.append(str(leaf._parent_tree._root))
            leaf = leaf._parent_tree
        lst.reverse()
        path = ""
        for value in lst:
            path += self.get_separator() + value
        return path

    def deleted(self) -> None:
        """Removes a rectangle that represents leaf """
        remover = self.data_size
        if self._parent_tree:
            self._parent_tree.deleted_helper(remover)
            for i in self._parent_tree._subtrees:
                if i == self:
                    self._parent_tree._subtrees.remove(self)
        self.data_size = 0

    def deleted_helper(self, num: int) -> None:
        """delete helper"""
        self.data_size -= num
        if self._parent_tree:
            self._parent_tree.deleted_helper(num)

    def grow(self) -> None:
        """Grows a data set """
        percent = math.ceil(self.data_size * 0.01)
        self.data_size += percent
        if self._parent_tree:
            self._parent_tree.parent_grower(percent)

    def shrink(self) -> None:
        """Shrinks a data set """
        percent = math.ceil(self.data_size * 0.01)
        if self.data_size == 1:
            return
        if self.data_size - percent < 1:
            self.data_size = 1
            if self._parent_tree:
                self._parent_tree.parent_shrink(1)
        else:
            self.data_size -= percent
            if self._parent_tree:
                self._parent_tree.parent_shrink(percent)

    def parent_grower(self, num: int) -> None:
        """Grows the parents of the file  """
        self.data_size += num
        if self._parent_tree:
            self._parent_tree.parent_grower(num)

    def parent_shrink(self, num: int) -> None:
        """shrinks the parents of the file """
        if self.data_size - num < 1:
            self.data_size = 1
            if self._parent_tree:
                self._parent_tree.parent_shrink(1)
        else:
            self.data_size -= num
            if self._parent_tree:
                self._parent_tree.parent_shrink(num)

    def get_separator(self: AbstractTree) -> str:
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.

        This should be overridden by each AbstractTree subclass, to customize
        how these items are separated for different data domains.
        """
        raise NotImplementedError

    def get_data_size(self) -> int:
        """ Provides total data contingent on the subtrees """
        if not self._subtrees:
            return self.data_size
        total = 0
        for tree in self._subtrees:
            if not tree._subtrees:
                total += tree.data_size
            else:
                total += tree.get_data_size()
        return total

    def set_parent(self) -> None:
        """Sets parent tree to each subtree """
        for tree in self._subtrees:
            tree._parent_tree = self
            if tree._subtrees:
                tree.set_parent()


class FileSystemTree(AbstractTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _root attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/David/csc148/assignments'

    The data_size attribute for regular files as simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self: FileSystemTree, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        # Remember that you should recursively go through the file system
        # and create new FileSystemTree objects for each file and folder
        # encountered.
        #
        # Also remember to make good use of the superclass constructor!
        root = os.path.basename(path)
        if os.path.isdir(path):
            sub_path = os.listdir(path)
            subtrees = self.get_sub_files(sub_path, path)
            AbstractTree.__init__(self, root, subtrees)

        else:
            data = os.path.getsize(path)
            subtrees = []
            AbstractTree.__init__(self, root, subtrees, data)

    def get_separator(self: FileSystemTree) -> str:
        """ Implementation of abstract separator """
        return "/"

    @staticmethod
    def get_sub_files(subtrees: List[str], path: str) -> List[FileSystemTree]:
        """
            Implements subtree of the tree and turns the file path into trees
        """
        lst = []
        for file in subtrees:
            new_path = os.path.join(path, file)
            other_tree = FileSystemTree(new_path)
            if os.path.isdir(new_path):
                new_subtree = os.listdir(new_path)
                other_tree.get_sub_files(new_subtree, new_path)
            lst.append(other_tree)
        return lst


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(
        config={
            'extra-imports': ['os', 'random', 'math'],
            'generated-members': 'pygame.*'})
