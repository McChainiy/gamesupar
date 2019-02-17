import pygame as pg
import os
import time
import sys
from copy import deepcopy


def load_image(name, colorkey=None):
    fullname = os.path.join('128textures', name)
    try:
        image = pg.image.load(fullname)
        if colorkey == -2:
            image.convert_alpha()
        elif colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        return image
    except pg.error:
        print('error', name)


def load_level(filename):
    filename = "maps/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [''.join(line.strip().split()) for line in mapFile]
    return level_map


def draw_sprites(forbidden=[]):
    screen.fill(GREY)
    buttons.draw(screen)
    p_land.draw(screen)
    if 'highlights' not in forbidden:
        highlights.draw(screen)
    if 'lines' not in forbidden:
        lines.draw(screen)
    p_heros.draw(screen)
    p_castles.draw(screen)
    healthbars.draw(screen)
    buttons.draw(screen)


def terminate():
    pg.quit()
    sys.exit()


textures = {'box': load_image('box.png'), 'grass': load_image('grass.png'),
            'knight': load_image('knight.png'), 'cavalry': load_image('cavalry.png'),
            'medic': load_image('medic.png'), 'sneaker': load_image('sneaker.png'),
            'farmer': load_image('farmer.png'),
            'archer': load_image('archer.png', -1),
            'moraler': load_image('moraler.png'), 'sand': load_image('sand.png'),
            'castle': load_image('castle.png'), 'trebushet': load_image('trebushet.png', -1)}

