from random import randint


class Ship:
    UNBROKEN_DECK = 1
    BROKEN_DECK = 2

    def __init__(self, length, tp=1, x=None, y=None):
        self._x, self._y = x, y
        self._length = length
        self._is_move = True

        # 1 - ориентация по горизонтали, 2 - ориентация по вертикали
        self._tp = tp

        # 1 - палуба целая, 2 - в палубу попали
        self._cells = [self.UNBROKEN_DECK for _ in range(self._length)]

    def ship_coords(self):
        x0, y0 = self._x, self._y
        return tuple(
            (x0 + delta, y0) if self._tp == 1 else (x0, y0 + delta) for delta in range(self._length)
            if x0 != None and y0 != None
        )

    def ship_surroundings(self):
        x0, y0 = self._x, self._y

        W = self._length if self._tp == 1 else 1
        H = self._length if self._tp == 2 else 1

        start_x, finish_x = x0 - 1, (x0 + W)
        start_y, finish_y = y0 - 1, (y0 + H)

        # Here + 1 is added as stop is not uncluded in range object
        return tuple((x, y) for x in range(start_x, finish_x + 1) for y in range(start_y, finish_y + 1))

    def set_start_coords(self, x, y):
        self._x, self._y = x, y

    def get_start_coords(self):
        return self._x, self._y

    def move(self, go):
        if self._is_move:
            if self._tp == 1:
                self._x += go

            if self._tp == 2:
                self._y += go

    def is_collide(self, ship):
        for tp in ship.ship_coords():
            if tp in self.ship_surroundings():
                return True

        return False

    def is_out_pole(self, size):
        for x_ship, y_ship in self.ship_coords():
            if not (0 <= x_ship < size) or not (0 <= y_ship < size):
                return True

        return False

    def __iter__(self):
        for st in self._cells:
            yield st

    def __getitem__(self, item):
        if 0 <= item <= self._length - 1:
            return self._cells[item]

    def __setitem__(self, key, value):
        if 0 <= key <= self._length - 1:
            self._cells[key] = value


class GamePole:
    COVER = '#'
    MISHIT = -1
    NO_HIT = 0
    UNBROKEN_DECK = Ship.UNBROKEN_DECK
    BROKEN_DECK = Ship.BROKEN_DECK

    def __init__(self, size, cover=False):
        self._size = size
        self._ships = []
        self._cover = cover

        self._allowed_coords = []
        self._forbidden_coords = []
        self._mishits = set()

    @property
    def mishits(self):
        return self._mishits

    @mishits.setter
    def mishits(self, value: tuple):
        if type(value) != tuple:
            raise TypeError('тип передаваемого аргумента должен быть tuple, состоящий из двух координат')

        self._mishits.add(value)

    def init(self):
        self._ships += [
            Ship(4, tp=randint(1, 2)),
            Ship(3, tp=randint(1, 2)), Ship(3, tp=randint(1, 2)),
            Ship(2, tp=randint(1, 2)), Ship(2, tp=randint(1, 2)), Ship(2, tp=randint(1, 2)),
            Ship(1, tp=randint(1, 2)), Ship(1, tp=randint(1, 2)), Ship(1, tp=randint(1, 2)), Ship(1, tp=randint(1, 2))
        ]

        self._allowed_coords = [(x, y) for x in range(self._size) for y in range(self._size)]

        for ship in self._ships:
            self._place_ship(ship)
            for tp in ship.ship_surroundings():
                if tp in self._allowed_coords:
                    self._allowed_coords.remove(tp)
                    self._forbidden_coords.append(tp)

    def _place_ship(self, ship):
        tp = ship._tp
        tp_inverted = 2 if tp == 1 else 1

        while True:
            xt, yt = self._allowed_coords[randint(0, len(self._allowed_coords) - 1)]
            ship.set_start_coords(xt, yt)

            # Break condition:
            # not ship.is_out_pole(self._size) and set(ship.ship_coords()) & set(self._forbidden_coords) == set()

            if not ship.is_out_pole(self._size) and set(ship.ship_coords()) & set(self._forbidden_coords) == set():
                break
            else:
                ship._tp = tp_inverted
                if not ship.is_out_pole(self._size) and set(ship.ship_coords()) & set(self._forbidden_coords) == set():
                    break
                else:
                    continue

    def __check_ship_collision(self, ship):
        for s in self._ships:
            if s != ship:
                if ship.is_collide(s) or ship.is_out_pole(self._size):
                    return True

        return False

    def __check_mines_at_heading(self, ship):
        for x_ship, y_ship in ship.ship_coords():
            if (x_ship, y_ship) in self._mishits:
                return True

        return False

    def get_ships(self):
        return self._ships

    def move_ships(self):
        for ship in self._ships:
            if ship._is_move:
                go = (-1, 1)[randint(0, 1)]

                ship.move(go)
                if self.__check_ship_collision(ship) or ship.is_out_pole(self._size) or self.__check_mines_at_heading(ship):
                    ship.move(-2 * go)
                    if self.__check_ship_collision(ship) or ship.is_out_pole(self._size) or self.__check_mines_at_heading(ship):
                        ship.move(go)

    def show(self):
        for row in self.get_pole():
            print(*row)

    def get_pole(self):
        '''
        API call to get pole with state of each cell
        :param cover: covering non shooted positions: NO_HIT and UNBROKEN_DECK (as MISHIT and BROKEN_DECK are damaged due to shot)
        :return: tuple with states of each cell, covered if required
        '''
        pole_prepack = tuple([self.COVER if self._cover else self.NO_HIT for _ in range(self._size)] for _ in range(self._size))

        # positioning mishits
        for x, y in self.mishits:
            pole_prepack[y][x] = self.MISHIT

        # positioning ships
        for ship in self._ships:
            for i, coords in enumerate(ship.ship_coords()):
                x, y = coords
                if ship[i] == self.UNBROKEN_DECK:
                    pole_prepack[y][x] = self.COVER if self._cover else ship[i]
                elif ship[i] == self.BROKEN_DECK:
                    pole_prepack[y][x] = ship[i]

        return tuple(tuple(st for st in row) for row in pole_prepack)


