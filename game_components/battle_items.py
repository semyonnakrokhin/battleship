from pprint import pprint
from typing import Callable

import pygame as pg
from random import randint
from .game_config import *
from time import sleep
from ..battle_components.components import GamePole

pg.init()
fnt_num = pg.font.SysFont('freesansbold', FNT_SIZE)


class PlayField:
    def __init__(self, parent_surface: pg.Surface, center_coords: tuple, poleobj: GamePole, cell_qty: int = CELL_QTY,
                 cell_size: int = CELL_SIZE):
        self.__screen = parent_surface
        self.__cell_qty = cell_qty
        self.__cell_size = cell_size
        self.__cells_offset = None

        self.__poleobj = poleobj
        self.__poleobj.init()
        self.__cell_states = CELL_STATES

        self.__all_cells = pg.sprite.Group()
        self.__all_states = pg.sprite.Group()
        self.__all_sights = pg.sprite.Group()

        self.__cell_pressed = None
        self.__cell_in_sight = None
        self.__current_sight = None

        # DRAWING WHILE INITIALIZING
        self.__draw_playfield(center_coords)
        self.__draw_cells_on_playfield()
        pg.display.update()

    def __draw_playfield(self, center_coords):
        total_size = self.__cell_size * self.__cell_qty

        n_cols, n_rows = self.__create_num_fields()
        play_field = pg.Surface((
            n_rows.get_width() + total_size,
            n_cols.get_height() + total_size
        ), pg.SRCALPHA)

        play_field.blit(n_cols, (n_rows.get_width(), 0))
        play_field.blit(n_rows, (0, n_cols.get_height()))
        self.__screen.blit(play_field, play_field.get_rect(center=center_coords))

        self.__cells_offset = (
            center_coords[0] - play_field.get_width() // 2 + n_rows.get_width(),
            center_coords[1] - play_field.get_height() // 2 + n_cols.get_height()
        )

    def __create_num_fields(self):
        n_cols = pg.Surface((self.__cell_size * self.__cell_qty, self.__cell_size), pg.SRCALPHA)
        n_rows = pg.Surface((self.__cell_size, self.__cell_size * self.__cell_qty), pg.SRCALPHA)
        for i in range(0, self.__cell_qty):
            letter = fnt_num.render(LTRS[i], 1, WHITE)
            number = fnt_num.render(str(i + 1), 1, WHITE)
            n_cols.blit(
                source=letter,
                dest=(i * self.__cell_size + (self.__cell_size - letter.get_rect().width) // 2,
                      (n_cols.get_height() - letter.get_rect().height) // 2)
            )
            n_rows.blit(
                source=number,
                dest=((n_rows.get_width() - number.get_rect().width) // 2,
                      i * self.__cell_size + (self.__cell_size - number.get_rect().height) // 2)
            )

        return n_cols, n_rows

    #### VERY IMPORTANT PART - DRAWING CELLS ON ABSOLUTE SCREEN
    def __create_battlefield(self):
        group = pg.sprite.Group()
        for y in range(self.__cell_qty):
            for x in range(self.__cell_qty):
                # !!! GET CURRENT STATE OF POLE !!!
                state = self.__poleobj.get_pole()[y][x]
                color, statefile = self.__cell_states[state]

                cell = Cell(
                    color=color,
                    statefile=statefile,
                    size=self.__cell_size,
                    coords=(x, y),
                    name=LTRS[x] + str(y + 1)
                )

                group.add(cell)

        return group

    def __add_states_on_cells(self):
        for cell in self.__all_cells:
            if cell.statefile:
                self.__all_states.add(State(cell))

    def __add_offsets_to_cells(self):
        for cell in self.__all_cells:
            cell.rect.x += self.__cells_offset[0]
            cell.rect.y += self.__cells_offset[1]

    def __draw_cells_on_playfield(self):
        self.__all_cells = self.__create_battlefield()
        self.__add_offsets_to_cells()
        self.__add_states_on_cells()
        self.__all_cells.draw(self.__screen)
        self.__all_states.draw(self.__screen)

    #### END OF VERY IMPORTANT PART

    def __get_cell(self, position):
        for cell in self.__all_cells:
            if cell.rect.collidepoint(position):
                return cell

        return None

    def btn_down(self, button: int, position: tuple, function_human_go: Callable[[int, int], None]):
        cell_pressed = self.__get_cell(position)

        if cell_pressed is not None:
            if button == 1:
                x, y = cell_pressed.battle_coords
                # Поле компьютера старое
                function_human_go(x, y)
                # Поле компьютера обновилось
                self.__draw_cells_on_playfield()

    def sight_moving(self, position: tuple):
        cell_in_sight = self.__get_cell(position)

        if cell_in_sight is not None:
            if self.__cell_in_sight is None or cell_in_sight != self.__cell_in_sight:
                self.__cell_in_sight = cell_in_sight
                self.__all_sights.empty()
                self.__all_sights.add(Sight(cell_in_sight))

                self.__draw_cells_on_playfield()
                self.__all_sights.draw(self.__screen)
        else:
            self.__all_sights.empty()
            self.__draw_cells_on_playfield()

    def btn_up(self, function_computer_go: Callable[[], None]):
        sleep(3)
        function_computer_go()
        self.__draw_cells_on_playfield()


class Cell(pg.sprite.Sprite):
    def __init__(self, color: pg.Color, statefile: str or None, size: int, coords: tuple, name: str):
        super().__init__()

        x, y = coords
        self.battle_coords = coords
        self.statefile = statefile
        self.cell_name = name

        self.image = pg.Surface((size, size), pg.SRCALPHA)
        self.image.fill(color)

        self.rect = self.image.get_rect(topleft=(x * size, y * size))

        pg.draw.rect(self.image, MID_GREY, (0, 0, self.rect.width, self.rect.height), 1)


class Sight(pg.sprite.Sprite):
    def __init__(self, cell: Cell):
        super().__init__()
        self.coords = (cell.rect.x, cell.rect.y)
        self.cell_name = cell.cell_name

        img = pg.image.load(BASE_DIR + IMG_DIR + 'sight.png').convert()
        img.set_colorkey((255, 255, 255))
        self.image = pg.transform.scale(img, (cell.rect.width, cell.rect.height)).convert()
        self.rect = self.image.get_rect(topleft=self.coords)


class State(pg.sprite.Sprite):
    def __init__(self, cell: Cell):
        super().__init__()

        self.image = pg.transform.scale(
            pg.image.load(cell.statefile).convert(),
            (cell.rect.width, cell.rect.height)).convert_alpha()
        self.image.set_colorkey(WHITE)
        self.rect = cell.rect.copy()
