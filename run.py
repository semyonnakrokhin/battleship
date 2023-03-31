import pygame as pg
from game_components.game_config import *
from game_components.battle_items import PlayField
from battle_components.components import SeaBattle, GamePole


pg.init()
clock = pg.time.Clock()

screen = pg.display.set_mode(WINDOW_SIZE)

# Init and draw some content and environment
back_img = pg.image.load(BASE_DIR + IMG_DIR + 'background.jpg')
back_img = pg.transform.scale(back_img, WINDOW_SIZE)
screen.blit(back_img, (0, 0))

game = SeaBattle(human_pole=GamePole(CELL_QTY), computer_pole=GamePole(CELL_QTY, cover=True))

human_playfield = PlayField(screen, HUMAN_FIELD_CENTER, game.get_human_pole_obj)
computer_playfield = PlayField(screen, COMPUTER_FIELD_CENTER, game.get_computer_pole_obj)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()

        if game:
            if event.type == pg.MOUSEBUTTONDOWN:
                computer_playfield.btn_down(event.button, event.pos, game.human_go)
                # initialize.btn_down(event.button, event.pos, game.init)

            if event.type == pg.MOUSEBUTTONUP:
                human_playfield.btn_up(game.computer_go)

            if event.type == pg.MOUSEMOTION:
                computer_playfield.sight_moving(event.pos)
        elif game.is_human_win:
            print("Поздравляем! Вы победили!")
        elif game.is_computer_win:
            print("Вы проиграли")


    pg.display.update()

    clock.tick(FPS)