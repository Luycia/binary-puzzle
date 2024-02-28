from typing import List, Tuple

import pulp

from src.binary_puzzle.puzzle import BinaryPuzzle


def _build_model(puzzle: BinaryPuzzle) -> Tuple[pulp.LpProblem, pulp.LpVariable.dicts]:
    prob = pulp.LpProblem("Binary_Puzzle_Solver")

    # Fake objective function (no optimization problem but feasibility problem)
    prob += 0, "Arbitrary Objective Function"

    N = puzzle.N
    rows = range(N)
    cols = range(N)
    values = [0, 1]

    # Decision Variable/Target variable
    grid_vars = pulp.LpVariable.dicts(
        "grid_value", (rows, cols, values), cat='Binary')

    # CONSTRAINT 1: Constraint to ensure only one value is filled for a cell
    for row in rows:
        for col in cols:
            prob += pulp.lpSum([grid_vars[row][col][value]
                                for value in values]) == 1

    # CONSTRAINT 2: Constraint to ensure parity of rows
    for row in rows:
        for value in values:
            prob += pulp.lpSum([grid_vars[row][col][value]
                                for col in cols]) == N/2

    # CONSTRAINT 3: Constraint to ensure parity of cols
    for col in cols:
        for value in values:
            prob += pulp.lpSum([grid_vars[row][col][value]
                                for row in rows]) == N/2

    # CONSTRAINT 4: Constraint to ensure no triples
    for triple in range(N - 3 + 1):
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
            if (puzzle.grid[row][col] != -1):
                prob += pulp.lpSum(
                    [grid_vars[row][col][value]*value for value in values]) == puzzle.grid[row][col]

    return prob, grid_vars


def _decision_var_to_puzzle(grid: pulp.LpVariable.dict) -> BinaryPuzzle:
    # Code to extract the final solution grid
    solution = [[0 for _ in range(len(grid))] for _ in range(len(grid))]
    for row in range(len(grid)):
        for col in range(len(grid)):
            for value in grid[row][col]:
                if pulp.value(grid[row][col][value]) == 1:
                    solution[row][col] = value

    return BinaryPuzzle(solution)


def _add_current_solution_as_constraint(prob: pulp.LpProblem, grid_vars: pulp.LpVariable.dict):
    N = len(grid_vars)
    prob += pulp.lpSum([grid_vars[row][col][value]
                        for row in range(N)
                        for col in range(N)
                        for value in grid_vars[row][col]
                        if pulp.value(grid_vars[row][col][value]) == 1]) <= N**2 - 1


def solve(puzzle: BinaryPuzzle) -> BinaryPuzzle:
    """
    Returns a single possible solution for given binary puzzle.

        Parameters:
            puzzle (BinaryPuzzle): The puzzle to be solved

        Returns:
            BinaryPuzzle: Possible solution that solve the puzzle
    """

    prob, grid_vars = _build_model(puzzle)

    while True:
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        if pulp.LpStatus[prob.status] != "Optimal":
            return None

        solution = _decision_var_to_puzzle(grid_vars)
        if solution.check():
            return solution

        _add_current_solution_as_constraint(prob, grid_vars)


def solve_all(puzzle: BinaryPuzzle) -> List[BinaryPuzzle]:
    """
    Returns all possible solutions for given binary puzzle. If the size of the solutions equals 1, the solution is unique.

        Parameters:
            puzzle (BinaryPuzzle): The puzzle to be solved

        Returns:
            List[BinaryPuzzle]: List of all possible solutions that solve the puzzle
    """

    prob, grid_vars = _build_model(puzzle)

    solutions = []
    while True:
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        if pulp.LpStatus[prob.status] != "Optimal":
            break

        solution = _decision_var_to_puzzle(grid_vars)
        if solution.check():
            solutions.append(solution)

        _add_current_solution_as_constraint(prob, grid_vars)

    return solutions
