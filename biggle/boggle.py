"""boggle.py - This file contains the functions which generate a
boggle board, and determine if the word exists on the board. 

"""

def _find_in_row(letter, row):
    """
    Return a list of the indices of a letter in a list.
    """
    locations = []
    for i in range(len(row)):
        if row[i] == letter:
            locations.append(i)
    return locations


def _find_letter(letter, board):
    """
    Returns a list of coordinates where a letter is located in a board.
    """
    coords = []
    # iterate over rows
    for y in range(len(board)):
        # find locations of letter
        indices = _find_in_row(letter, board[y])
        for x in indices:
            coords.append((x, y,))
    return coords


def find_letters(word, board):
    """
    Returns a dict, with coordinates of each letter in the word.
    """
    path = dict()
    for letter in word:
        loc = _find_letter(letter, board)
        path[letter] = loc
    return path


def _is_adjacent(c1, c2):
    """Takes two 2-dim coordinate tuples.
    Returns false if they are not adjacent.
    """
    # test for same position
    if c1 == c2:
        return False
    vector = (c2[0]-c1[0], c2[1]-c1[1])
    # neither coord value should vary by more than 1
    for v in vector:
        if (v < -1 or v > 1):
            return False
    return True


def _path_test(path):
    """
    Takes: a list of 2-dim coordinate tuples
    Returns: True iff the path is continous
    """
    for index, coord in enumerate(path):
        # print coord
        if index >= len(path)-1:
            return True
        next_coord = path[index+1]
        # print next_coord
        if not _is_adjacent(coord, next_coord):
            return False


def all_paths(word, word_coords):
    """
    word = the word we are checking for
    word_coords = the dict of letters and their coordinates.
    Returns all permutations of the possible order of those paths.
    """
    options = []
    path_list = []  # We'll build this into a list of lists of tuples
    # Use the word to traverse the dict
    for letter in word:
        # Using the code in list_games.py, create a new function to
        # build an "options list" by counting coords for each word
        options.append(len(word_coords[letter]))
    print options
    # For each item in the options list,
    # create a list of each posible path through the coords
    paths = [[]]
    for letter in word:
        new_paths = []
        for i in range(len(paths)):
            for j in range(len(word_coords[letter])):
                new_paths.append(paths[i]+[word_coords[letter][j]])
        paths = new_paths
    # check each path until one is found valid
    for path in paths:
        print "testing path: %s" % path
        if _path_test(path):
            return True
    return False


def word_points(word):
    """Return the number of points earned by finding a word.
    The points scheme is taken from https://en.wikipedia.org/wiki/Boggle
    """
    l = len(word)
    if l < 3:
        return 0
    elif l < 5:
        return 1
    elif l == 5:
        return 2
    elif l == 6:
        return 3
    elif l == 7:
        return 5
    else:
        return 11
