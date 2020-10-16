import numpy as np
from config import BOARD_ROWS, BOARD_COLS, opp, HU_PLAYER, AI_PLAYER, EMPTY_SPOT


class Board:
    def __init__(self, brd=None):
        self.board = np.zeros([BOARD_ROWS, BOARD_COLS], dtype=int)
        if brd is not None: self.board = np.array(brd)  # self.board=brd

    def __copy__(self):
        return Board(self.board.copy())

    def check_for_win(self, i, j, player):
        """given insertion at (i,j) checks for a win"""
        cou = 0
        row_check = self.board[:, j]  # get [all the rows , in col j] = col j in a list
        col_check = self.board[i, :]
        diag1_check, diag2_check = [self.board[i, j]], [self.board[i, j]]
        for p in range(1, max(BOARD_ROWS, BOARD_COLS)):
            if i + p < BOARD_ROWS and j + p < BOARD_COLS: diag1_check += [self.board[i + p, j + p]]
            if i - p >= 0 and j - p >= 0: diag1_check = [self.board[i - p, j - p]] + diag1_check
            if i + p < BOARD_ROWS and j - p >= 0: diag2_check = [self.board[i + p, j - p]] + diag2_check
            if i - p >= 0 and j + p < BOARD_COLS: diag2_check += [self.board[i - p, j + p]]

        return Board.check_for_seq(row_check, player) or Board.check_for_seq(col_check, player) or \
               Board.check_for_seq(diag1_check, player) or Board.check_for_seq(diag2_check, player)

    def get_avail_loc(self, col):
        for i in range(BOARD_ROWS):
            if self.board[i, col] == 0:
                return i  # available
        return -1

    def check_full(self):
        return np.count_nonzero(self.board) == BOARD_ROWS * BOARD_COLS

    def make_move(self, col, player):
        """returns status in string and insertion place
            status will be on of - 'move_won', 'full_table', 'moved_succ', 'error_col_is_full' """
        ind = self.get_avail_loc(col)
        if ind == -1: return "error_col_is_full",

        self.board[ind, col] = player  # plays
        if self.check_for_win(ind, col, player): return "move_won", (ind, col)
        if self.check_full(): return "full_table", (ind, col)  # moved succ and table now full
        return "moved_succ", (ind, col)

    def eval_curr_board(self, player):
        """scores the current board position relatively to given player,
            essential for minimax algorithm"""
        score = 0

        # center scoring:
        score += (list(self.board[:, BOARD_COLS // 2])).count(player) * 3

        # rows scoring:
        for r in range(BOARD_ROWS):
            row_lst = self.board[r, :]
            for w in range(BOARD_COLS - 3):
                score += Board.score_window(player, row_lst[w:w + 4])

        # cols scoring:
        for c in range(BOARD_COLS):
            col_lst = self.board[:, c]
            for w in range(BOARD_ROWS - 3):
                score += Board.score_window(player, col_lst[w:w + 4])

        # diag scoring (main diags):
        for r in range(BOARD_ROWS - 3):
            for c in range(BOARD_COLS - 3):
                window = [self.board[r + i, c + i] for i in range(4)]  # main diag
                score += Board.score_window(player, window)
                window = [self.board[r + 3 - i][c + i] for i in range(4)]  # secondary diag
                score += Board.score_window(player, window)

        return score

    @staticmethod
    def score_window(player, window):
        """scores given 4-elements-size-window, assuming its not game-over-case"""
        wind_score = 0
        window = list(window)
        player_count, opp_count, empty_count = window.count(player), window.count(opp(player)), window.count(EMPTY_SPOT)

        # if there is 4 in the window - we would be in a game over situation. otherwise we'll score:

        if player_count == 3 and empty_count == 1:
            wind_score += 5
        elif player_count == 2 and empty_count == 2:
            wind_score += 2

        elif opp_count == 3 and empty_count == 1:
            wind_score -= 5
        elif opp_count == 2 and empty_count == 2:
            wind_score -= 2

        return wind_score

    @staticmethod
    def check_for_seq(lst, pivot, seq_len=4):
        cou = 0
        for i in lst:
            if i == pivot:
                cou += 1
                if cou == seq_len:
                    return True
            else:
                cou = 0
        return False

    def __str__(self):
        return np.flip(self.board, 0).__str__()
        # return self.board.__str__()
        # return self.board.transpose()[2].__str__()
