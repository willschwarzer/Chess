## Chess
[GITHUB LINK](https://github.com/willschwarzer/Chess/)
Chess with AI in Python. By Will Schwarzer and Blake Johnson. Originally intended for comparing alpha-beta search with MCTS, but has human support for just playing chess. Includes the extremely fun "horde" variant.

### Dependencies
PyGame and SciPy

### Sample Usage:
```$ python chess.py --player1 human --player2 minimax --num-games 3```

```$ python chess.py --player1 mcts --player2 mcts --mcts-rollouts 50 100 --heuristic-simulation True False ```

```$ python chess.py --variant horde```

## Credit where credit is due
Images for chessboard and pieces from Wikimedia, licensed under Creative Commons 3:
Chess pieces: en:User:Cburnett [CC BY-SA 3.0 (http://creativecommons.org/licenses/by-sa/3.0/)]
Chess board: https://commons.wikimedia.org/wiki/File:ExperimentalChessbaseChessBoard.png (attribution unclear)

