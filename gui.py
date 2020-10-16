from config import *
import pygame

# py game:
def init_board(SCREEN, brd=None):
    for r in range(2, BOARD_ROWS + 2):
        for c in range(BOARD_COLS):
            pygame.draw.rect(SCREEN, B_COLOR, [c * CFG.SQUARE_SIZE, r * CFG.SQUARE_SIZE, CFG.SQUARE_SIZE, CFG.SQUARE_SIZE])
            pygame.draw.circle(SCREEN, EMP_COLOR,
                               [(c * CFG.SQUARE_SIZE) + CFG.SQUARE_SIZE // 2, (r * CFG.SQUARE_SIZE) + CFG.SQUARE_SIZE // 2],
                               int(CFG.SQUARE_SIZE / 2.3))

    pygame.draw.rect(SCREEN, EMP_COLOR, [0, 1 * CFG.SQUARE_SIZE, CFG.WIDTH, CFG.SQUARE_SIZE])
    pygame.draw.rect(SCREEN, B_COLOR, [0, 1 * CFG.SQUARE_SIZE, CFG.WIDTH, CFG.SQUARE_SIZE], 10)
    pygame.display.update()


def draw_move(SCREEN, col, row, player, curr_move=False):
    pygame.draw.circle(SCREEN, P_COLOR[player - 1],
                       [(col * CFG.SQUARE_SIZE) + CFG.SQUARE_SIZE // 2,
                        ((BOARD_ROWS - row + 1) * CFG.SQUARE_SIZE) + CFG.SQUARE_SIZE // 2],
                       int(CFG.SQUARE_SIZE / 2.3))
    pygame.draw.circle(SCREEN, P_COLOR[player + 1],
                       [(col * CFG.SQUARE_SIZE) + CFG.SQUARE_SIZE // 2,
                        ((BOARD_ROWS - row + 1) * CFG.SQUARE_SIZE) + CFG.SQUARE_SIZE // 2],
                       int(CFG.SQUARE_SIZE / 4))
    if curr_move: pygame.draw.circle(SCREEN, TEXT_COLOR,
                                     [(col * CFG.SQUARE_SIZE) + CFG.SQUARE_SIZE // 2,
                                      ((BOARD_ROWS - row + 1) * CFG.SQUARE_SIZE) + CFG.SQUARE_SIZE // 2],
                                     int(CFG.SQUARE_SIZE / 4))
    pygame.display.update()


def draw_motion(SCREEN, pos, player):
    pygame.draw.rect(SCREEN, EMP_COLOR, [0, 1 * CFG.SQUARE_SIZE, CFG.WIDTH, CFG.SQUARE_SIZE])
    pygame.draw.rect(SCREEN, B_COLOR, [0, 1 * CFG.SQUARE_SIZE, CFG.WIDTH, CFG.SQUARE_SIZE], int(0.1 * CFG.SQUARE_SIZE))
    pygame.draw.circle(SCREEN, P_COLOR[player - 1], [pos[0], (int)(1.5 * CFG.SQUARE_SIZE)], CFG.SQUARE_SIZE // 2)
    pygame.display.update()


def draw_text(SCREEN, text, size=int(0.9 * CFG.SQUARE_SIZE), coor=(CFG.WIDTH // 2, CFG.HEIGHT // 2), font_name="Comic Sans MS",
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
    pygame.draw.rect(SCREEN, BLACK, [int(0.6 * CFG.WIDTH), 0, int(0.4 * CFG.WIDTH), int(0.9 * CFG.SQUARE_SIZE)])
    draw_text(SCREEN, "Player " + str(player) + "'s Move", size=int(0.25 * CFG.SQUARE_SIZE),
              coor=(int(0.8 * CFG.WIDTH), int(0.25 * CFG.SQUARE_SIZE)), bold=False)
    draw_text(SCREEN, "Turns: " + str(turns), size=int(0.25 * CFG.SQUARE_SIZE),
              coor=(int(0.8 * CFG.WIDTH), int(0.6 * CFG.SQUARE_SIZE)), bold=False)
