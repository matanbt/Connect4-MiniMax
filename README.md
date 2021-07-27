# Connect4 With MiniMax
### Description:
A variation of "4 In a Row" game, that can be player against "AI".

- Implemented with Python using PyGame.
- AI based on Minimax algorithm implementation 
 
### Idea behind the AI
 Basically builds a tree of all possible moves after each step. 
 Each leaf in the tree is given a "score" by a heuristic function (my choice is described briefly in `./dev_notes.txt`), so the "AI" chooses his next move aspiring to maximize this "score".  [More on this [here](https://en.wikipedia.org/wiki/Minimax#Combinatorial_game_theory)]

### Demo:
<img src="https://github.com/matanbt/Connect4-AI/blob/master/img/demo.png" width=400>



