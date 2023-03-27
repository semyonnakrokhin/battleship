from string import ascii_lowercase
from ..battle_components.components import SeaBattle

BASE_DIR = ''#'/battleship/'
IMG_DIR = 'images/'

FPS = 20
WINDOW_SIZE = (1000, 600)
HUMAN_FIELD_CENTER = WINDOW_SIZE[0] // 4, WINDOW_SIZE[1] // 2
COMPUTER_FIELD_CENTER = 3 * WINDOW_SIZE[0] // 4, WINDOW_SIZE[1] // 2

BACKGROUND = (150, 90, 30)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
METAL = (108, 108, 108)
WATER = (98, 156, 255)
MID_GREY = (180, 180, 180)

CELL_QTY = 10
CELL_SIZE = 30
COLORS = (WATER, METAL)
CELL_STATES = {
    SeaBattle.COVER: (WHITE, None),
    SeaBattle.MISHIT: (WATER, BASE_DIR + IMG_DIR + 'bomb1.png'),
    SeaBattle.NO_HIT: (WATER, None),
    SeaBattle.UNBROKEN_DECK: (METAL, None),
    SeaBattle.BROKEN_DECK: (METAL, BASE_DIR + IMG_DIR + 'explosion1.png')
}

LTRS = ascii_lowercase
FNT_SIZE = 22