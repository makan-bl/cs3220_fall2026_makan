# Treasure Maze - the state space (Lab3 Task)
#
# HOW THE MAZE WAS MODELLED
# The maze picture from the notebook was read as a 15 x 15 grid of blocks
# ('#' = wall, '.' = corridor), see MAZE_GRID below (row 0 = top).
# A node (vertex) is placed at:
#   * the starting point S  (the entrance, bottom-left, arrow pointing in)
#   * the finishing point F (the exit, top-right, arrow pointing out)
#   * every dead end (the Agent must turn around there)
#   * every junction where more than one path can be taken
# Plain corridors and simple corners are NOT nodes - they are the edges.
# Two nodes are connected when a corridor joins them.
#
# mazeData       {node: {neighbour: corridor length in blocks, ...}, ...}  (same format as romaniaData)
# mazeDirections {(A, B): (direction leaving A, direction of travel when arriving at B)}
#                 directions: 'N' (up), 'S' (down), 'E' (right), 'W' (left)
#                 -> used to translate a move into the actions advance / left / right
# mazeLocations  {node: (column, row)} of the node in MAZE_GRID - used to draw the maze graph

START = 'S'
FINISH = 'F'
START_HEADING = 'E'   # the Agent enters the maze moving to the right (East)

# The 4 treasures (name -> emoji)
TREASURES = {
    'Gold': '🪙',          # Pile of Gold
    'Diamond': '🔷',       # Diamond
    'Pizza': '🍕',         # Flyer for 100 Free Pizzas
    'Extra Points': '🎉',  # 20 Extra Points for the CS3220 Final Exam
}

MAZE_GRID = [
    '###############',
    '#..............',
    '#####.#.#.#####',
    '#...#.#.#.#...#',
    '#.#.#.#.#.#.#.#',
    '#.#...#.#...#.#',
    '#.#.###.###.#.#',
    '###.........###',
    '#.#.#######.#.#',
    '#.#....#....#.#',
    '#.#.#######.#.#',
    '#.............#',
    '#######.#######',
    '..............#',
    '###############',
]

mazeData = {'A': {'B': 4},
 'B': {'A': 4, 'C': 2, 'E': 6},
 'C': {'B': 2, 'D': 2, 'K': 6},
 'D': {'C': 2, 'F': 5, 'G': 6},
 'E': {'B': 6, 'H': 7, 'J': 2},
 'F': {'D': 5},
 'G': {'D': 6, 'I': 7, 'L': 2},
 'H': {'E': 7},
 'I': {'G': 7},
 'J': {'E': 2, 'K': 4, 'O': 2},
 'K': {'C': 6, 'J': 4, 'L': 4},
 'L': {'G': 2, 'K': 4, 'R': 2},
 'M': {'T': 5},
 'N': {'V': 5},
 'O': {'J': 2, 'P': 3, 'T': 2},
 'P': {'O': 3},
 'Q': {'R': 3},
 'R': {'L': 2, 'Q': 3, 'V': 2},
 'S': {'W': 7},
 'T': {'M': 5, 'O': 2, 'U': 4},
 'U': {'T': 4, 'V': 4, 'W': 2},
 'V': {'N': 5, 'R': 2, 'U': 4},
 'W': {'S': 7, 'U': 2, 'X': 6},
 'X': {'W': 6}}

mazeDirections = {('A', 'B'): ('E', 'E'),
 ('B', 'A'): ('W', 'W'),
 ('B', 'C'): ('E', 'E'),
 ('B', 'E'): ('S', 'W'),
 ('C', 'B'): ('W', 'W'),
 ('C', 'D'): ('E', 'E'),
 ('C', 'K'): ('S', 'S'),
 ('D', 'C'): ('W', 'W'),
 ('D', 'F'): ('E', 'E'),
 ('D', 'G'): ('S', 'E'),
 ('E', 'B'): ('E', 'N'),
 ('E', 'H'): ('N', 'S'),
 ('E', 'J'): ('S', 'S'),
 ('F', 'D'): ('W', 'W'),
 ('G', 'D'): ('W', 'N'),
 ('G', 'I'): ('N', 'S'),
 ('G', 'L'): ('S', 'S'),
 ('H', 'E'): ('N', 'S'),
 ('I', 'G'): ('N', 'S'),
 ('J', 'E'): ('N', 'N'),
 ('J', 'K'): ('E', 'E'),
 ('J', 'O'): ('S', 'S'),
 ('K', 'C'): ('N', 'N'),
 ('K', 'J'): ('W', 'W'),
 ('K', 'L'): ('E', 'E'),
 ('L', 'G'): ('N', 'N'),
 ('L', 'K'): ('W', 'W'),
 ('L', 'R'): ('S', 'S'),
 ('M', 'T'): ('S', 'E'),
 ('N', 'V'): ('S', 'W'),
 ('O', 'J'): ('N', 'N'),
 ('O', 'P'): ('E', 'E'),
 ('O', 'T'): ('S', 'S'),
 ('P', 'O'): ('W', 'W'),
 ('Q', 'R'): ('E', 'E'),
 ('R', 'L'): ('N', 'N'),
 ('R', 'Q'): ('W', 'W'),
 ('R', 'V'): ('S', 'S'),
 ('S', 'W'): ('E', 'E'),
 ('T', 'M'): ('W', 'N'),
 ('T', 'O'): ('N', 'N'),
 ('T', 'U'): ('E', 'E'),
 ('U', 'T'): ('W', 'W'),
 ('U', 'V'): ('E', 'E'),
 ('U', 'W'): ('S', 'S'),
 ('V', 'N'): ('E', 'N'),
 ('V', 'R'): ('N', 'N'),
 ('V', 'U'): ('W', 'W'),
 ('W', 'S'): ('W', 'W'),
 ('W', 'U'): ('N', 'N'),
 ('W', 'X'): ('E', 'E'),
 ('X', 'W'): ('W', 'W')}

mazeLocations = {'A': (1, 1),
 'B': (5, 1),
 'C': (7, 1),
 'D': (9, 1),
 'E': (3, 5),
 'F': (14, 1),
 'G': (11, 5),
 'H': (1, 6),
 'I': (13, 6),
 'J': (3, 7),
 'K': (7, 7),
 'L': (11, 7),
 'M': (1, 8),
 'N': (13, 8),
 'O': (3, 9),
 'P': (6, 9),
 'Q': (8, 9),
 'R': (11, 9),
 'S': (0, 13),
 'T': (3, 11),
 'U': (7, 11),
 'V': (11, 11),
 'W': (7, 13),
 'X': (13, 13)}
