## Chess
[GITHUB LINK](https://github.com/willschwarzer/Chess/)
Chess with AI in Python. By Will Schwarzer and Blake Johnson. Originally intended for comparing alpha-beta search with MCTS, but has human support for just playing chess.

### Dependencies
PyGame and SciPy

### Sample Usage:
```$ python chess.py --player1 human --player2 minimax --num-games 3```

```$ python chess.py --player1 mcts --player2 mcts --mcts-rollouts 50 100 --heuristic-simulation True False ```

```$ python chess.py --variant horde```

## Modified MCTS vs MCTS vs Minimax

Chess is a game with a lot of possible states. For this reason, MCTS rollouts to the end may take a lot of time - besides checkmate or stalemate, the only possible end conditions are threefold repetition and the 50-move rule, which can take many hundreds of moves to take effect, especially if the players are moving randomly. Furthermore, chess is a fickle game: often there is only one reasonable move to win a game or continue the game without losing immediately (for example, recapturing a piece, or moving a piece to safety), and so random rollouts will give a *severely* distorted view of either player's actual chances from a certain board.
To solve these problems, we took 2 different approaches. One approach is heuristic based rollouts. This means that while rolling out to the end, instead of using a random move, the MCTS AI will simply take the move that maximizes a heuristic (in this case, the same heuristic that we used for our alpha-beta program). This serves two purposes: one is that a rollout all the way to the end of a game will finish much more quickly, as the AI will at least try to capture pieces when it can, increase its pieces mobility, and achieve the other goals laid out in the heuristic. The other purpose is that the moves will likely represent more reasonable play, and so will give a more accurate prediction of a player's chances from a certain state.
Another approach we took was limiting the depth of the rollouts, and then using the heuristic at that point (similar to minimax). This allows the rollouts to still have the randomness that allows them to explore to a much deeper level than minimax, but stops them from going so far as to making pointless strange moves 300 moves into a rollout. Again, with chess being such a fickle game, moves so far out in a rollout will likely have exceedingly little relationship to the actual quality of the current position.

As a side note, we weren't sure if removing the randomness of the rollouts caused the AI to technically be less than optimal in the long run - that is, perhaps our version of MCTS will not in fact converge to minimax. That said, it did make the AI much faster when exploring to maximum depth, though it was never as fast in this condition as minimax exploring to a reasonable depth (e.g. 3).

## Credit where credit is due
Images for chessboard and pieces from Wikimedia, licensed under Creative Commons 3:
Chess pieces: en:User:Cburnett [CC BY-SA 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)]
Chess board: https://commons.wikimedia.org/wiki/File:ExperimentalChessbaseChessBoard.png (attribution unclear)

