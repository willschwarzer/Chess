## Chess
[GITHUB LINK](https://github.com/willschwarzer/Chess/)
Chess with AI in Python. Chess elements modified by Will Schwarzer from his and Tony Bouza's final intro CS project (https://github.com/willschwarzer/ChessSnake) - note however that nearly all code was rewritten extensively for this project. AI done by Will Schwarzer and Blake Johnson.

### Dependencies:
pygame and numpy


These are both already installed on Carleton machines (both Mac and Windows).


## Modified MCTS vs MCTS vs Minimax

Chess is a game with a lot of possible states. For this reason, MCTS rollouts to the end may take a lot of time - besides checkmate or stalemate, the only possible end conditions are threefold repetition and the 50-move rule, which can take many hundreds of moves to take effect, especially if the players are moving randomly. Furthermore, chess is a fickle game: often there is only one reasonable move to win a game or continue the game without losing immediately (for example, recapturing a piece, or moving a piece to safety), and so random rollouts will give a *severely* distorted view of either player's actual chances from a certain board.
To solve these problems, we took 2 different approaches. One approach is heuristic based rollouts. This means that while rolling out to the end, instead of using a random move, the MCTS AI will simply take the move that maximizes a heuristic (in this case, the same heuristic that we used for our alpha-beta program). This serves two purposes: one is that a rollout all the way to the end of a game will finish much more quickly, as the AI will at least try to capture pieces when it can, increase its pieces mobility, and achieve the other goals laid out in the heuristic. The other purpose is that the moves will likely represent more reasonable play, and so will give a more accurate prediction of a player's chances from a certain state.
Another approach we took was limiting the depth of the rollouts, and then using the heuristic at that point (similar to minimax). This allows the rollouts to still have the randomness that allows them to explore to a much deeper level than minimax, but stops them from going so far as to making pointless strange moves 300 moves into a rollout. Again, with chess being such a fickle game, moves so far out in a rollout will likely have exceedingly little relationship to the actual quality of the current position.

As a side note, we weren't sure if removing the randomness of the rollouts caused the AI to technically be less than optimal - that is, perhaps our version of MCTS will not in fact converge to minimax in the long run. That said, it did make the AI much faster when exploring to maximum depth, though it was never as fast in this condition as minimax exploring to a reasonable depth (e.g. 3).

Almost every setting that can be modified for these AIs is modifiable through arguments. We used argparse to take in args, so you can run 
```$ python3 chess.py --help``` to see all of the options. I'll summarize some of them here.

```--player1 --player2``` are white and black, respectively, and default to human and minimax.

```--mcts-depth, --minimax-depth, --mcts-rollouts``` all control those respective numbers. If you have 2 minimax or 2 mcts, you can input multiple values to have asymmetric AIs. MCTS depth of 0 will go all the way to the end.

```--variant``` you can play horde chess. Both the AIs should work with this too. Definitely minimax does.

```--input-file, --output-file``` MCTS can store its tree and load it for another session through the pickle module. It saves and loads files in the saves directory.

```--display, --wait-between``` whether or not to display a game between 2 AIs, and whether to wait on a checkmate boardstate for a click.

## Findings

While MCTS was in fact faster with our modifications, it was surprisingly bad against minimax. Minimax itself was pretty good, able to beat me consistently around depth 3, and depth 4 was usually fairly crushing. We weren't able to train mcts much, so hopefully after more training, MCTS would consistently be able to defeat Minimax, as rollouts means MCTS can look much farther into the future.

Additionally, we found MCTS extremely frustrating to code. It would often try and exploit bugs in the game, such as taking 2 moves in a row, or capturing its own pawn en passant in order to break the game and give them an extra king or two (don't ask).
In contrast, being able to code Minimax easily and then having it instantly be able to also play horde without any major issues was incredibly satisfying.
We never got to a point of confidence with MCTS where we asked it to play horde. In theory, it should be able to just fine, but we kept getting problems with it just in normal chess.

Minimax wasn't without its problems either. An early version didn't actually care about checks, but instead just valued its king at an absurdly high number of points. However, the AI found the loophole to this: trading kings. Minimax would sometimes not avoid check, but instead threaten the opponent's king. Technically, it was completely correct, since it would usually pick up a piece in the process, and therefore technically the king trade was valuable.
When we updated our check detection and enabled it for Minimax, this problem completely went away.

Another possibility that we would've liked to explore further are different heuristics. Our algorithms should be able to function with multiple heuristics, but we only had time to implement a basic point-value heuristic which just adds up the conventional chess piece values (and subtracts the opponent's). With more time, we could compare different heuristics and see what works best.

## Data
Here's some code with MCTS playing against itself showing the speed difference with heuristic rollouts. Both versions were doing 20 rollouts with depth 0 (all the way to the end).
```
Hueristic rollouts:   get_move took 12.00 seconds
Random rollouts:      get_move took 11.75 seconds
Hueristic rollouts:   get_move took 10.70 seconds
Random rollouts:      get_move took 13.75 seconds
Hueristic rollouts:   get_move took 9.60 seconds
Random rollouts:      get_move took 15.70 seconds
Hueristic rollouts:   get_move took 7.63 seconds
Random rollouts:      get_move took 14.96 seconds
Hueristic rollouts:   get_move took 7.65 seconds
Random rollouts:      get_move took 16.59 seconds
Hueristic rollouts:   get_move took 10.25 seconds
Random rollouts:      get_move took 19.93 seconds
Hueristic rollouts:   get_move took 10.81 seconds
Random rollouts:      get_move took 21.20 seconds
Hueristic rollouts:   get_move took 11.75 seconds
Random rollouts:      get_move took 27.52 seconds
Hueristic rollouts:   get_move took 9.41 seconds
Random rollouts:      get_move took 22.91 seconds
Hueristic rollouts:   get_move took 10.79 seconds
Random rollouts:      get_move took 28.45 seconds
Hueristic rollouts:   get_move took 10.07 seconds
Random rollouts:      get_move took 26.13 seconds
Hueristic rollouts:   get_move took 11.82 seconds
Random rollouts:      get_move took 24.19 seconds
Hueristic rollouts:   get_move took 11.24 seconds
Random rollouts:      get_move took 26.57 seconds
Hueristic rollouts:   get_move took 11.96 seconds
Random rollouts:      get_move took 31.33 seconds
...
Random rollouts:      get_move took 30.09 seconds
Hueristic rollouts:   get_move took 10.07 seconds
Random rollouts:      get_move took 38.76 seconds
Hueristic rollouts:   get_move took 9.42 seconds
Random rollouts:      get_move took 33.74 seconds
Hueristic rollouts:   get_move took 8.88 seconds
Random rollouts:      get_move took 33.10 seconds
```
As you can see, heuristic rollouts were about 3 times faster than random rollouts, especially in midgame/endgame. So at least we accomplished something!



## Credit where credit is due
Images for chessboard and pieces from Wikimedia, licensed under Creative Commons 3:
Chess pieces: en:User:Cburnett [CC BY-SA 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)]
Chess board: https://commons.wikimedia.org/wiki/File:ExperimentalChessbaseChessBoard.png (attribution unclear)

