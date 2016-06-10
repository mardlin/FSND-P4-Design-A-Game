# Boggle API

## create_user

Use this endpoint to create the users (or players) who will play boggle against each other. If an email address is included, it will be used to remind players when it is their turn to play.

#### Request:
**POST /create_user**  
Parameters: 
    - user_name
    - email (optional)
#### Response:
When a user has been succesfully created, this endpoint will respond with a success message like "User {{name}} created"


## new_game
Creates and responds with a new game. Each game has a randomly generated board, two players, and a customizable number of turns allowed. 

#### Request: 
**POST /new_game**
Parameters: 
    - user1_name 
    - user2_name 
    - turns     *game play will be limited to the number of turns chosen*
    Note: user1_name and user2_name must be unique, and match existing players
#### Response:
The response is a Game Form representation of the new game:
```json
    {
     "board": "R S P L  | E I B T  | U L Z A  | E S T I  | ",
     "game_over": false,
     "message": "Good luck playing Boggle!",
     "turns_remaining": "4",
     "urlsafe_key": "ag9kZXZ-Ym9nZ2xlLWdhbWVyEQsSBEdhbWUYgICAgICAoAgM",
     "user1_is_next": true,
     "user1_name": "john",
     "user1_points": "0",
     "user2_name": "sarah",
     "user2_points": "0",
     "words_found": "[]"
    }
```
I recommend that players manually copy/past the board into a text editor for easy access, and reformat it for readability:
```
R S P L 
E I B T 
U L Z A 
E S T I 
```

## make_move

Using this endpoint, a user submits a "guess" for a word found on the board. The guess is checked for validity, and the game state updated accordingly. Returns a game state with message.

#### The following are required in order to submit a guess
- The game is not over
- The user is a player in this game, and has the next turn

If the requirements are not met, the response will contain an error message, and the game state will not be modified. 

#### The following are required in order to successfuly find a word using this endpoint:
- The word is english
    - The [Merriam-Webster Dictionary API](http://www.dictionaryapi.com) is used for reference
- The word can be found on the board, ie:
    + Each of the letters in the word is present on the board, and the word can be spelled by moving in a **path** from one letter to the next in order. 
    + A path is valid if each letter is adjacent to the previous, either above/below, to the side, or diagonally 
    + No letter on the board can be used twice
- The guess is not case-sensitive, ie. "WORD", "word", and "wORd" will all be treated equally.

##### Points are awarded for a valid word based on the following scheme: 

Word length   |       Points
----------------------------
less than 3   |       0    
4 letters     |       1
5             |       2   
6             |       3
7             |       5
more than 7   |       11

#### Request:
**PUT /make_move/{urlsafe_game_key}**
Parameters: 
    - user_name
    - guess

*Example request:*
```json
    {
      "guess": "lisp",
      "user_name": "john"
    }
```

#### Response:
The response will be an updated Game Form for this game. 

```json
    {
     "board": "R QU P L  | E I B T  | U L Z A  | E S T I  | ",
     "game_over": false,
     "message": "Correct! 1 points for the word \"LISP\"",
     "turns_remaining": "3",
     "urlsafe_key": "ag9kZXZ-Ym9nZ2xlLWdhbWVyEQsSBEdhbWUYgICAgICAoAgM",
     "user1_is_next": false,
     "user1_name": "john",
     "user1_points": "1",
     "user2_name": "sarah",
     "user2_points": "0",
     "words_found": "[\"LISP\"]"
    }
```

##### Notice what has been updated:
`turns_remaining` has decremented by 1
`user1_is_next` is toggled to `false`
`user1_points` is now 1
"LISP" has been appended to the `words_found` list


## get_game
Returns the current game state of a game

#### Request:
**GET /get_game/{urlsafe_game_key}**

done.

## get_user_games
Returns all of a user's games. 
You may want to modify the `User` and `Game` models to simplify this type
    of query. **Hint:** it might make sense for each game to be a `descendant` 
    of a `User`.

#### Request:
**GET /user/{urlsafe_game_key}**

done.

    
## cancel_game

Allows a user to cancel a game in progress. The user who cancels a game forfeits, and the other user becomes the winner. 

### Request:
**PUT /cancel_game**

    
## get_user_rankings

Returns a list of users ranked by win_percentage, with ties broken by totals wins.

### Request:
**GET /user_rankings**

---
 
## get_game_history

Returns the history of moves for a game.

### Request:
**GET games/{urlsafe_game_key}/history**

---

## get_average_turns
Returns the cached average number of turns remaining across all games. 

### Request:
**GET /games/average_turns**
