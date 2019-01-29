import pygame as pg
import os, time
import random, sys
from copy import deepcopy


def load_image(name, colorkey=None):
    fullname = os.path.join('game_textures', name)
    try:
        image = pg.image.load(fullname)
        if colorkey == -2:
            image = image.convert_alpha()
        elif colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
                print(colorkey)
            image.set_colorkey(colorkey)
        return image
    except pg.error:
        print('error')


def load_level(filename):
    filename = "maps/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [''.join(line.strip().split()) for line in mapFile]
    return level_map


def terminate():
    pg.quit()
    sys.exit()


textures = {'box': load_image('box.png'), 'grass': load_image('grass.png'),
            'knight': load_image('knight.png'), 'cavalry': load_image('cavalry.png')}

BLACK = pg.Color('black')
WHITE = pg.Color('white')
f_img = load_image('farmer.png', pg.Color('white'))

image_size = textures['grass'].get_width()

right_i = load_image('line_r.png')

arrows = {'right': right_i, 'up': pg.transform.rotate(right_i, 90),
          'down': pg.transform.rotate(right_i, -90), 'left': pg.transform.rotate(right_i, 180),
          'up_right': pg.transform.rotate(right_i, 45), 'up_left': pg.transform.rotate(right_i, 135),
          'down_right': pg.transform.rotate(right_i, -45),
          'down_left': pg.transform.rotate(right_i, -135)}

team_colors = {1: pg.Color('blue'), 2: pg.Color('red')}

mapa = load_level('map1.txt')


