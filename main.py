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


def draw_sprites(forbidden=[]):
    buttons.draw(screen)
    land.draw(screen)
    if 'highlights' not in forbidden:
        highlights.draw(screen)
    if 'lines' not in forbidden:
        lines.draw(screen)
    heros.draw(screen)
    healthbars.draw(screen)


def terminate():
    pg.quit()
    sys.exit()


textures = {'box': load_image('box.png'), 'grass': load_image('grass.png'),
            'knight': load_image('knight.png'), 'cavalry': load_image('cavalry.png'),
            'medic': load_image('medic.png'), 'sneaker': load_image('sneaker.png'),
            'farmer': load_image('farmer.png'), 'archer': load_image('archer.png'),
            'moraler': load_image('moraler.png')}

BLACK = pg.Color('black')
WHITE = pg.Color('white')

image_size = textures['grass'].get_width()

right_i = load_image('line_r.png')

arrows = {'right': right_i, 'up': pg.transform.rotate(right_i, 90),
          'down': pg.transform.rotate(right_i, -90), 'left': pg.transform.rotate(right_i, 180),
          'up_right': pg.transform.rotate(right_i, 45), 'up_left': pg.transform.rotate(right_i, 135),
          'down_right': pg.transform.rotate(right_i, -45),
          'down_left': pg.transform.rotate(right_i, -135)}

buttons_imgs = {'turn': [load_image('turn.png'), load_image('turn_pushed.png')]}

team_colors = {1: pg.Color('blue'), 2: pg.Color('red')}

highlight = pg.Surface((image_size, image_size), pg.SRCALPHA, 32)
highlight.fill(pg.Color('yellow'))

for i in range(image_size):
    for j in range(image_size):
        tipa_textura = list(highlight.get_at((j, i)))
        tipa_textura[-1] = 180
        highlight.set_at((j, i), tuple(tipa_textura))

mapa = load_level('map1.txt')


