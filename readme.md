## Chess

Chess with AI in Python. Chess elements modified from Will Schwarzer and Tony Bouza's final intro CS project. AI done by Will Schwarzer and Blake Johnson.

### Dependencies:
pygame
numpy
torch

All of which are already installed on Carleton machines (both Mac and Windows).


## Modified MCTS vs MCTS vs Minimax

Chess is a game with a lot of possible states. For this makes random rollouts all the way to the end for MCTS in chess take a really long time.
To speed this up, we took 2 different approaches. One approach is heuristic based rollouts. This means that instead of a random move, the AI will simply take the best move of a heuristic. This makes it so that rollouts finish much more quickly.
Another approach we took was limiting the depth of the rollouts, and then using the heuristic from that point. This allows the rollouts to still have that completely random factor which is often useful for exploring all possibilities, but stops it from going so far as to making pointless strange moves 300 moves into a rollout.

We weren't sure if removing the randomness of the rollouts caused the AI to technically be less than optimal. However, it definitely made the AI a lot faster. Even still, it was never as fast as minimax. 

Almost every setting that can be modified for these AIs is modifiable through arguments. We used argparse to take in args, so you can run 
```$ python3 chess.py --help``` to see all of the options. I'll summarize some of them here.

```--player1 --player2``` are white and black, respectively, and default to human and minimax.

```--mcts-depth, --minimax-depth, --mcts-rollouts``` all control those respective numbers. If you have 2 minimax or 2 mcts, you can input multiple values to have asymmetric AIs.

```--variant``` you can play horde chess. Both the AIs should work with this too. Definitely minimax does.

```--input-file, --output-file``` MCTS can store its tree and load it for another session through the pickle module. It saves and loads files in the saves directory.

```--display, --wait-between``` whether or not to display a game between 2 AIs, and whether to wait on a checkmate boardstate for a click.



