import sys
import pygame

from GUI_API import FormGUI
from config import *
from board_model import Board
from minimax import minimax
from gui import *

# pygame's GUI game
def gui_game():
    # vars setup
    brd = Board()
    player = HU_PLAYER  # human begins
    cou = 0
    gameover = ""  # will contain the reason for exit
    last_move_drawn = None
    # pygame setup:
    pygame.init()
    SCREEN = pygame.display.set_mode((CFG.WIDTH, CFG.HEIGHT))  # (51,153,255)
    draw_text(SCREEN, "Connect-4", size=int(0.6 * CFG.SQUARE_SIZE), coor=(int(CFG.WIDTH * 0.3), int(CFG.HEIGHT * 0.05)),
              color=(0, 220, 255), border=True, border_color=(200, 0, 0))
    pygame.display.set_caption(CAPTION)
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
                chosen_col = pos[0] // CFG.SQUARE_SIZE
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
                    draw_text(SCREEN, "Thinking!", size=int(0.6 * CFG.SQUARE_SIZE), coor=(CFG.WIDTH // 2, (int)(CFG.HEIGHT * 0.18)))
                    ai_col_choice = minimax(brd, CFG.DEPTH_OF_AI)[0]
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
                    draw_text(SCREEN, "SENSATION! Human Wins!", size=int(0.78 * CFG.SQUARE_SIZE), border=True)

            draw_text(SCREEN, "Click For Another Game", size=int(0.4 * CFG.SQUARE_SIZE),
                      coor=(CFG.WIDTH // 2, int(CFG.HEIGHT * 0.6)), border=True)

            while True:  # pauses game, waiting to exit
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:  # exit
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # make move
                        gui_game()

# gui pop up for user to re-configure settings
def settingsPopup():
    settings = FormGUI(CFG.setup, title="Game Settings",width=600)
    settings.setField('square_size', 'combobox', label='Screen Size', values=CFG.SQUARE_SIZE_DICT,default='LG')
    settings.setField('depth_of_ai', 'combobox', label='Depth of AI', values=CFG.DEPTH_OF_AI_DICT,default='5',
                      desc='The DEEPER you choose - the HARDER it gets'
                           '\n (note this also slows computation time)')
    settings.run()

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


if __name__=='__main__':
    settingsPopup()
    gui_game()