class Board:
    def __init__(self, coords, cell_size, width, height):
        self.width = width
        self.height = height
        self.left = coords[0]
        self.top = coords[1]
        self.cell_size = cell_size
        self.clicked = False
        self.step = 1

    def get_pos(self, coords):
        return [coords[1] * self.cell_size + self.left, coords[0] * self.cell_size + self.top]

    def create_hero(self, group, coords, texture, dmg, hp, team, movep=1, bonus=[], attack_range=1):
        self.board[coords[0]][coords[1]] = \
            Hero(group, [64 * coords[1], 64 * coords[0]], texture, dmg, hp, team,
                 movep, bonus, attack_range)

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

    def abort(self):
        self.clicked = False
        for i in highlights:
            highlights.remove(i)
        for i in lines:
            lines.remove(i)

    def get_cell(self, mouse_pos):
        y_cell = (mouse_pos[1] - self.top) // self.cell_size
        x_cell = (mouse_pos[0] - self.left) // self.cell_size
        if 0 <= x_cell < self.width and 0 <= y_cell < self.height:
            return [y_cell, x_cell]
        return None

    def change_step(self):
        self.check_bonus()
        self.step = 2 if self.step == 1 else 1
        for i in heros:
            i.cur_movep = i.movep
            i.attacked = False

    def check_bonus(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                cur_cell = self.board[i][j]
                if cur_cell.__class__ == Hero and cur_cell.team == self.step:
                    for z in cur_cell.bonus:
                        ry1 = i - z.range
                        ry1 = 0 if ry1 < 0 else ry1
                        ry2 = i + z.range + 1
                        ry2 = self.height - 1 if ry2 >= self.height else ry2
                        rx1 = j - z.range
                        rx1 = 0 if rx1 < 0 else rx1
                        rx2 = j + z.range + 1
                        rx2 = self.width - 1 if rx2 >= self.width else rx2
                        for y in range(len(self.board))[ry1:ry2]:
                            for x in range(len(self.board[y]))[rx1:rx2]:
                                if y == i and x == j:
                                    continue
                                if self.board[y][x].__class__ == Hero and\
                                        self.board[y][x].team == cur_cell.team:
                                    z.do_bonus(self.board[y][x])

    def on_click(self, cell_coords):
        if not self.clicked:
            cur_cell = self.board[cell_coords[0]][cell_coords[1]]
            if cur_cell.__class__ == Hero and cur_cell.team == self.step and cur_cell.cur_movep != 0:
                self.clicked = cell_coords
                self.was = [[0 for _ in range(self.width)] for _ in range(self.height)]
                self.has_path(self.clicked[1], self.clicked[0])
                if cur_cell.attacked == True:
                    return
                if cur_cell.attack_range > 1:
                    ry1 = self.clicked[0] - cur_cell.attack_range
                    ry1 = 0 if ry1 < 0 else ry1
                    ry2 = self.clicked[0] + cur_cell.attack_range + 1
                    ry2 = self.height - 1 if ry2 >= self.height else ry2
                    rx1 = self.clicked[1] - cur_cell.attack_range
                    rx1 = 0 if rx1 < 0 else rx1
                    rx2 = self.clicked[1] + cur_cell.attack_range + 1
                    rx2 = self.width - 1 if rx2 >= self.width else rx2
                    for y in range(len(self.board))[ry1:ry2]:
                        for x in range(len(self.board[y]))[rx1:rx2]:
                            if self.board[y][x].__class__ == Hero and\
                                    self.board[y][x].team != self.step:
                                Highlight(self.get_pos([y, x]))
                else:
                    for y1 in range(len(self.board)):
                        for x1 in range(len(self.board[y1])):
                            if self.board[y1][x1].__class__ == Hero and (
                                    self.board[y1][x1].team != cur_cell.team):
                                minim = False
                                for i in [-1, 0, 1]:
                                    for j in [-1, 0, 1]:
                                        if not (0 <= x1 + j < self.width and 0 <= y1 + i < self.height):
                                            continue
                                        cur = self.was[y1 + i][x1 + j]
                                        if cur > 0:
                                            if not minim or cur < minim:
                                                print('da')
                                                minim = cur

                                print(minim + 1)
                                for i in self.was:
                                    print(*i, sep='\t')
                                if minim and minim <= cur_cell.cur_movep and\
                                        not self.board[y1][x1].attacked:
                                    Highlight(self.get_pos([y1, x1]))

        if self.clicked:
            goal = self.board[cell_coords[0]][cell_coords[1]]
            if goal == 0:
                self.make_movement(cell_coords)
                self.abort()
            elif goal.__class__ == Hero and goal.team\
                    != self.board[self.clicked[0]][self.clicked[1]].team:
                self.attack(cell_coords)
                self.abort()

    def attack(self, cell_coords):
        myhero = self.board[self.clicked[0]][self.clicked[1]]
        if myhero.attack_range == 1:
            new_coords = self.make_movement(cell_coords, -1)
            if not new_coords:
                return
            myhero = self.board[new_coords[0]][new_coords[1]]
        else:
            self.has_path(self.clicked[1], self.clicked[0])
            if not self.was[cell_coords[0]][cell_coords[1]] <= myhero.attack_range:
                return
        if myhero.cur_movep > 0 and not myhero.attacked:
            enemy_died = self.board[cell_coords[0]][cell_coords[1]].get_damage(myhero.dmg)
            myhero.attacked = True
            myhero.cur_movep -= 1
            if enemy_died:
                if myhero.attack_range == 1:
                    crds = self.get_pos(cell_coords)
                    myhero.move([crds[0], crds[1]])
                    self.board[cell_coords[0]][cell_coords[1]] = myhero
                    self.board[new_coords[0]][new_coords[1]] = 0
                    for i in healthbars:
                        i.move()
                else:
                    self.board[cell_coords[0]][cell_coords[1]] = 0
            screen.fill(pg.Color('white'))
            all_sprites.draw(screen)
            pg.display.flip()

    def make_movement(self, cell_coords, predel=None):
        for i in self.was:
            #print(*i, sep='\t')
            pass
        back_way = self.get_back(cell_coords[1], cell_coords[0],
                                 self.clicked[1], self.clicked[0])
        if not back_way:
            return False
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
            screen.fill(pg.Color('white'))
            all_sprites.draw(screen)
            pg.display.flip()
            time.sleep(0.15)
            op -= 1
        my_hero.cur_movep = op
        return [last[0], last[1]]

    def show_way(self, cell_coords):
        for i in lines:
            lines.remove(i)
        if self.board[self.clicked[0]][self.clicked[1]].attack_range > 1 and \
                self.board[cell_coords[0]][cell_coords[1]].__class__ == Hero:
            draw_sprites()
            pg.display.flip()
            return
        back_way = self.get_back(cell_coords[1], cell_coords[0],
                                 self.clicked[1], self.clicked[0])
        if back_way is False:
            return
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
        draw_sprites()
        pg.display.flip()

    def get_mouse_movement(self, mouse_pos):
        cell_pos = self.get_cell(mouse_pos)
        if cell_pos is not None:
            if self.board[cell_pos[0]][cell_pos[1]] == 0 or (self.board[cell_pos[0]][
                cell_pos[1]].__class__ == Hero and (self.board[cell_pos[0]][cell_pos[1]
                    ].team != self.board[self.clicked[0]][self.clicked[1]].team)):
                self.show_way(cell_pos)
            else:
                for i in lines:
                    lines.remove(i)
                draw_sprites()

    def get_click(self, mouse_pos):
        cell_pos = self.get_cell(mouse_pos)
        if cell_pos is not None:
            self.on_click(cell_pos)
        else:
            return False

    def has_path(self, x1, y1, dung=1, above=False):
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
                                if (self.board[new_y][new_x] == 1 or \
                                        (self.board[new_y][new_x].__class__ == Hero and
                                 [new_y, new_x] != [y1, x1])) and not above:
                                    self.was[new_y][new_x] = -1
                                    continue
                                if self.was[new_y][new_x] == 0:
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
                    if not (0 <= x1 + j < self.width and 0 <= y1 + i < self.height):
                        continue
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


class Hero(pg.sprite.Sprite):
    def __init__(self, group, coords, texture, dmg, max_hp, team, movep, bonus, attack_range):
        super().__init__(group, all_sprites)
        if team == 2:
            self.image = pg.transform.flip(texture, True, False)
        else:
            self.image = texture
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]
        self.dmg = dmg
        self.max_hp = max_hp
        self.cur_hp = max_hp
        self.movep = movep
        self.bonus = bonus
        self.cur_movep = movep
        self.team = team
        self.healthbar = Healthbar(healthbars, self)
        self.attacked = False
        self.attack_range = attack_range

    def move(self, coords):
        self.rect.x = coords[0]
        self.rect.y = coords[1]

    def get_damage(self, damage):
        self.cur_hp -= damage
        self.healthbar.check_hp()
        textura = []
        for i in range(image_size):
            textura.append([])
            for j in range(image_size):
                textura[-1].append(self.image.get_at((j, i)))
                tipa_textura = list(textura[-1][-1])
                if tipa_textura[-1] != 0:
                    tipa_textura[0] += 200
                    if tipa_textura[0] > 255:
                        tipa_textura[0] = 255

                self.image.set_at((j, i), tuple(tipa_textura))
        draw_sprites(['lines', 'highlights'])
        pg.display.flip()
        time.sleep(0.3)
        for i in range(len(textura)):
            for j in range(len(textura[i])):
                self.image.set_at((j, i), textura[i][j])
        draw_sprites(['lines', 'highlights'])
        pg.display.flip()
        if self.cur_hp <= 0:
            heros.remove(self)
            all_sprites.remove(self, self.healthbar)
            healthbars.remove(self.healthbar)
            return True
        return False

    def get_heal(self, heal):
        self.cur_hp += heal
        self.cur_hp = self.max_hp if self.cur_hp > self.max_hp else self.cur_hp
        self.healthbar.check_hp()
        textura = []
        for i in range(image_size):
            textura.append([])
            for j in range(image_size):
                textura[-1].append(self.image.get_at((j, i)))
                tipa_textura = list(textura[-1][-1])
                if tipa_textura[-1] != 0:
                    tipa_textura[1] += 150
                    if tipa_textura[1] > 255:
                        tipa_textura[1] = 255
                self.image.set_at((j, i), tuple(tipa_textura))
        draw_sprites(['lines', 'highlights'])
        pg.display.flip()
        time.sleep(0.3)
        for i in range(len(textura)):
            for j in range(len(textura[i])):
                self.image.set_at((j, i), textura[i][j])
        draw_sprites(['lines', 'highlights'])
        pg.display.flip()

    def check_bonus(self):
        #for i in self.bonus:
            #if i == 'range_attack'
        pass