textures.update({'castle': [pg.transform.scale(textures['castle'], [128 // i, 128 // i]) for i in range(1, 6)]})
textures.update({'cavalry': [pg.transform.scale(textures['cavalry'], [128 // i, 128 // i]) for i in range(1, 6)]})
textures.update({'knight': [pg.transform.scale(textures['knight'], [128 // i, 128 // i]) for i in range(1, 6)]})
textures.update({'archer': [pg.transform.scale(textures['archer'], [128 // i, 128 // i]) for i in range(1, 6)]})
textures.update({'medic': [pg.transform.scale(textures['medic'], [128 // i, 128 // i]) for i in range(1, 6)]})
textures.update({'moraler': [pg.transform.scale(textures['moraler'], [128 // i, 128 // i]) for i in range(1, 6)]})
textures.update({'farmer': [pg.transform.scale(textures['farmer'], [128 // i, 128 // i]) for i in range(1, 6)]})
textures.update({'sneaker': [pg.transform.scale(textures['sneaker'], [128 // i, 128 // i]) for i in range(1, 6)]})
textures.update({'trebushet': [pg.transform.scale(textures['trebushet'], [128 // i, 128 // i]) for i in range(1, 6)]})
textures.update({'grass': [pg.transform.scale(textures['grass'], [128 // i, 128 // i]) for i in range(1, 6)]})
textures.update({'sand': [pg.transform.scale(textures['sand'], [128 // i, 128 // i]) for i in range(1, 6)]})
textures.update({'box': [pg.transform.scale(textures['box'], [128 // i, 128 // i]) for i in range(1, 6)]})

print(textures)

BLACK = pg.Color('black')
WHITE = pg.Color('white')
RED = pg.Color('red')
GREEN = pg.Color('green')
GREY = pg.Color('grey')

image_size = textures['grass'][0].get_width()

right_i = load_image('line_r.png', WHITE)

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
        stipa_textura = list(highlight.get_at((j, i)))
        stipa_textura[-1] = 180
        highlight.set_at((j, i), tuple(stipa_textura))

mapa = load_level('map2.txt')
print(len(mapa), len(mapa[0]))


class Board:
    def __init__(self, coords, mapa):
        mapa.insert(0, 's' * len(mapa[0]))
        mapa.append('s' * len(mapa[0]))
        for i in range(len(mapa)):
            mapa[i] = 's' + mapa[i] + 's'
        self.width = len(mapa[0])
        self.height = len(mapa)
        self.mapa = mapa
        self.left = False
        self.top = False
        self.clicked = False
        self.step = 1
        self.myinf = None

    def get_pos(self, coords):
        return [coords[1] * image_size + self.left, coords[0] * image_size + self.top]

    def create_hero(self, group, coords, texture, dmg, hp, team, movep=1, bonus=[], attack_range=1):
        self.board[coords[0] + 1][coords[1] + 1] = \
            Hero(group, [coords[0] + 1, coords[1] + 1],
                 texture, dmg, hp, team, movep, bonus, attack_range)

    def create_castle(self, group, coords, texture, max_hp, team):
        self.board[coords[0] + 1][coords[1] + 1] = \
            Castle(group, [coords[0] + 1, coords[1] + 1], texture, max_hp, team)

    def render(self):
        self.board = []
        for c_i, i in enumerate(self.mapa):
            self.board.append([])
            for c_j, j in enumerate(i):
                if j == 'g':
                    Ground(land, [c_j, c_i], 'grass')
                    self.board[-1].append(0)
                elif j == 'c' or j == 'o':
                    Ground(land, [c_j, c_i], 'box')
                    self.board[-1].append(1)
                elif j == 's':
                    Ground(land, [c_j, c_i], 'sand')
                    self.board[-1].append(1)

    def abort(self):
        self.clicked = False
        for i in highlights:
            highlights.remove(i)
        for i in lines:
            lines.remove(i)

    def get_cell(self, mouse_pos):
        y_cell = (mouse_pos[1] - self.top) // image_size
        x_cell = (mouse_pos[0] - self.left) // image_size
        if 0 <= x_cell < self.width and 0 <= y_cell < self.height:
            return [y_cell, x_cell]
        return None

    def change_step(self):
        for i in heros:
            i.obnulyay()
        self.check_bonus()
        self.step = 2 if self.step == 1 else 1

    def check_bonus(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                cur_cell = self.board[i][j]
                if cur_cell.__class__ == Hero:
                    for z in cur_cell.bonus:
                        ry1 = i - z.range
                        ry1 = 0 if ry1 < 0 else ry1
                        ry2 = i + z.range + 1
                        ry2 = self.height if ry2 >= self.height else ry2
                        rx1 = j - z.range
                        rx1 = 0 if rx1 < 0 else rx1
                        rx2 = j + z.range + 1
                        rx2 = self.width if rx2 >= self.width else rx2
                        for y in range(len(self.board))[ry1:ry2]:
                            for x in range(len(self.board[y]))[rx1:rx2]:
                                if self.board[y][x].__class__ == Hero:
                                    z.do_bonus(self.board[y][x], self.step, cur_cell)

    def on_click(self, cell_coords):
        if not self.clicked:
            cur_cell = self.board[cell_coords[0]][cell_coords[1]]
            if cur_cell.__class__ == Hero and cur_cell.team == self.step and cur_cell.cur_movep != 0:
                self.clicked = cell_coords
                self.has_path(self.clicked[1], self.clicked[0])
                if cur_cell.attacked:
                    return
                if cur_cell.attack_range > 1:
                    ry1 = self.clicked[0] - cur_cell.attack_range
                    ry1 = 0 if ry1 < 0 else ry1
                    ry2 = self.clicked[0] + cur_cell.attack_range + 1
                    ry2 = self.height if ry2 >= self.height else ry2
                    rx1 = self.clicked[1] - cur_cell.attack_range
                    rx1 = 0 if rx1 < 0 else rx1
                    rx2 = self.clicked[1] + cur_cell.attack_range + 1
                    rx2 = self.width if rx2 >= self.width else rx2
                    print(ry1, ry2, rx1, rx2)
                    for y in range(len(self.board))[ry1:ry2]:
                        for x in range(len(self.board[y]))[rx1:rx2]:
                            if self.board[y][x].__class__ in [Hero, Castle] and\
                                    self.board[y][x].team != self.step:
                                Highlight([y, x])
                else:
                    for y1 in range(len(self.board)):
                        for x1 in range(len(self.board[y1])):
                            if self.board[y1][x1].__class__ in [Hero, Castle] and (
                                    self.board[y1][x1].team != cur_cell.team):
                                minim = False
                                for i in [-1, 0, 1]:
                                    for j in [-1, 0, 1]:
                                        if not (0 <= x1 + j < self.width and
                                                0 <= y1 + i < self.height):
                                            continue
                                        cur = self.was[y1 + i][x1 + j]
                                        if cur > 0:
                                            if not minim or cur < minim:
                                                minim = cur
                                if minim and minim <= cur_cell.cur_movep and\
                                        not self.board[y1][x1].attacked:
                                    Highlight([y1, x1])
            else:
                return False

        elif self.clicked:
            goal = self.board[cell_coords[0]][cell_coords[1]]
            if goal == 0:
                self.make_movement(cell_coords)
                self.abort()
                return True
            elif goal.__class__ in [Hero, Castle] and goal.team\
                    != self.board[self.clicked[0]][self.clicked[1]].team:
                self.attack(cell_coords)
                self.abort()
                return True
            else:
                return False

    def attack(self, cell_coords):
        myhero = self.board[self.clicked[0]][self.clicked[1]]
        if myhero.attack_range == 1:
            new_coords = self.make_movement(cell_coords, -1)
            if not new_coords:
                return
            myhero = self.board[new_coords[0]][new_coords[1]]
        else:
            self.has_path(self.clicked[1], self.clicked[0], above=True, goal=
            [cell_coords[0], cell_coords[1]])
            if self.was[cell_coords[0]][cell_coords[1]] - 1 > myhero.attack_range:
                return
        if myhero.cur_movep > 0 and not myhero.attacked:
            enemy_died = self.board[cell_coords[0]][cell_coords[1]].get_damage(myhero)
            myhero.attacked = True
            myhero.cur_movep -= 1
            if enemy_died:
                if myhero.attack_range == 1:
                    myhero.move(cell_coords)
                    self.board[cell_coords[0]][cell_coords[1]] = myhero
                    self.board[new_coords[0]][new_coords[1]] = 0
                    for i in healthbars:
                        i.move()
                else:
                    self.board[cell_coords[0]][cell_coords[1]] = 0
            screen.fill(GREY)
            draw_sprites(['highlights', 'lines'])
            pg.display.flip()

    def make_movement(self, cell_coords, predel=None):
        self.has_path(self.clicked[1], self.clicked[0], goal=cell_coords)
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
            my_hero.move(i)
            self.board[i[0]][i[1]] = my_hero
            self.board[last[0]][last[1]] = 0
            last = i
            for i in healthbars:
                i.move()
            screen.fill(GREY)
            draw_sprites(['highlights', 'lines'])
            pg.display.flip()
            time.sleep(0.15)
            op -= 1
        my_hero.cur_movep = op
        return [last[0], last[1]]

    def show_way(self, cell_coords):
        self.has_path(self.clicked[1], self.clicked[0], goal=cell_coords)
        for i in lines:
            lines.remove(i)
        if self.board[self.clicked[0]][self.clicked[1]].attack_range > 1 and \
                self.board[cell_coords[0]][cell_coords[1]].__class__ in [Hero, Castle]:
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
            last
            if last[1] > i[1]:
                if last[0] > i[0]:
                    Lines(lines, last, 'up_left')
                elif last[0] == i[0]:
                    Lines(lines, last, 'left')
                else:
                    Lines(lines, last, 'down_left')
            elif last[1] == i[1]:
                if last[0] > i[0]:
                    Lines(lines, last, 'up')
                elif last[0] < i[0]:
                    Lines(lines, last, 'down')
            else:
                if last[0] > i[0]:
                    Lines(lines, last, 'up_right')
                elif last[0] == i[0]:
                    Lines(lines, last, 'right')
                else:
                    Lines(lines, last, 'down_right')
            last = i
            op -= 1
        draw_sprites()
        pg.display.flip()

    def get_mouse_movement(self, mouse_pos):
        cell_pos = self.get_cell(mouse_pos)
        if cell_pos is not None:
            if self.board[cell_pos[0]][cell_pos[1]] == 0 or (self.board[cell_pos[0]][
                cell_pos[1]].__class__ in [Hero, Castle] and (self.board[cell_pos[0]][cell_pos[1]
                    ].team != self.board[self.clicked[0]][self.clicked[1]].team)):
                self.show_way(cell_pos)
            else:
                for i in lines:
                    lines.remove(i)
                draw_sprites()

    def get_click(self, mouse_pos):
        cell_pos = self.get_cell(mouse_pos)
        if cell_pos is not None:
            return self.on_click(cell_pos)
        else:
            return False

    def get_click2(self, mouse_pos):
        if self.clicked:
            self.abort()
            return
        cell_pos = self.get_cell(mouse_pos)
        if cell_pos is not None:
            self.myinf = self.board[cell_pos[0]][cell_pos[1]]
            if self.myinf.__class__ == Hero and self.myinf.team == self.step:
                self.myinf.show_inf()
            else:
                self.myinf = None

    def get_click2_up(self):
        if self.myinf is not None:
            self.myinf.hide_inf()
            self.myinf = None

    def has_path(self, x1, y1, dung=1, above=False, goal=None):
        self.was = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.was[y1][x1] = 1

        last_was = False
        while True:
            if last_was == self.was:
                break
            if goal is not None:
                if self.was[goal[0]][goal[1]] != 0:
                    break
            else:
                if self.board[y1][x1].cur_movep + self.board[y1][x1].attack_range + 1 < dung:
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
                                if (self.board[new_y][new_x] == 1 or
                                        (self.board[new_y][new_x].__class__ == Hero and
                                         [new_y, new_x] != [y1, x1] and not above)):
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
        if self.board[y1][x1].__class__ in [Hero, Castle] and (
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
        self.image = textures[texture][0]
        self.rect = self.image.get_rect()
        self.coords = coords
        self.texture_name = texture

    def change_res(self):
        global p_land
        self.rect.x = self.coords[0] * image_size + camera.center[0] - borda.width * image_size // 2
        self.rect.y = self.coords[1] * image_size + camera.center[1] - borda.height * image_size // 2
        if not (self.rect.x > width or 0 > self.rect.x + image_size or
                self.rect.y > height or 0 > self.rect.y + image_size):
            self.image = textures[self.texture_name][camera.boost - 1]
            p_land.add(self)
        return [self.rect.x, self.rect.y]


class Hero(pg.sprite.Sprite):
    def __init__(self, group, coords, texture, dmg, max_hp, team, movep, bonus, attack_range):
        super().__init__(group, all_sprites)
        self.image = pg.transform.flip(textures[texture][0], True, False)
        if team == 1:
            self.image = pg.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.texture_name = texture
        self.coords = coords
        self.change_res()
        self.dmg = dmg
        self.max_dmg = dmg
        self.max_hp = max_hp
        self.cur_hp = max_hp
        self.movep = movep
        self.bonus = bonus
        self.cur_movep = movep
        self.team = team
        self.healthbar = Healthbar(healthbars, self)
        self.attacked = False
        self.attack_range = attack_range
        self.direction = team - 1

    def change_res(self):
        global p_heros
        self.rect.x = self.coords[1] * image_size + camera.center[0] - borda.width * image_size // 2
        self.rect.y = self.coords[0] * image_size + camera.center[1] - borda.height * image_size // 2
        if not (self.rect.x > width or 0 > self.rect.x + image_size or
                self.rect.y > height or 0 > self.rect.y + image_size):
            self.image = self.image = textures[self.texture_name][camera.boost - 1]
            p_heros.add(self)

    def move(self, coords):
        if self.coords[1] < coords[1] and self.direction == 1:
            self.direction = 0
            self.image = pg.transform.flip(self.image, True, False)
        elif self.coords[1] > coords[1] and self.direction == 0:
            self.direction = 1
            self.image = pg.transform.flip(self.image, True, False)
        self.rect.x = coords[1] * image_size + borda.left
        self.rect.y = coords[0] * image_size + borda.top
        self.coords = coords

    def get_damage(self, hero, just_dmg=False):
        if not just_dmg:
            multi = 0
            for i in hero.bonus:
                multi += i.attack_bonus(hero, self)
            self.cur_hp -= (hero.dmg + multi)
        else:
            self.cur_hp -= hero
            if self.cur_hp <= 0:
                self.cur_hp = 1
        self.healthbar.check_hp()
        for i in range(image_size):
            for j in range(image_size):
                tipa_textura = list(self.image.get_at((j, i)))
                if tipa_textura[-1] != 0:
                    tipa_textura[0] += 200
                    if tipa_textura[0] > 255:
                        tipa_textura[0] = 255
                self.image.set_at((j, i), tuple(tipa_textura))
        if not just_dmg:
            if self.rect.x > hero.rect.x and hero.direction == 1:
                hero.direction = 0
                hero.image = pg.transform.flip(hero.image, True, False)
            elif self.rect.x < hero.rect.x and hero.direction == 0:
                hero.direction = 1
                hero.image = pg.transform.flip(hero.image, True, False)
        draw_sprites(['lines', 'highlights'])
        pg.display.flip()
        time.sleep(0.3)
        self.image = textures[self.texture_name][camera.boost - 1]
        if self.direction == 1:
            self.image = pg.transform.flip(self.image, True, False)
        draw_sprites(['lines', 'highlights'])
        pg.display.flip()
        if self.cur_hp <= 0:
            heros.remove(self)
            all_sprites.remove(self, self.healthbar)
            healthbars.remove(self.healthbar)
            return True
        return False

    def obnulyay(self):
        self.cur_movep = self.movep
        self.dmg = self.max_dmg
        self.attacked = False

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

    def show_inf(self):
        self.textura = self.image
        self.image = pg.transform.scale(load_image('info_fon.png'),
                                        [128 // camera.boost, 128 // camera.boost])
        font = pg.font.SysFont('miriam', int(0.21 * image_size))
        clr = WHITE if self.attacked else GREEN
        text = font.render(str(self.dmg), 0, pg.Color('blue'))
        self.image.blit(text, (int(0.43 * image_size), int(0.15 * image_size)))
        text = font.render(str(self.cur_movep), 0, WHITE)
        self.image.blit(text, (int(0.43 * image_size), int(0.43 * image_size)))
        self.healthbar.hide()
        draw_sprites(['lines', 'highlights'])
        pg.display.flip()

    def hide_inf(self):
        self.image = self.textura
        camera.update()
        self.healthbar.check_hp()
        draw_sprites(['lines', 'highlights'])
        pg.display.flip()


class Bonus:
    def __init__(self, name, range, power=0):
        self.name = name
        self.range = range
        self.power = power

    def do_bonus(self, hero, step, giver):
        allies = hero.team == giver.team
        if hero.team == step:
            if self.name == 'heal':
                if allies:
                    if hero.cur_hp != hero.max_hp:
                        hero.get_heal(self.power)
            if self.name == 'rot':
                if not allies:
                    hero.get_damage(self.power, just_dmg=True)
        else:
            if self.name == 'farm':
                if allies:
                    if hero != giver:
                        hero.cur_movep += self.power
            if self.name == 'moral_attack':
                if allies:
                    if hero != giver:
                        hero.dmg += self.power

    def attack_bonus(self, attacker, defense):
        if defense.__class__ == Castle:
            if self.name == 'siege':
                return self.power
        else:
            if self.name == 'dmg_to_farmer':
                for i in defense.bonus:
                    if i.name == 'dmg_from_knight':
                        return self.power
            if self.name == 'sup_dmg':
                for i in defense.bonus:
                    if i.name in ['farm', 'heal', 'moral_attack']:
                        return self.power
        return 0


class Lines(pg.sprite.Sprite):
    def __init__(self, group, coords, direction='right'):
        super().__init__(group)
        self.image = pg.transform.scale(arrows[direction], [arrows[direction].get_width() //
                                    camera.boost, arrows[direction].get_height() // camera.boost])
        self.rect = self.image.get_rect()
        self.direction = direction
        self.coords = coords
        self.change_res()

    def rotate(self, coords):
        if 'right' in self.direction:
            self.rect.x = coords[0] + image_size * 3 // 4
        elif 'left' in self.direction:
            self.rect.x = coords[0] - image_size * 2 // 4
        else:
            self.rect.x = coords[0] + image_size // 2 - 5
        if 'down' in self.direction:
            self.rect.y = coords[1] + image_size * 3 // 4
        elif 'up' in self.direction:
            self.rect.y = coords[1] - image_size * 2 // 4
        else:
            self.rect.y = coords[1] + image_size // 2 - 5

    def change_res(self):
        coordx = self.coords[1] * image_size + camera.center[0] - borda.width * image_size // 2
        coordy = self.coords[0] * image_size + camera.center[1] - borda.height * image_size // 2
        self.rotate([coordx, coordy])
        self.image = pg.transform.scale(arrows[self.direction], [arrows[
                                    self.direction].get_width() // camera.boost, arrows[
            self.direction].get_height() // camera.boost])


class Healthbar(pg.sprite.Sprite):
    def __init__(self, group, owner):
        super().__init__(group, all_sprites)
        self.owner = owner
        self.check_hp()
        self.rect = self.image.get_rect()
        self.move()

    def move(self):
        global p_healthbars
        self.rect.x = self.owner.rect.x + image_size // 8
        self.rect.y = self.owner.rect.y + image_size * 4 // 5
        if not (self.rect.x > width or 0 > self.rect.x + image_size or
                self.rect.y > height or 0 > self.rect.y + image_size):
            p_healthbars.add(self)
            self.check_hp()

    def check_hp(self):
        length = int(0.75 * image_size) * self.owner.cur_hp // self.owner.max_hp
        length = 0 if length <= 0 else length
        self.image = pg.Surface([int(0.8 * image_size), int(0.21 * image_size)], pg.SRCALPHA, 32)
        self.image.fill(BLACK)
        image_hp = pg.Surface((length, int(0.15 * image_size)), pg.SRCALPHA, 32)
        image_hp.fill(team_colors[self.owner.team])
        self.image.blit(image_hp, (2, 2))
        font = pg.font.SysFont('visitor', int(0.28 * image_size))
        text = font.render(str(self.owner.cur_hp), 1, (255, 255, 255))
        self.image.blit(text, (int(0.18 * image_size), 1))

    def hide(self):
        self.image = pg.Surface((0, 0), pg.SRCALPHA, 32)


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
        self.image = pg.transform.scale(highlight, [128 // camera.boost, 128 // camera.boost])
        self.rect = self.image.get_rect()
        self.coords = coords
        self.change_res()

    def change_res(self):
        self.rect.x = self.coords[1] * image_size + camera.center[0] - borda.width * image_size // 2
        self.rect.y = self.coords[0] * image_size + camera.center[1] - borda.height * image_size // 2
        self.image = pg.transform.scale(highlight, [128 // camera.boost, 128 // camera.boost])


class Castle(pg.sprite.Sprite):
    def __init__(self, group, coords, texture, max_hp, team):
        super().__init__(group, all_sprites)
        if team == 2:
            self.image = pg.transform.flip(textures[texture][0], True, False)
        else:
            self.image = textures[texture][0]
        self.rect = self.image.get_rect()
        self.coords = coords
        self.texture_name = texture
        self.change_res()
        self.max_hp = max_hp
        self.cur_hp = max_hp
        self.team = team
        self.healthbar = Healthbar(healthbars, self)
        self.attacked = False

    def change_res(self):
        global p_castles
        self.rect.x = self.coords[1] * image_size + camera.center[0] - borda.width * image_size // 2
        self.rect.y = self.coords[0] * image_size + camera.center[1] - borda.height * image_size // 2
        if not (self.rect.x > width or 0 > self.rect.x + image_size or
                self.rect.y > height or 0 > self.rect.y + image_size):
            self.image = self.image = textures[self.texture_name][camera.boost - 1]
            p_castles.add(self)

    def get_damage(self, hero):
        multi = 0
        for i in hero.bonus:
            multi += i.attack_bonus(hero, self)
        self.cur_hp -= (hero.dmg + multi)
        self.healthbar.check_hp()
        for i in range(image_size):
            for j in range(image_size):
                tipa_textura = list(self.image.get_at((j, i)))
                if tipa_textura[-1] != 0:
                    tipa_textura[0] += 200
                    if tipa_textura[0] > 255:
                        tipa_textura[0] = 255

                self.image.set_at((j, i), tuple(tipa_textura))
        if self.rect.x > hero.rect.x and hero.direction == 1:
            hero.direction = 0
            hero.image = pg.transform.flip(hero.image, True, False)
        elif self.rect.x < hero.rect.x and hero.direction == 0:
            hero.direction = 1
            hero.image = pg.transform.flip(hero.image, True, False)
        draw_sprites(['lines', 'highlights'])
        pg.display.flip()
        time.sleep(0.3)
        self.image = textures[self.texture_name][camera.boost - 1]
        draw_sprites(['lines', 'highlights'])
        pg.display.flip()
        if self.cur_hp <= 0:
            castles.remove(self)
            all_sprites.remove(self, self.healthbar)
            healthbars.remove(self.healthbar)
            end_screen(self.team)
            return True
        return False


class Camera:
    def __init__(self):
        self.boost = 2
        self.center = [960, 540]

    def move_cam(self, changes):
        #t1 = time.time()
        global p_land, p_castles, p_healthbars, p_heros
        p_land = pg.sprite.Group()
        p_heros = pg.sprite.Group()
        p_healthbars = pg.sprite.Group()
        p_castles = pg.sprite.Group()
        borda.left = False
        borda.top = False
        scaling = 128 // camera.boost
        for x in [heros, castles, land, highlights]:
            for i in x:
                i.rect.x += changes[0]
                i.rect.y += changes[1]
                if not (i.rect.x > width or 0 > i.rect.x + image_size or
                        i.rect.y > height or 0 > i.rect.y + image_size):
                    if i.__class__ == Highlight:
                        i.change_res()
                    else:
                        i.image = textures[i.texture_name][self.boost - 1]
                    if i.__class__ == Ground:
                        p_land.add(i)
                    if i.__class__ == Hero:
                        if i.direction == 1:
                            i.image = pg.transform.flip(i.image, True, False)
                        p_heros.add(i)
                    if i.__class__ == Castle:
                        p_castles.add(i)
                if i.__class__ == Ground:
                    if not borda.left or i.rect.x < borda.left:
                        borda.left = i.rect.x
                    if not borda.top or i.rect.y < borda.top:
                        borda.top = i.rect.y
        for i in healthbars:
            i.move()
            if not (i.rect.x > width or 0 > i.rect.x + image_size or
                    i.rect.y > height or 0 > i.rect.y + image_size):
                    p_healthbars.add(i)
        #print(time.time() - t1)

    def update(self):
        global image_size
        global p_land, p_castles, p_healthbars, p_heros
        p_land = pg.sprite.Group()
        p_heros = pg.sprite.Group()
        p_healthbars = pg.sprite.Group()
        p_castles = pg.sprite.Group()
        image_size = 128 // camera.boost
        borda.left = False
        borda.top = False
        for x in [heros, castles, land, highlights]:
            for i in x:
                a = i.change_res()
                if a is not None:
                    if not borda.left or a[0] < borda.left:
                        borda.left = a[0]
                    if not borda.top or a[1] < borda.top:
                        borda.top = a[1]
                if i.__class__ == Hero and i.direction == 1:
                    i.image = pg.transform.flip(i.image, True, False)
        for x in healthbars:
            x.move()

    def zoom(self, pos):
        if self.boost < 5:
            self.boost += 1
            r_x, r_y = camera.center[0] - 960, camera.center[1] - 540
            camera.center[0] = camera.center[0] - r_x // camera.boost
            camera.center[1] = camera.center[1] - r_y // camera.boost
            return True
        return False

    def unzoom(self, pos):
        if self.boost > 1:
            self.boost -= 1
            r_x, r_y = camera.center[0] - pos[0], camera.center[1] - pos[1]
            camera.center[0] = camera.center[0] + r_x // camera.boost
            camera.center[1] = camera.center[1] + r_y // camera.boost
            return True
        return False


def end_screen(name):
    global running
    running = False
    name_text = 'КОМАНДОЙ СИНИХ' if name == 2 else 'КОМАНДОЙ КРАСНЫХ'
    text = ["ПОБЕДА", 'ЗА', name_text]
    image = 'fon.jpg' if name == 1 else 'fon_blue.jpg'
    fon = pg.transform.scale(load_image(image), (width, height))
    screen.blit(fon, (0, 0))
    font = pg.font.SysFont('visitor', 140)
    text_coord = [i + 100 for i in[25, 250, 500]]
    text_coord2 = [400, 540, 100]
    for i, line in enumerate(text):
        rendered_string = font.render(line, 1, BLACK)
        text_rect = rendered_string.get_rect()
        text_rect.top = text_coord[i]
        text_rect.x = text_coord2[i]
        screen.blit(rendered_string, text_rect)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                terminate()
        pg.display.flip()


running = True

pg.init()
width, height = size = [1920, 1080]
#width, height = size = [1080, 720]
screen = pg.display.set_mode(size, pg.FULLSCREEN)
#screen = pg.display.set_mode(size)

clock = pg.time.Clock()

camera = Camera()

all_sprites = pg.sprite.Group()
land = pg.sprite.Group()
heros = pg.sprite.Group()
healthbars = pg.sprite.Group()
buttons = pg.sprite.Group()
highlights = pg.sprite.Group()
lines = pg.sprite.Group()
castles = pg.sprite.Group()

Button(buttons, [width // 2 - 96, 692], 'turn')

screen.fill(GREY)

MYEVENTTYPE = 19
ADDEVENT = 10
speed = 1000

pg.time.set_timer(ADDEVENT, 40)

pg.mouse.set_visible(True)

borda = Board([image_size, 0], mapa)
borda.render()


borda.create_hero(heros, [1, 2], 'cavalry', 15, 120, 1, movep=5)
borda.create_hero(heros, [7, 2], 'cavalry', 15, 120, 1, movep=5)
borda.create_hero(heros, [2, 0], 'archer', 15, 80, 1, movep=3, attack_range=3)
borda.create_hero(heros, [6, 0], 'archer', 15, 80, 1, movep=3, attack_range=3)
borda.create_hero(heros, [3, 1], 'knight', 20, 120, 1, movep=3)
borda.create_hero(heros, [5, 1], 'knight', 20, 120, 1, movep=3)
borda.create_hero(heros, [5, 0], 'farmer', 5, 80, 1, movep=3, bonus=[Bonus('farm', 2, 1)])
borda.create_hero(heros, [3, 0], 'medic', 5, 80, 1, movep=3, bonus=[Bonus('heal', 2, 10)])
borda.create_hero(heros, [4, 2], 'moraler', 5, 80, 1, movep=3,
                  bonus=[Bonus('moral_attack', 2, 15)])
borda.create_hero(heros, [8, 0], 'sneaker', 10, 80, 1, movep=4,
                  bonus=[Bonus('sup_dmg', 2, 25)])
borda.create_hero(heros, [4, 0], 'trebushet', 10, 80, 1, movep=3,
                  bonus=[Bonus('siege', 2, 20)], attack_range=2)
borda.create_castle(castles, [4, -1], 'castle', 150, 1)

borda.create_hero(heros, [1, 3], 'cavalry', 15, 120, 2, movep=5)
# -----------------------------------------------------------------------------------------
borda.create_hero(heros, [1, 14], 'cavalry', 15, 120, 2, movep=5)
borda.create_hero(heros, [7, 14], 'cavalry', 15, 120, 2, movep=5)
borda.create_hero(heros, [8, 15], 'cavalry', 15, 100, 2, movep=5)
borda.create_hero(heros, [0, 15], 'cavalry', 15, 100, 2, movep=5)
borda.create_hero(heros, [2, 16], 'archer', 15, 80, 2, movep=3, attack_range=3)
borda.create_hero(heros, [6, 16], 'archer', 15, 80, 2, movep=3, attack_range=3)
borda.create_hero(heros, [3, 15], 'knight', 20, 120, 2, movep=3)
borda.create_hero(heros, [5, 15], 'knight', 20, 120, 2, movep=3)
borda.create_hero(heros, [3, 16], 'farmer', 5, 80, 2, movep=3, bonus=[Bonus('farm', 2, 1)])
borda.create_hero(heros, [5, 16], 'medic', 5, 80, 2, movep=3, bonus=[Bonus('heal', 2, 10)])
borda.create_hero(heros, [4, 14], 'moraler', 5, 80, 2, movep=3,
                  bonus=[Bonus('moral_attack', 2, 15)])
borda.create_hero(heros, [0, 16], 'sneaker', 10, 80, 2, movep=4,
                  bonus=[Bonus('sup_dmg', 2, 25)])
borda.create_hero(heros, [4, 1], 'trebushet', 10, 80, 2, movep=3,
                  bonus=[Bonus('siege', 2, 20)], attack_range=2)
borda.create_castle(castles, [4, 17], 'castle', 150, 2)

camera.update()

draw_sprites()
pg.display.flip()


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
                borda.get_click2(event.pos)
            elif event.button == 5:
                if camera.zoom(event.pos):
                    camera.update()
                borda.abort()
            elif event.button == 4:
                if camera.unzoom(event.pos):
                    camera.update()
                borda.abort()
            draw_sprites()
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                for i in buttons:
                    i.get_click2(event.pos)
            elif event.button == 3:
                borda.get_click2_up()
            draw_sprites()
        if event.type == pg.QUIT:
            terminate()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                terminate()

        if event.type == ADDEVENT:
            mouse_pos = pg.mouse.get_pos()
            changed = [0, 0]
            boost = 3
            if pg.mouse.get_focused():
                if 0 <= mouse_pos[0] < 50:
                    camera.center[0] += 10 * boost
                    changed[0] = 10 * boost
                if 0 <= mouse_pos[0] > width - 50:
                    camera.center[0] -= 10 * boost
                    changed[0] = -10 * boost
                if 0 <= mouse_pos[1] < 50:
                    camera.center[1] += 10 * boost
                    changed[1] = 10 * boost
                if 0 <= mouse_pos[1] > height - 50:
                    camera.center[1] -= 10 * boost
                    changed[1] = -10 * boost
                if changed != [0, 0]:
                    camera.move_cam(changed)
                    draw_sprites()
        pg.display.flip()