class Creature(pg.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = f_img
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.left_jump = 0
        self.right_jump = 0

    def check(self):
        if self.right_jump:
            self.rect.x += 5
            self.right_jump = False
            self.image = f_img
        if self.left_jump:
            self.rect.x -= 5
            self.left_jump = False
            self.image = f_img


class Board:
    def __init__(self, coords, cell_size, width, height):
        self.width = width
        self.height = height
        self.left = coords[0]
        self.top = coords[1]
        self.cell_size = cell_size
        self.clicked = False

    def get_pos(self, coords):
        return [coords[1] * self.cell_size + self.left, coords[0] * self.cell_size + self.top]

    def render(self, mapa):
        self.board = []
        for c_i, i in enumerate(mapa):
            self.board.append([])
            for c_j, j in enumerate(i):
                if j == 'g':
                    Ground(land, [self.left + c_j * self.cell_size,
                                  self.top + c_i * self.cell_size], textures['grass'])
                    self.board[-1].append(0)
                elif j == 'c' or j == 'o':
                    Ground(land, [self.left + c_j * self.cell_size,
                                  self.top + c_i * self.cell_size], textures['box'])
                    self.board[-1].append(1)

    def get_cell(self, mouse_pos):
        y_cell = (mouse_pos[1] - self.top) // self.cell_size
        x_cell = (mouse_pos[0] - self.left) // self.cell_size
        if 0 <= x_cell < self.width and 0 <= y_cell < self.height:
            return [y_cell, x_cell]
        return None

    def on_click(self, cell_coords):
        if not self.clicked:
            if self.board[cell_coords[0]][cell_coords[1]].__class__ == Hero:
                self.clicked = cell_coords
                self.was = [[0 for _ in range(self.width)] for _ in range(self.height)]
                self.has_path(self.clicked[1], self.clicked[0])
        if self.clicked:
            goal = self.board[cell_coords[0]][cell_coords[1]]
            if goal == 0:
                self.make_movement(cell_coords)
                self.clicked = False
            elif goal.__class__ == Hero and goal.team\
                    != self.board[self.clicked[0]][self.clicked[1]].team:
                self.attack(cell_coords, self.board[self.clicked[0]][self.clicked[1]])
                self.clicked = False

    def attack(self, cell_coords, myhero):
        self.make_movement(cell_coords, -1)
        if myhero.cur_movep > 0 and not myhero.attacked:
            self.board[cell_coords[0]][cell_coords[1]].get_damage(myhero.dmg)
            myhero.attacked = True
            myhero.cur_movep -= 1

    def make_movement(self, cell_coords, predel=None):
        back_way = self.get_back(cell_coords[1], cell_coords[0],
                                 self.clicked[1], self.clicked[0])
        back_way.append([cell_coords[0], cell_coords[1]])
        last = back_way[0]
        my_hero = self.board[last[0]][last[1]]
        op = my_hero.cur_movep
        for i in back_way[1:predel]:
            if op == 0:
                break
            crds = self.get_pos(i)
            my_hero.move([crds[0], crds[1]])
            self.board[i[0]][i[1]] = my_hero
            self.board[last[0]][last[1]] = 0
            last = i
            for i in healthbars:
                i.move()
            all_sprites.draw(screen)

            pg.display.flip()
            time.sleep(0.15)
            op -= 1
        my_hero.cur_movep = op

    def show_way(self, cell_coords):
        lines = pg.sprite.Group()
        back_way = self.get_back(cell_coords[1], cell_coords[0],
                                 self.clicked[1], self.clicked[0])
        back_way.append([cell_coords[0], cell_coords[1]])
        last = back_way[0]
        op = self.board[last[0]][last[1]].cur_movep
        for i in back_way[1:]:
            if op == 0:
                break
            crds_last = self.get_pos(last)
            if last[1] > i[1]:
                if last[0] > i[0]:
                    Lines(lines, crds_last, 'up_left')
                elif last[0] == i[0]:
                    Lines(lines, crds_last, 'left')
                else:
                    Lines(lines, crds_last, 'down_left')
            elif last[1] == i[1]:
                if last[0] > i[0]:
                    Lines(lines, crds_last, 'up')
                elif last[0] < i[0]:
                    Lines(lines, crds_last, 'down')
            else:
                if last[0] > i[0]:
                    Lines(lines, crds_last, 'up_right')
                elif last[0] == i[0]:
                    Lines(lines, crds_last, 'right')
                else:
                    Lines(lines, crds_last, 'down_right')
            last = i
            op -= 1
        land.draw(screen)
        lines.draw(screen)
        heros.draw(screen)
        healthbars.draw(screen)
        pg.display.flip()

    def get_mouse_movement(self, mouse_pos):
        cell_pos = self.get_cell(mouse_pos)
        if cell_pos is not None:
            if self.board[cell_pos[0]][cell_pos[1]] == 0 or (self.board[cell_pos[0]][
                cell_pos[1]].__class__ == Hero and (self.board[cell_pos[0]][cell_pos[1]
                    ].team != self.board[self.clicked[0]][self.clicked[1]].team)):
                self.show_way(cell_pos)

    def get_click(self, mouse_pos):
        cell_pos = self.get_cell(mouse_pos)
        if cell_pos is not None:
            self.on_click(cell_pos)

    def has_path(self, x1, y1, dung=1):
        self.was[y1][x1] = 1

        last_was = False
        while True:
            if last_was == self.was:
                break
            last_was = deepcopy(self.was)
            for r_cnt, row in enumerate(self.was):
                for c_cnt, col in enumerate(row):
                    if col == dung:
                        for i in [-1, 0, 1]:
                            for j in [-1, 0, 1]:
                                new_y, new_x = i + r_cnt, j + c_cnt
                                if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                                    continue
                                if i == j == 0:
                                    continue
                                if self.board[new_y][new_x] == 1 or \
                                        (self.board[new_y][new_x].__class__ == Hero and
                                 [new_y, new_x] != [y1, x1] ):
                                    self.was[new_y][new_x] = -1
                                    continue
                                if self.board[new_y][new_x] != 1 and self.was[new_y][new_x] == 0:
                                    self.was[new_y][new_x] = dung + 1

            dung += 1

    def get_back(self, x1, y1, x2, y2):
        back_way = []
        breaking = False
        minim = False
        copy_was = deepcopy(self.was)
        if self.board[y1][x1].__class__ == Hero and (
            self.board[y1][x1].team != self.board[self.clicked[0]][self.clicked[1]].team):
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    cur = copy_was[y1 + i][x1 + j]
                    if cur > 0:
                        if not minim or cur < minim:
                            minim = cur
            copy_was[y1][x1] = minim + 1

        c = 1
        ways = 0
        while [y2, x2] not in back_way:
            if ways - c > 7:
                return False
            d_x = [-1, 0, 1] if x1 > x2 else [0, 1, -1] if x1 == x2 else [1, 0, -1]
            d_y = [-1, 0, 1] if y1 > y2 else [0, 1, -1] if y1 == y2 else [1, 0, -1]
            for i in d_y:
                if breaking:
                    breaking = False
                    break
                for j in d_x:
                    new_y, new_x = i + y1, j + x1
                    if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                        continue
                    if i == j == 0:
                        continue
                    if copy_was[new_y][new_x] == copy_was[y1][x1] - 1:
                        x1, y1 = new_x, new_y
                        back_way.append([y1, x1])
                        c += 1
                        breaking = True
                        break
            ways += 1

        return back_way[::-1]


class Ground(pg.sprite.Sprite):
    def __init__(self, group, coords, texture):
        super().__init__(group, all_sprites)
        self.image = texture
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]
        #print(self.rect.x, self.rect.y)