class Bonus:
    def __init__(self, name, range, power=0):
        self.name = name
        self.range = range
        self.power = power

    def do_bonus(self, hero, allies=True):
        if self.name == 'heal':
            if allies:
                if hero.cur_hp != hero.max_hp:
                    hero.get_heal(self.power)


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
        length = 48 * self.owner.cur_hp // self.owner.max_hp
        length = 0 if length <= 0 else length
        self.image = pg.Surface((52, 14), pg.SRCALPHA, 32)
        self.image.fill(BLACK)
        image_hp = pg.Surface((length, 10), pg.SRCALPHA, 32)
        image_hp.fill(team_colors[self.owner.team])
        self.image.blit(image_hp, (2, 2))
        font = pg.font.SysFont('visitor', 18)
        text = font.render(str(self.owner.cur_hp), 1, (255, 255, 255))
        self.image.blit(text, (12, 1))


class Button(pg.sprite.Sprite):
    def __init__(self, group, coords, meaning):
        super().__init__(group, all_sprites)
        self.image = buttons_imgs[meaning][0]
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]
        self.meaning = meaning
        self.clicked = False

    def do_smth(self):
        if self.meaning == 'turn':
            borda.change_step()

    def get_click1(self, pos):
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.width and \
                self.rect.y <= pos[1] <= self.rect.height + self.rect.y:
            self.clicked = True
            self.image = buttons_imgs[self.meaning][1]

    def get_click2(self, pos):
        self.image = buttons_imgs[self.meaning][0]
        if self.rect.x <= pos[0] <= self.rect.x + self.rect.width and \
                self.rect.y <= pos[1] <= self.rect.height + self.rect.y:
            if self.clicked:
                borda.change_step()
                self.clicked = False



