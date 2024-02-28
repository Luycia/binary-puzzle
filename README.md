# Binary Puzzle
The aim of the game is to fill in the empty fields in accordance with certain rules. The game principle is similar to Sudoku. The following rules must be observed:
 1. **Binary:** The playing field may only be filled with zeros and ones.
 2. **Parity:** The number of zeros and ones must be the same in each row and column.
 3. **No triples:** Neither horizontal nor vertical triples (three times the same number next to each other) are allowed.
 4. **Uniqueness:** All rows and columns must be unique, i.e. a row cannot be exactly the same as another row and no column can be exactly the same as another column.

## Example
**Puzzle**  
|   |   |   |   |   |   |   |   |
|---|---|---|---|---|---|---|---|
|   |   |   |1  |1  |   |   |0  |
|   |0  |   |   |   |0  |   |   |
|   |0  |0  |   |   |   |   |   |
|1  |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |1  |
|   |   |1  |   |   |   |   |   |
|0  |   |   |   |   |   |   |   |
|   |   |   |   |   |   |   |   |

**Solution**  
|   |   |   |   |   |   |   |   |
|---|---|---|---|---|---|---|---|
|0  |1  |0  |1  |1  |0  |1  |0  |
|0  |0  |1  |0  |1  |0  |1  |1  |
|1  |0  |0  |1  |0  |1  |0  |1  |
|1  |1  |0  |0  |1  |0  |1  |0  |
|0  |1  |1  |0  |0  |1  |0  |1  |
|1  |0  |1  |1  |0  |0  |1  |0  |
|0  |1  |0  |0  |1  |1  |0  |1  |
|1  |0  |1  |1  |0  |1  |0  |0  |

## Impelemtation
For solving this constraint satisfaction problem (binary) integer linear programming is applied. As this is a feasibility problem, the objective function of the optimization problem was set to 0. In this implementation, the fourth constraint (uniqueness) is not taken into account by the solver. Therefore, new solutions are sought until they are either valid or the problem can no longer be solved. The `solve_all` method returns all solutions for the problem. If the puzzle cannot be solved unambiguously, the length of the return array is greater than 0.