class Hero(pg.sprite.Sprite):
    def __init__(self, group, coords, texture, dmg, hp, team, movep=1, bonus=None):
        super().__init__(group, all_sprites)
        self.image = texture
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]
        self.dmg = dmg
        self.hp = hp
        self.movep = movep
        self.bonus = bonus
        self.cur_movep = movep
        self.team = team
        self.healthbar = Healthbar(healthbars, self)
        self.attacked = False

    def move(self, coords):
        self.rect.x = coords[0]
        self.rect.y = coords[1]

    def draw(self, screen):
        self.draw(screen)
        self.healthbar.draw(screen)

    def get_damage(self, damage):
        self.hp -= damage
        self.healthbar.check_hp()


class Lines(pg.sprite.Sprite):
    def __init__(self, group, coords, direction='right'):
        super().__init__(group)
        self.image = arrows[direction]
        self.rect = self.image.get_rect()
        if 'right' in direction:
            self.rect.x = coords[0] + image_size * 3 // 4
        elif 'left' in direction:
            self.rect.x = coords[0] - image_size * 2 // 4
        else:
            self.rect.x = coords[0] + image_size // 2 - 5
        if 'down' in direction:
            self.rect.y = coords[1] + image_size * 3 // 4
        elif 'up' in direction:
            self.rect.y = coords[1] - image_size * 2 // 4
        else:
            self.rect.y = coords[1] + image_size // 2 - 5


class Healthbar(pg.sprite.Sprite):
    def __init__(self, group, owner):
        super().__init__(group, all_sprites)
        self.owner = owner
        self.check_hp()
        self.rect = self.image.get_rect()
        self.move()

    def move(self):
        self.rect.x = self.owner.rect.x + image_size // 8
        self.rect.y = self.owner.rect.y + image_size * 4 // 5

    def check_hp(self):
        self.image = pg.Surface((48, 10), pg.SRCALPHA, 32)
        self.image.fill(team_colors[self.owner.team])
        font = pg.font.SysFont('visitor', 18)
        text = font.render(str(self.owner.hp), 1, (255, 255, 255))
        self.image.blit(text, (16, 0))


running = True

pg.init()
width, height = size = [1280, 720]
screen = pg.display.set_mode(size)

all_sprites = pg.sprite.Group()
land = pg.sprite.Group()
heros = pg.sprite.Group()
healthbars = pg.sprite.Group()

screen.fill(BLACK)

MYEVENTTYPE = 19
ADDEVENT = 10
speed = 1000

pg.time.set_timer(ADDEVENT, 80)

pg.mouse.set_visible(True)

borda = Board([0, 0], image_size, len(mapa[0]), len(mapa))
borda.render(mapa)


borda.board[5][14] = Hero(heros, [64*14, 64*5], textures['knight'], 10, 5678, 2, movep=2)
borda.board[0][0] = Hero(heros, [64*0, 64*0], textures['cavalry'], 10, 222, 1, movep=16)


print(len(healthbars))

land.draw(screen)
heros.draw(screen)
healthbars.draw(screen)


while running:
    for event in pg.event.get():
        if event.type == pg.MOUSEMOTION:
            if borda.clicked:
                borda.get_mouse_movement(event.pos)
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                borda.get_click(event.pos)
            elif event.button == 3:
                borda.clicked = False
            screen.fill(WHITE)
            all_sprites.draw(screen)
        if event.type == pg.KEYDOWN:
            pass

        if event.type == pg.QUIT:
            terminate()
    pg.display.flip()
