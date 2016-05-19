import random

# reference: http://everything2.com/title/Boggle
# The 16 dice have the following 96 letters on their faces:

#  1. A E A N E G      9. W N G E E H
#  2. A H S P C O     10. L N H N R Z
#  3. A S P F F K     11. T S T I Y D
#  4. O B J O A B     12. O W T O A T
#  5. I O T M U C     13. E R T T Y L
#  6. R Y V D E L     14. T O E S S I
#  7. L R E I X D     15. T E R W H V
#  8. E I U N E S     16. N U I H M Qu


# build a list of lists, each on representing a dice:
def board():
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

    board=[]
    i = 0

    for row in range(4):
        board.append([])
        for column in range(4):
            board[row].append(faces[i])
            i += 1
    return board
        




