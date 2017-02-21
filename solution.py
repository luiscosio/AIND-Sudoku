from collections import defaultdict
from visualize import visualize_assignments

assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def cross(a, b):
    """Given two strings — a and b — will return the list formed by all the possible
    concatenations of a letter s in string a with a letter t in string b.

    Args:
        a: string
        b: string
    Returns:
        List formed by all the possible concatenations of a letter s in string a with a letter t in string b
    """
    return [s+t for s in a for t in b]

def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '123456789' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
    """
    all_digits = '123456789'
    res = dict()
    for i in range(len(grid)):
        if grid[i] == '.':
            assign_value(res, boxes[i], all_digits)
        else:
            assign_value(res, boxes[i], grid[i])
    return res

def display(values):
    """
    Display the sodoku values as a 2-D grid.
    Args:
        The sudoku in dictionary form
    Returns:
        None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def print_dictionary(values) :
    """
    Displays the soduku values as key value.
    Args:
        The sudoku in dictionary form
    Returns:
        None
    """
    for k,v in values.items():
        print(k,v)

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Args:
        Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    """
    Constraint propagation - Iterate eliminate() and only_choice(). If at some point,
    there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Args:
        A sudoku in dictionary form.
    Return:
        The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use eliminate
        values = eliminate(values)
        # Use only_choice
        values = only_choice(values)
        # Use naked_twins
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, try all possible values.
    Args:
        A sudoku in dictionary form.
    Return:
        The resulting sudoku in dictionary form.
    """
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    for value in values[s]:
        new_sudoku = values.copy()
        assign_value(new_sudoku, s, value)
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    nt = []
    for unit in unitlist:
        values2cell = defaultdict(set)
        for cell in unit:
            values2cell[values[cell]].add(cell)
        for (vals, cells) in iter(values2cell.items()):
            if len(vals) == len(cells) and len(vals) == 2:
               nt.append((unit, vals, cells))
    for (unit, vals, cells) in iter(nt):
        for cell in unit:
            if cell not in cells:
                 for v in vals:
                     assign_value(values, cell, values[cell].replace(v, ''))
    return values

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Add diagonals to units
diagonal = True
diagonal_units = [[rows[i]+cols[i] for i in range(len(rows))], [rows[len(rows) - i - 1]+cols[i] for i in range(len(rows))]]
print(diagonal_units)
if diagonal == True:
    unitlist = row_units + column_units + square_units + diagonal_units
else:
    unitlist = row_units + column_units + square_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

if __name__ == '__main__':
    sudoku_grid_diagonal = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(sudoku_grid_diagonal))

    try:
        visualize_assignments(assignments)
    except SystemExit:
        pass
    except:
        print('There was an issue visualizing the solver!')
