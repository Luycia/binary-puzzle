from pathlib import Path
from typing import Self

import numpy as np


class BinaryPuzzle:

    def __init__(self, grid) -> None:
        self.grid = np.asarray(grid, dtype=np.int8)
        self.N = self.grid.shape[0]
        self._check_valid_shape()

    def _check_valid_shape(self):
        if len(self.grid.shape) != 2:
            raise ValueError(
                f"Grid must be 2-dimensional, but actual {len(self.grid.shape)} dimensions")

        if self.grid.shape[0] != self.grid.shape[1]:
            raise ValueError(
                f"Grid must be quadratic shape, expected {self.N}x{self.N}, but actual {self.grid.shape[0]}x{self.grid.shape[1]}")

        if self.N % 2 != 0:
            raise ValueError("Grid size must be even")

        if self.N == 0:
            raise ValueError("Grid must be at least size 2")

        return True

    def check_binary(self) -> bool:
        return np.isin(self.grid, [0, 1]).all()

    def check_parity(self) -> bool:
        return (self.grid.sum(axis=0) == self.N / 2).all() \
            and (self.grid.sum(axis=1) == self.N / 2).all()

    def _check_triples_row(self, puzzle) -> bool:
        for row in puzzle:
            triples = [np.array(row[i:i+3]) for i in range(len(row)-3+1)]
            for triple in triples:
                if triple.sum() in [0, 3]:
                    return False
        return True

    def check_triples(self) -> bool:
        return self._check_triples_row(self.grid) and self._check_triples_row(self.grid.T)

    def check_uniqueness(self) -> bool:
        return np.unique(self.grid, axis=0).shape[0] == self.N and np.unique(self.grid, axis=1).shape[1] == self.N

    def check(self) -> bool:
        """
        Checks whether the puzzle meets the rules.

            Returns:
                bool: True if puzzle is valid
        """

        return self.check_binary() and self.check_parity() and self.check_triples() and self.check_uniqueness()

    def verify(self) -> bool:
        """
        Checks whether the puzzle meets the rules. If not, an exception is raised.

            Returns:
                bool: True if puzzle is valid
        """

        if not self.check_binary():
            raise ValueError("All grid values must be 0 or 1")

        if not self.check_parity():
            raise ValueError(
                "All rows and columns must have equal amount of 0 and 1 (parity)")

        if not self.check_triples():
            raise ValueError(
                "No row and column are allowed to have three times the same number (triples)")

        if not self.check_uniqueness():
            raise ValueError("All rows and columns must be unique")

        return True

    def __str__(self) -> str:
        s = ""

        # Top
        s += f"┌───┬{''.join((self.N-2) * ['───┬'])}───┐\n"

        # Middle
        for i, row in enumerate(self.grid):
            s += "│"
            for cell in row:
                symbol = cell if cell != -1 else " "
                s += f" {symbol} │"

            s += "\n"
            if i < self.N - 1:
                s += f"├───┼{''.join((self.N-2) * ['───┼'])}───┤\n"

        # Bottom
        s += f"└───┴{''.join((self.N-2) * ['───┴'])}───┘\n"

        return s

    def to_csv(self, filename: str) -> None:
        """
        Saves puzzles in CSV. If parent folders do not exist in the path, they are created.

            Parameters:
                filename (str): Specifies the name of the file
            Returns:
                bool: True if puzzle is valid
        """

        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        grid = self.grid.astype(str)
        grid[grid == '-1'] = ''
        np.savetxt(filename, grid, fmt='%s', delimiter=',')


@staticmethod
def from_csv(filename: str) -> Self:
    return BinaryPuzzle(np.genfromtxt(filename, delimiter=',', dtype=np.int8, filling_values=-1))