class Highlight(pg.sprite.Sprite):
    def __init__(self, coords):
        super().__init__(highlights)
        self.image = highlight
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]


running = True

pg.init()
width, height = size = [1280, 720]
screen = pg.display.set_mode(size)

all_sprites = pg.sprite.Group()
land = pg.sprite.Group()
heros = pg.sprite.Group()
healthbars = pg.sprite.Group()
buttons = pg.sprite.Group()
highlights = pg.sprite.Group()
lines = pg.sprite.Group()

Button(buttons, [0, 500], 'turn')

screen.fill(WHITE)

MYEVENTTYPE = 19
ADDEVENT = 10
speed = 1000

pg.time.set_timer(ADDEVENT, 80)

pg.mouse.set_visible(True)

borda = Board([0, 0], image_size, len(mapa[0]), len(mapa))
borda.render(mapa)

borda.create_hero(heros, [0, 7], textures['medic'], 10, 100, 1, movep=3, bonus=[Bonus('heal', 3, 5)])
borda.create_hero(heros, [1, 7], textures['archer'], 100, 100, 1, movep=3, attack_range=5)
borda.create_hero(heros, [2, 7], textures['cavalry'], 120, 250, 1, movep=15)
borda.create_hero(heros, [3, 7], textures['farmer'], 10, 100, 1, movep=3)
borda.create_hero(heros, [4, 7], textures['moraler'], 10, 100, 1, movep=3)
borda.create_hero(heros, [5, 2], textures['knight'], 10, 100,  1, movep=3)
borda.create_hero(heros, [6, 2], textures['sneaker'], 10, 100, 1, movep=3)

borda.create_hero(heros, [0, 8], textures['medic'], 10, 100, 2, movep=3)
borda.create_hero(heros, [1, 8], textures['archer'], 10, 100, 2, movep=3, attack_range=5)
borda.create_hero(heros, [2, 8], textures['cavalry'], 10, 100, 2, movep=3)
borda.create_hero(heros, [3, 8], textures['farmer'], 10, 100, 2, movep=3)
borda.create_hero(heros, [4, 8], textures['moraler'], 10, 100, 2, movep=3)
borda.create_hero(heros, [5, 8], textures['knight'], 10, 100,  2, movep=3)
borda.create_hero(heros, [6, 8], textures['sneaker'], 10, 100, 2, movep=3)

draw_sprites()

while running:
    for event in pg.event.get():
        if event.type == pg.MOUSEMOTION:
            if borda.clicked:
                borda.get_mouse_movement(event.pos)
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                nu = borda.get_click(event.pos)
                if nu is False:
                    for i in buttons:
                        i.get_click1(event.pos)
                    borda.abort()
            elif event.button == 3:
                borda.abort()
            screen.fill(WHITE)
            draw_sprites()
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                for i in buttons:
                    i.get_click2(event.pos)
            draw_sprites()
        if event.type == pg.QUIT:
            terminate()
    pg.display.flip()