class SeaBattle:
    COVER = '#'
    MISHIT = GamePole.MISHIT
    NO_HIT = GamePole.NO_HIT
    UNBROKEN_DECK = Ship.UNBROKEN_DECK
    BROKEN_DECK = Ship.BROKEN_DECK

    def __init__(self, human_pole, computer_pole):
        self.__human_pole = human_pole
        self.__computer_pole = computer_pole

    def init(self):
        self.__human_pole.init()
        self.__computer_pole.init()

    @property
    def get_human_pole_obj(self):
        return self.__human_pole

    @property
    def get_computer_pole_obj(self):
        return self.__computer_pole

    # def get_human_pole(self):
    #     return self.__human_pole.get_pole()

    # def get_computer_pole(self):
    #     res_pole = ()
    #     for row in self.__computer_pole.get_pole():
    #         new_row = ()
    #         for st in row:
    #             new_row += (self.COVER if st in (self.NO_HIT, self.UNBROKEN_DECK) else st,)
    #         res_pole += (new_row,)
    #
    #     return res_pole

    def show(self):
        self.__human_pole.show()
        print()

        self.__computer_pole.show()
        print()

    def __shoot(self, pole, x, y):
        if not isinstance(pole, GamePole):
            raise TypeError('поле должно быть экземпляром класса GamePole')

        for ship in pole.get_ships():
            if (x, y) in ship.ship_coords():
                deck_indx = ship.ship_coords().index((x, y))
                ship[deck_indx] = self.BROKEN_DECK
                ship._is_move = False
                break
        else:
            pole.mishits = (x, y)

    def human_go(self, x, y):
        c_pole = self.__computer_pole

        self.__shoot(c_pole, x, y)
        c_pole.move_ships()

    def computer_go(self):
        h_pole = self.__human_pole

        pull_coords = tuple((x, y)
                            for y, row in enumerate(h_pole.get_pole())
                            for x, st in enumerate(row)
                            if st in (h_pole.NO_HIT, h_pole.UNBROKEN_DECK))

        x, y = pull_coords[randint(0, len(pull_coords) - 1)]

        self.__shoot(h_pole, x, y)
        h_pole.move_ships()

    @property
    def is_human_win(self):
        return tuple(ship for ship in self.__computer_pole.get_ships() if not all(st == 2 for st in ship)) == ()

    @property
    def is_computer_win(self):
        return tuple(ship for ship in self.__human_pole.get_ships() if not all(st == 2 for st in ship)) == ()

    def __bool__(self):
        return not self.is_human_win and not self.is_computer_win


if __name__ == '__main__':
    POLE_SIZE = 10

    my_pole = GamePole(POLE_SIZE)
    enemy_pole = GamePole(POLE_SIZE, cover=True)

    game = SeaBattle(my_pole, enemy_pole)
    game.init()
    step_game = 0

    while game:
        game.show()

        if step_game % 2 == 0:
            x, y = map(int, input().split())
            game.human_go(x, y)
        else:
            game.computer_go()

        step_game += 1

    if game.is_human_win:
        print("Поздравляем! Вы победили!")
    elif game.is_computer_win:
        print("Вы проиграли")
