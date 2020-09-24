import math
import sys

import numpy as np
import pygame
from GUI_API import GUIApp

# DEFAULT VALUES (TO BE REDEFINED BY USER IN MAIN)
BOARD_ROWS, BOARD_COLS = 6, 7
SQUARE_SIZE = 80  # pixels of element in matrix
SQUARE_SIZE_DICT = {
    'XL': 90, 'LG': 80, 'MD': 70, 'SM': 60
}
DEPTH_OF_AI = 5
DEPTH_OF_AI_DICT = {
    '3': 3, '4': 4, '5': 5, '6': 6, '7': 7
}

WIDTH, HEIGHT = BOARD_COLS * SQUARE_SIZE, (BOARD_ROWS + 2) * SQUARE_SIZE

# CONSTANTS:
ICON = "icon.png"
CAPTION = ""
B_COLOR = (0, 153, 255)
EMP_COLOR = (0, 0, 51)
GREY = (192, 192, 192)
P_COLOR = ((51, 204, 51), (255, 51, 0), (0, 153, 0), (204, 0, 0))
BLACK = (0, 0, 0)
TEXT_COLOR = (255, 255, 102)

HU_PLAYER = 1
AI_PLAYER = 2
EMPTY_SPOT = 0


# player1 [HUMAN], player2 [AI]= =: 1,2, EMPTY=0

# HELPERS 'static' METHODS:
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


opp = lambda p: p % 2 + 1  # returns the opponent id


# scores given 4-grids-size-window, assuming its not game-over-case
def score_window(player, window):
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


