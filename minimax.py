import math
from config import BOARD_COLS, AI_PLAYER, HU_PLAYER
"""
the AI algorithm:
"""

def minimax(board, depth, maximizing_player=True, alpha=-math.inf, beta=math.inf):
    """minimax implementation, with alpha-beta pruning optimization:
       board from type Board, assumes board was checked after last move and is legit
       @:param board: Board instance, represents connect-4 game board
   """

    # terminate recursion: *game-over nodes are dealt with in-place
    if depth == 0:
        # as deep as it can get
        eval = board.eval_curr_board(AI_PLAYER)
        # print(eval) # console logging
        return None, eval

    # continue recursion
    if maximizing_player:
        max_score = -math.inf
        max_col = -1  # random init value, will be updated
        for col in range(BOARD_COLS):
            brd_copy = board.__copy__()
            status = brd_copy.make_move(col, AI_PLAYER)[0]  # simulate AI move
            if status == "error_col_is_full":
                continue
            # terminal cases:
            elif status == "move_won":
                curr_score = 1000 * depth  # the faster the better
            elif status == "full_table":
                curr_score = 0
            # recursive case:
            else:  # status=="moved_succ"
                curr_score = minimax(brd_copy, depth - 1, False, alpha, beta)[1]
            if max_score < curr_score:  # max update
                max_score = curr_score
                max_col = col
            alpha = max(alpha, curr_score)
            if alpha >= beta: break  # alpha-beta pruning
        return max_col, max_score

    else:  # minimizing player:
        min_score = math.inf
        min_col = -1  # random init value, will be updated
        for col in range(BOARD_COLS):
            brd_copy = board.__copy__()
            status = brd_copy.make_move(col, HU_PLAYER)[0]  # simulate HUMAN move
            if status == "error_col_is_full":
                continue
            # terminal cases:
            elif status == "move_won":
                curr_score = -1000 * depth
            elif status == "full_table":
                curr_score = 0
            # recursive case:
            else:  # status=="moved_succ"
                curr_score = minimax(brd_copy, depth - 1, True, alpha, beta)[1]
            if min_score > curr_score:  # update min
                min_score = curr_score
                min_col = col
            beta = min(beta, curr_score)
            if alpha >= beta: break  # alpha-beta pruning

        return min_col, min_score

