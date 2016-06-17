# Boggle API

The Boggle API provides a basic framework for a two player Boggle game, and ranking the performance of multiple players across multiple games. 
 
### Get started:

The Boggle API runs on Google App Engine. App Engine's API Explorer interface, allows you to [play the game](https://apis-explorer.appspot.com/apis-explorer/?base=https://boggle-game.appspot.com/_ah/api#p/boggle/v1/) right away:

1. Create two users [here](https://apis-explorer.appspot.com/apis-explorer/?base=https://boggle-game.appspot.com/_ah/api#p/boggle/v1/boggle.create_user) 
2. Create a [new game](https://apis-explorer.appspot.com/apis-explorer/?base=https://boggle-game.appspot.com/_ah/api#p/boggle/v1/boggle.create_user) with those user names.

(Refer to the endpoints documentation below for request and response formats)

### Local setup:

1. Install the [Google App Engine SDK for Python](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python)
2. Run the GoogleAppEngineLauncher. 
3. Go to File > Add existing application 
4. Choose the folder containing this project, with the `app.yaml` file at its top level
5. Run the application
6. Visit `localhost:{PORT}/_ah/api/explorer` in your browser. The value for `PORT` is found in the apps list of GoogleAppEngineLauncher. 
7. The game can be played via the api explorer. 

Refer to the rules and endpoints documentation below for further instructions.

## Rules: 

These are general rules explaining game play for this version of Boggle. 

- Games are limited to two players/users.
- Each game has a randomly generated Board of 16 letters arranged in a 4x4 grid.
- Players take turns submitting a word they have found on the board.
- Longer words are worth more points.
- Refer to the "make_move" endpoint below for criteria for a valid word, and how points are awarded for a word.

## Endpoints: 

### create_user
------

Use this endpoint to create the users (or players) who will play boggle against each other. If an email address is included, it will be used to remind players when it is their turn to play.

#### Request:

`POST /create_user`

##### Parameters: 

- user_name
- email (optional)

#### Response:
When a user has been succesfully created, this endpoint will respond with a success message like "User {{name}} created"


### new_game
------
Creates and responds with a new game. Each game has a randomly generated board, two players, and a customizable number of turns allowed. 

#### Request: 
`POST /new_game`

##### Parameters: 

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

I recommend that players manually copy/paste the board into a text editor for easy access, and reformat it for readability:

```
R S P L 
E I B T 
U L Z A 
E S T I 
```

### make_move
------

Using this endpoint, a user submits a "guess" for a word found on the board. The guess is checked for validity, and the game state updated accordingly. Returns a game state with message.

#### The following are required in order to submit a guess

- The game is not over
- The user is a player in this game, and has the next turn

If the requirements are not met, the response will contain an error message, and the game state will not be modified. 

#### Requirements for a valid word

1. The word is english
    - The [Merriam-Webster Dictionary API](http://www.dictionaryapi.com) is used for reference

2. The word can be "found" on the board. 
  - Each of the letters in the word is present on the board, and the word can be spelled by moving in a **path** from one letter to the next in order.
    + A path is valid if each letter is adjacent to the previous, either above/below, to the side, or diagonally 
    + No letter in a _given position_ can appear twice in a _single word_. 
      * If the letter "R" appears only once, the word "RARE" would *not* be valid. 
      * If the letter "R" appears twice, the word "RARE" could be valid.
    + Letters can be reused in subsequents words
      * If the letter "L" appears only once, the words "TALE" and "LATE" could both be valid.
    + The word has not yet been found
      * This applies even if the word appears twice
- The guess is not case-sensitive, ie. "WORD", "word", and "wORd" will all be treated equally.

#### Examples:

Here's an example board, let's look at some of the words that can and can not be found:
```
  F X I E
  A M L O
  E W B X
  W O T U
```

*Valid words:* 
- BOX 
- MILE
- LIME (MILE and LIME containe the same letters, but that's OK) 
- WOW (The W appears twice) 
- BOW (this could only be found once, even though it can be spelled with either W)

*Invalid words:*

- FAMILY (There's no Y on the board)
- BLOB (The same B is used twice)
- IXAWBUTO (Not an english word)



##### Points are awarded for a valid word based on the following scheme: 

|   *Word length*  |  *Points*  |
|   ---            |    ---     |
|   less than 3    |    0       |    
|   4 letters      |    1       |
|   5              |    2       |   
|   6              |    3       |
|   7              |    5       |
|   more than 7    |    11      |

#### Request:

`PUT /make_move/{urlsafe_game_key}`

##### Parameters: 
- user_name
- guess

**Example request:**
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

- `turns_remaining` has decremented by 1
- `user1_is_next` is toggled to `false`
- `user1_points` is now 1
- `"LISP"` has been appended to the `words_found` list


### get_game
---

Returns the current game state of a game

#### Request:

**GET /get_game/{urlsafe_game_key}**

#### Response: 

The response is a Game Form representation of the game, as seen in *new_game* above. 

## get_user_games
---

Returns all of a user's games. 

#### Request:
**GET /user/{urlsafe_user_key}**

#### Reponse:

The response contains a user object, and a list of Game Form representations of the user's games.

```json
{
"user": {
    "name": "john",
    "urlsafe_key": "ag9kZXZ-Ym9nZ2xlLWdhbWVyEQsSBFVzZXIYgICAgICAgAoM"
    },
"games": [
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
    }, 
    {
    "board": "...."
    }
]}
```

    
## cancel_game
---
Allows a user to cancel a game in progress. The user who cancels a game forfeits, and the other user becomes the winner. 

#### Request:

**PUT /game/{urlsafe_game_key}/cancel**

```json
{
    "user_name": "john"
}
```
    
#### Response: 

The response is a Game Form representation of the cancelled game, including the message indicating that the other user is now the winner. 

## get_user_rankings
---
Returns a list of users ranked by win_percentage, with ties broken by total wins.

#### Request:
**GET /user_rankings**

####

```json
{
 "users": [
  {
   "losses": "1",
   "name": "beethoven",
   "urlsafe_key": "ag9kZXZ-Ym9nZ2xlLWdhbWVyEQsSBFVzZXIYgICAgICAwAgM",
   "win_percentage": 0.9,
   "wins": "9"
  },
  {
   "losses": "3",
   "name": "scooby doo",
   "urlsafe_key": "ag9kZXZ-Ym9nZ2xlLWdhbWVyEQsSBFVzZXIYgICAgICAgAkM",
   "win_percentage": 0.7,
   "wins": "7"
  },
  {
   "losses": "5",
   "name": "gerf",
   "urlsafe_key": "ag9kZXZ-Ym9nZ2xlLWdhbWVyEQsSBFVzZXIYgICAgICAgAoM",
   "win_percentage": 0.5,
   "wins": "5"
  },
  {
   "losses": "8",
   "name": "Claus",
   "urlsafe_key": "ag9kZXZ-Ym9nZ2xlLWdhbWVyEQsSBFVzZXIYgICAgICAgAsM",
   "win_percentage": 0.2,
   "wins": "2"
  }
 ]
}
```
 
## get_game_history
---
Returns the history of moves for a game.

#### Request:
**GET games/{urlsafe_game_key}/history**

#### Response: 


```json
{
 "game": {
  "board": "R QU P L  | E I B T  | U L Z A  | E S T I  | ",
  "game_over": false,
  "message": "Here is the history of this game",
  "turns_remaining": "1",
  "urlsafe_key": "ag9kZXZ-Ym9nZ2xlLWdhbWVyEQsSBEdhbWUYgICAgICAoAgM",
  "user1_is_next": false,
  "user1_name": "john",
  "user1_points": "1",
  "user2_name": "sarah",
  "user2_points": "0",
  "words_found": "[\"BILE\"]"
 },
 "turns": [
  "{\"user\": \"john\", \"message\": \"Sorry! The word \\\"COBBLE\\\" is not in the board.\"}",
  "{\"user\": \"sarah\", \"message\": \"Sorry! \"ULZA\" is not in the english dictionary.\"}",
  "{\"user\": \"john\", \"message\": \"Correct! 1 points for the word \\\"LISP\\\"\"}"
 ]
}
```


## get_average_turns
---
Returns the cached average number of turns remaining across all games. 

#### Request:
**GET /games/average_turns**

#### Response: 

```json
{
 "message": "The average moves remaining is 2.25"
}
```