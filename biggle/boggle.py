"""boggle.py - This file contains the functions which generate a
boggle board, and determine if the word exists on the board."""

import random


# build a list of lists, each on representing a dice:
def board():
    """Returns a 4x4 list of single character strings.
    """

    # The 16 die used in Boggle have the following 96 letters on their faces.
    # reference: http://everything2.com/title/Boggle

    die = [
        ["A", "E", "A", "N", "E", "G"],  ["W", "N", "G", "E", "E", "H"],
        ["A", "H", "S", "P", "C", "O"],  ["L", "N", "H", "N", "R", "Z"],
        ["A", "S", "P", "F", "F", "K"],  ["T", "S", "T", "I", "Y", "D"],
        ["O", "B", "J", "O", "A", "B"],  ["O", "W", "T", "O", "A", "T"],
        ["I", "O", "T", "M", "U", "C"],  ["E", "R", "T", "T", "Y", "L"],
        ["R", "Y", "V", "D", "E", "L"],  ["T", "O", "E", "S", "S", "I"],
        ["L", "R", "E", "I", "X", "D"],  ["T", "E", "R", "W", "H", "V"],
        ["E", "I", "U", "N", "E", "S"],  ["N", "U", "I", "H", "M", "QU"]
    ]

    # first we will build a list in which each element is one face of the die
    # from the 16x6 list of lists above
    faces = []
    for i in range(16):
        # choose a random die
        dice = random.choice(die)
        # choose a random face from that die
        face = random.choice(dice)
        # take that die out of the list
        die.remove(dice)
        # Add the face to the die that will go on the board.
        faces.append(face)

    # Next break the 16 elements in the faces list into a 4x4 list
    # This will represent the randomly generated board used to play the game.
    board = []
    i = 0
    for row in range(4):
        board.append([])
        for column in range(4):
            board[row].append(faces[i])
            i += 1
    return board


def find_in_row(letter, row):
    """Return a list of all the indices of a letter in a list.
        Args:
            letter: a string
            row: a list
    """
    locations = []
    for i in range(len(row)):
        if row[i] == letter:
            locations.append(i)
    return locations


def find_letter(letter, board):
    """Returns a list of coordinates for a letter located in a board.
    Args:
        letter: a string
        board:  a 4x4 list of single character strings.
    """
    coords = []
    # iterate over rows
    for y in range(len(board)):
        # find locations of letter
        indices = find_in_row(letter, board[y])
        for x in indices:
            coords.append((x, y,))
    return coords


def find_letters(word, board):
    """This function is used models.Game.check_word(), as an input for
    the all_paths() function defined below.

    Returns a dict, with coordinates of each letter in the word.

    Args:
        word: a string
        board: a 4x4 list of strings
    """
    path = dict()
    for letter in word:
        loc = find_letter(letter, board)
        path[letter] = loc
    return path


def is_adjacent(c1, c2):
    """Determines if two coordinates are adjacent.
    Args:
        c1, c2: tuples of length 2.
    Returns: Boolean value
    """
    if c1 == c2:
        return False
    vector = (c2[0]-c1[0], c2[1]-c1[1])
    # neither coord value should vary by more than 1
    for v in vector:
        if (v < -1 or v > 1):
            return False
    return True


def path_test(path):
    """Determines if a list of coordinates can be traversed without requiring
    any non-adjacent moves.
    Args:
        path: a list of 2-dim coordinate tuples
    Returns: Boolean value
    """
    for index, coord in enumerate(path):
        if index >= len(path)-1:
            # We've reached the end of the path without issue
            return True
        # check that the path doesn't cross itself (no repeated coords)
        if coord in path[index+1:]:
            return False
        next_coord = path[index+1]
        if not is_adjacent(coord, next_coord):
            return False


def all_paths(word, word_coords):
    """Given a word, and the coordinates of the letters in that word in a
    board, find all possible paths through those coordinates, and then run
    path_test() on each. If any path is valid, return True.

    This function is used in models.Game.check_word()

    Args:
        word: the word we are checking for
        word_coords: the dict of letters and their coordinates.
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
        if path_test(path):
            return True
    return False


def word_points(word):
    """Return the number of points earned by finding a word.
    The points scheme is taken from https://en.wikipedia.org/wiki/Boggle

    This function is used in the make_move endpoint.
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
