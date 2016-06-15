
This boggle api was created for Project 4 of the [Udacity Fullstack Nanodegree](https://www.udacity.com/degrees/full-stack-web-developer-nanodegree--nd004). The API is a significant extension of the basic "[Guess a number](https://github.com/udacity/FSND-P4-Design-A-Game/tree/master/Skeleton%20Project%20Guess-a-Number)" game provided for the project, and runs on Google's app engine. 

## Design considerations

### Modeling

Several properties were added to the pre-existing User and Game models. 

For the User model, the following properties were added:
- `games` stores a list of Game entity keys
- `wins` and `losses` are both integer properties, which are updated when a game has completed

The Game model required much more modification. The following is a list of properties added, and where applicable a short comment about the considerations and impacts of these properties:
- `board` was added to store the randomly generated board associated with each game. 
    + Although not included in the models, there is a significant amount of game logic stored in the the `boggle.py` file. This logic only appears in the model in the `Game.check_word` and `Game.new_game` instance methods. Separating the logic makes the code for both the models and the game logic more readable and maintainable. 
- `user` was replaced with `user1` and `user2`, which also required the addition of `user1_is_next` (Boolean), and `user1_points` and `user2_points`
    + Extending from a single-player to two-player game required a significant amount of code to track the status of the game, and the players performance within it. In hindsight, I would prefer to have made a more flexible "multiplayer" game structure. Instead of a unique property for each player this could have been done with lists. That is:
        * a `users` list instead of `user1` and `user2`
        * a `next_user` integer value pointing to which element of the `users` list held the play who had the next turn
        * a `users_points` list instead of `user1_points` and `user2_points`
    + This approach would have created cleaner code, as well as providing a feature that would likely be requested by real players.

### Game Logic

The game logic is stored in the `boggle.py` file. There are three main purposes fulfilled by this logic:

#### 1. Generating the game board

This logic was straight forward to create. In order to most closely mimic the actual game play, I researched and found the actual letters on each of the 16 die used in the most popular version of the game. Then it was a fairly simple application of list methods and random number generation to randomly one face (or letter) from each die for each of the 16 nodes in the 4x4 grid that makes up the board. 

#### 2. Checking word validity

The task of taking a given word, and determining 'if the word is found on the board' according to the rules of boggle was more challenging. I broke up the task into many smaller functions to make it more manageable, and each function `find_in_row` through `all_paths` builds on the previous. There are possibly too many functions, taking on too small parts of the process, but it works. 


#### 3. Assigning point for a valid word

This is a very simple function which assigns a number of points based to a word based on its length
according to the standard rules of boggle. 

### General reflections 

#### On perfectionism

I was surprised at the time required for many of the tasks. Partially this is a function of my own perfectionism, and I'm equally proud of the parts I spent the time to get "just right", as the parts I was able to leave as "good enough" in order to move on.  

#### On testing

Having access to the App Engine API Explorer interface made it much easier to test what I was building. At the same time I came to understand the time required to test all of the possible cases in even a fairly simple application. I can get a sense of the power of "test driven development", and would like to explore the practice of TDD further in future projects. 