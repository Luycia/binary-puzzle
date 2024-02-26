from pathlib import Path
from typing import List, Self

import numpy as np
import pulp

import webpuzzle


class BinaryPuzzle:

    def __init__(self, grid) -> None:
        self.grid = np.asarray(grid)
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
        return self.check_binary() and self.check_parity() and self.check_triples() and self.check_uniqueness()

    def verify(self) -> bool:
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

    def to_csv(self, filename: str) -> None:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        np.savetxt(filename, self.grid, fmt='%i', delimiter=',')

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

    def solve(self) -> List[Self]:
        prob = pulp.LpProblem("Binary_Puzzle_Solver")

        # Fake objective function (no optimization problem but feasibility problem)
        prob += 0, "Arbitrary Objective Function"

        rows = range(self.N)
        cols = range(self.N)
        values = [0, 1]

        # Decision Variable/Target variable
        grid_vars = pulp.LpVariable.dicts(
            "grid_value", (rows, cols, values), cat='Binary')

        # CONSTRAINT 1: Constraint to ensure only one value is filled for a cell
        for row in rows:
            for col in cols:
                prob += pulp.lpSum([grid_vars[row][col][value]
                                   for value in values]) == 1
                # prob.addConstraint(pulp.LpConstraint(e=pulp.lpSum([grid_vars[row][col][value] for value in values]),
                #                                     sense=pulp.LpConstraintEQ, rhs=1, name=f"constraint_sum_{row}_{col}"))

        # CONSTRAINT 2: Constraint to ensure parity of rows
        for row in rows:
            for value in values:
                prob += pulp.lpSum([grid_vars[row][col][value]
                                   for col in cols]) == self.N/2
                # prob.addConstraint(pulp.LpConstraint(e=pulp.lpSum([grid_vars[row][col][value] for col in cols]),
                #                                     sense=pulp.LpConstraintEQ, rhs=self.N/2, name=f"constraint_sum_row_{row}_{value}_eq{self.N/2}"))

        # CONSTRAINT 3: Constraint to ensure parity of cols
        for col in cols:
            for value in values:
                prob += pulp.lpSum([grid_vars[row][col][value]
                                   for row in rows]) == self.N/2

        # CONSTRAINT 4: Constraint to ensure no triples
        for triple in range(self.N - 3 + 1):
            for value in values:
                for row in rows:
                    prob += pulp.lpSum([grid_vars[row][col+triple][value]
                                       for col in range(3)]) <= 2

                for col in cols:
                    prob += pulp.lpSum([grid_vars[row+triple][col][value]
                                       for row in range(3)]) <= 2

        # Fill the prefilled values from input puzzle as constraints
        for row in rows:
            for col in cols:
                if (self.grid[row][col] != -1):
                    prob += pulp.lpSum(
                        [grid_vars[row][col][value]*value for value in values]) == self.grid[row][col]

        solutions = []
        while True:
            prob.solve(pulp.PULP_CBC_CMD(msg=False))

            if pulp.LpStatus[prob.status] != "Optimal":
                break

            # Code to extract the final solution grid
            solution = [[0 for _ in cols] for _ in rows]
            for row in rows:
                for col in cols:
                    for value in values:
                        if pulp.value(grid_vars[row][col][value]) == 1:
                            solution[row][col] = value

            solution = BinaryPuzzle(solution)
            if solution.check():
                solutions.append(solution)

            prob += pulp.lpSum([grid_vars[row][col][value] for row in rows for col in cols for value in values if pulp.value(
                grid_vars[row][col][value]) == 1]) <= self.N**2 - 1

        return solutions
