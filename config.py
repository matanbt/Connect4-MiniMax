
# CONSTANTS:
BOARD_ROWS, BOARD_COLS = 6, 7
ICON = "img/icon.png"
CAPTION = "Matan's Connect-4"
B_COLOR = (0, 153, 255)
EMP_COLOR = (0, 0, 51)
GREY = (192, 192, 192)
P_COLOR = ((51, 204, 51), (255, 51, 0), (0, 153, 0), (204, 0, 0))
BLACK = (0, 0, 0)
TEXT_COLOR = (255, 255, 102)

HU_PLAYER = 1
AI_PLAYER = 2
EMPTY_SPOT = 0
opp = lambda p: p % 2 + 1  # returns the opponent id


# player1 [HUMAN], player2 [AI]= =: 1,2, EMPTY=0

class CFG:
    SQUARE_SIZE_DICT = {
        'XXL': 120, 'XL': 100, 'LG': 80, 'MD': 70, 'SM': 60
    }
    DEPTH_OF_AI_DICT = {
        '3': 3, '4': 4, '5': 5, '6': 6, '7': 7
    }

    # DEFAULT VALUES (TO BE REDEFINED BY USER IN SETTINGS)
    DEPTH_OF_AI = 5
    SQUARE_SIZE = 80  # pixels of a spot in the matrix

    WIDTH, HEIGHT = BOARD_COLS * SQUARE_SIZE, (BOARD_ROWS + 2) * SQUARE_SIZE

    @staticmethod
    def reCalc():
        CFG.WIDTH, CFG.HEIGHT = BOARD_COLS * CFG.SQUARE_SIZE, (BOARD_ROWS + 2) * CFG.SQUARE_SIZE

    @staticmethod
    def setup(square_size, depth_of_ai):
        CFG.SQUARE_SIZE = square_size
        CFG.DEPTH_OF_AI = depth_of_ai
        CFG.reCalc()