class Board:
    def __init__(self, brd=None):
        self.board = np.zeros([BOARD_ROWS, BOARD_COLS], dtype=int)
        if brd is not None: self.board = np.array(brd)  # self.board=brd

    def __copy__(self):
        return Board(self.board.copy())

    # given insertion at (i,j) checks for a win
    def check_for_win(self, i, j, player):
        cou = 0
        row_check = self.board[:, j]  # get [all the rows , in col j] = col j in a list
        col_check = self.board[i, :]
        diag1_check, diag2_check = [self.board[i, j]], [self.board[i, j]]
        for p in range(1, max(BOARD_ROWS, BOARD_COLS)):
            if i + p < BOARD_ROWS and j + p < BOARD_COLS: diag1_check += [self.board[i + p, j + p]]
            if i - p >= 0 and j - p >= 0: diag1_check = [self.board[i - p, j - p]] + diag1_check
            if i + p < BOARD_ROWS and j - p >= 0: diag2_check = [self.board[i + p, j - p]] + diag2_check
            if i - p >= 0 and j + p < BOARD_COLS: diag2_check += [self.board[i - p, j + p]]
        # print(diag2_check)
        return check_for_seq(row_check, player) or check_for_seq(col_check, player) or \
               check_for_seq(diag1_check, player) or check_for_seq(diag2_check, player)

    def get_avail_loc(self, col):
        for i in range(BOARD_ROWS):
            if self.board[i, col] == 0:
                return i  # available
        return -1

    def check_full(self):
        return np.count_nonzero(self.board) == BOARD_ROWS * BOARD_COLS

    # returns status in string and insertion place
    def make_move(self, col, player):
        ind = self.get_avail_loc(col)
        if ind == -1: return "error_col_is_full",

        self.board[ind, col] = player  # plays
        if self.check_for_win(ind, col, player): return "move_won", (ind, col)
        if self.check_full(): return "full_table", (ind, col)  # moved succ and table now full
        return "moved_succ", (ind, col)

    # scores the current board position relatively to given player
    def eval_curr_board(self, player):
        score = 0

        # center scoring:
        score += (list(self.board[:, BOARD_COLS // 2])).count(player) * 3

        # rows scoring:
        for r in range(BOARD_ROWS):
            row_lst = self.board[r, :]
            for w in range(BOARD_COLS - 3):
                score += score_window(player, row_lst[w:w + 4])

        # cols scoring:
        for c in range(BOARD_COLS):
            col_lst = self.board[:, c]
            for w in range(BOARD_ROWS - 3):
                score += score_window(player, col_lst[w:w + 4])

        # diag scoring (main diags):
        for r in range(BOARD_ROWS - 3):
            for c in range(BOARD_COLS - 3):
                window = [self.board[r + i, c + i] for i in range(4)]  # main diag
                score += score_window(player, window)
                window = [self.board[r + 3 - i][c + i] for i in range(4)]  # secondary diag
                score += score_window(player, window)

        return score

    def __str__(self):
        return np.flip(self.board, 0).__str__()
        # return self.board.__str__()
        # return self.board.transpose()[2].__str__()


# minimax implementation:
# board from type Board, assumes board was checked after last move and legit
def minimax(board, depth, maximizing_player=True, alpha=-math.inf, beta=math.inf):
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


# py game:
def init_board(SCREEN, brd=None):
    for r in range(2, BOARD_ROWS + 2):
        for c in range(BOARD_COLS):
            pygame.draw.rect(SCREEN, B_COLOR, [c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE])
            pygame.draw.circle(SCREEN, EMP_COLOR,
                               [(c * SQUARE_SIZE) + SQUARE_SIZE // 2, (r * SQUARE_SIZE) + SQUARE_SIZE // 2],
                               int(SQUARE_SIZE / 2.3))

    pygame.draw.rect(SCREEN, EMP_COLOR, [0, 1 * SQUARE_SIZE, WIDTH, SQUARE_SIZE])
    pygame.draw.rect(SCREEN, B_COLOR, [0, 1 * SQUARE_SIZE, WIDTH, SQUARE_SIZE], 10)
    pygame.display.update()


def draw_move(SCREEN, col, row, player, curr_move=False):
    pygame.draw.circle(SCREEN, P_COLOR[player - 1],
                       [(col * SQUARE_SIZE) + SQUARE_SIZE // 2,
                        ((BOARD_ROWS - row + 1) * SQUARE_SIZE) + SQUARE_SIZE // 2],
                       int(SQUARE_SIZE / 2.3))
    pygame.draw.circle(SCREEN, P_COLOR[player + 1],
                       [(col * SQUARE_SIZE) + SQUARE_SIZE // 2,
                        ((BOARD_ROWS - row + 1) * SQUARE_SIZE) + SQUARE_SIZE // 2],
                       int(SQUARE_SIZE / 4))
    if curr_move: pygame.draw.circle(SCREEN, TEXT_COLOR,
                                     [(col * SQUARE_SIZE) + SQUARE_SIZE // 2,
                                      ((BOARD_ROWS - row + 1) * SQUARE_SIZE) + SQUARE_SIZE // 2],
                                     int(SQUARE_SIZE / 4))
    pygame.display.update()


def draw_motion(SCREEN, pos, player):
    pygame.draw.rect(SCREEN, EMP_COLOR, [0, 1 * SQUARE_SIZE, WIDTH, SQUARE_SIZE])
    pygame.draw.rect(SCREEN, B_COLOR, [0, 1 * SQUARE_SIZE, WIDTH, SQUARE_SIZE], int(0.1 * SQUARE_SIZE))
    pygame.draw.circle(SCREEN, P_COLOR[player - 1], [pos[0], (int)(1.5 * SQUARE_SIZE)], SQUARE_SIZE // 2)
    pygame.display.update()


def draw_text(SCREEN, text, size=int(0.9 * SQUARE_SIZE), coor=(WIDTH // 2, HEIGHT // 2), font_name="Comic Sans MS",
              bold=True, border=False, color=TEXT_COLOR, border_color=(0, 0, 0)):
    if border:
        draw_text(SCREEN, text, size=int(size * 1.023), coor=coor, color=border_color, font_name=font_name)
    font = pygame.font.SysFont(font_name, size, bold)
    mytext = font.render(text, True, color)
    rect = mytext.get_rect()
    rect.center = coor  # puts text in coor center
    SCREEN.blit(mytext, rect)
    pygame.display.update()

    # SCREEN.blit(mytext, (x,y)) #regular text


def draw_status(SCREEN, player, turns):
    # Status: Player X plays
    pygame.draw.rect(SCREEN, BLACK, [int(0.6 * WIDTH), 0, int(0.4 * WIDTH), int(0.9 * SQUARE_SIZE)])
    draw_text(SCREEN, "Player " + str(player) + "'s Move", size=int(0.25 * SQUARE_SIZE),
              coor=(int(0.8 * WIDTH), int(0.25 * SQUARE_SIZE)), bold=False)
    draw_text(SCREEN, "Turns: " + str(turns), size=int(0.25 * SQUARE_SIZE),
              coor=(int(0.8 * WIDTH), int(0.6 * SQUARE_SIZE)), bold=False)


def main(square_size=SQUARE_SIZE, depth_of_ai=DEPTH_OF_AI):
    # define global variables:
    global SQUARE_SIZE, DEPTH_OF_AI, WIDTH, HEIGHT
    SQUARE_SIZE = square_size
    DEPTH_OF_AI = depth_of_ai
    print(SQUARE_SIZE,DEPTH_OF_AI)
    WIDTH, HEIGHT = BOARD_COLS * SQUARE_SIZE, (BOARD_ROWS + 2) * SQUARE_SIZE

    # vars setup
    brd = Board()
    player = HU_PLAYER  # human begins
    cou = 0
    gameover = ""  # will contain the reason for exit
    last_move_drawn = None
    # pygame setup:
    pygame.init()
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))  # (51,153,255)
    draw_text(SCREEN, "Connect-4", size=int(0.6 * SQUARE_SIZE), coor=(int(WIDTH * 0.3), int(HEIGHT * 0.05)),
              color=(0, 220, 255), border=True, border_color=(200, 0, 0))
    pygame.display.set_caption("Matan's Connect-4")
    gameIcon = pygame.image.load(ICON)
    pygame.display.set_icon(gameIcon)
    draw_status(SCREEN, player, cou)
    init_board(SCREEN)

    # gameloop, breaks when games over
    while not gameover:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # exit
                sys.exit()

            if event.type == pygame.MOUSEMOTION:  # moved element
                pos = event.pos
                draw_motion(SCREEN, pos, player)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # make move
                pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
                pos = event.pos
                chosen_col = pos[0] // SQUARE_SIZE
                res = brd.make_move(chosen_col, player)
                print(res)  # move's console logging

                if res[0] == "error_col_is_full":
                    pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)
                    continue  # col not relevant
                # else: was was inserted to board
                cou += 1
                draw_move(SCREEN, res[1][1], res[1][0], player)
                draw_status(SCREEN, player, cou)

                if res[0] == "full_table" or res[0] == "move_won":
                    gameover = res[0]
                else:  # moved_succ
                    player = opp(player)
                    draw_motion(SCREEN, pos, player)
                    draw_status(SCREEN, player, cou)

                    # computer goes here:
                    # draw thinking
                    draw_text(SCREEN, "Thinking!", size=int(0.6 * SQUARE_SIZE), coor=(WIDTH // 2, (int)(HEIGHT * 0.18)))
                    ai_col_choice = minimax(brd, DEPTH_OF_AI)[0]
                    res = brd.make_move(ai_col_choice, AI_PLAYER)
                    print(res)  # move's console logging

                    cou += 1
                    if last_move_drawn is not None: draw_move(SCREEN, last_move_drawn[1], last_move_drawn[0], player,
                                                              False)
                    draw_move(SCREEN, res[1][1], res[1][0], player, True)
                    last_move_drawn = res[1]
                    draw_status(SCREEN, player, cou)

                    if res[0] == "full_table" or res[0] == "move_won":
                        gameover = res[0]
                        draw_motion(SCREEN, pos, player)

                    else:  # moved_succ
                        player = opp(player)
                        draw_motion(SCREEN, pos, player)
                        draw_status(SCREEN, player, cou)

                pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)

        if gameover:  # last words
            if gameover == "full_table":
                draw_text(SCREEN, "DRAW!")
            if gameover == "move_won":
                if player == AI_PLAYER:
                    draw_text(SCREEN, "AI Wins!", border=True)
                else:
                    draw_text(SCREEN, "SENSATION! Human Wins!", size=int(0.78 * SQUARE_SIZE), border=True)

            draw_text(SCREEN, "Click For Another Game", size=int(0.4 * SQUARE_SIZE),
                      coor=(WIDTH // 2, int(HEIGHT * 0.6)), border=True)

            while True:  # pauses game, waiting to exit
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:  # exit
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # make move
                        main(SQUARE_SIZE,DEPTH_OF_AI)


def settingsPopup():
    settings = GUIApp(main, title="Game Settings",width=600)
    settings.setField('square_size', 'combobox', label='Screen Size', values=SQUARE_SIZE_DICT,default='LG')
    settings.setField('depth_of_ai', 'combobox', label='Depth of AI', values=DEPTH_OF_AI_DICT,default='5',
                      desc='The DEEPER you choose - the HARDER it gets'
                           '\n (note this also slow computation time)')
    settings.run()
    # choice :


settingsPopup()


# CLI game
def console_game():
    player = False
    bg = Board()
    while True:
        print(bg)
        print("-------------------------------")
        col = input("Player: " + str(int(player) + 1) + ", Choose a col from 0-6:  ")
        msg = bg.make_move(int(col), (int(player) + 1))
        print("-----> ", msg)
        if msg[0] != "error_col_is_full": player = not player
        if msg[0] == "move_won": break
