# pyinstaller --onefile --windowed --add-data "scoopa3W.bmp:." --add-data "doopa2.bmp.png:." your_file.py

from math import cos, sin, radians
from random import randint, choice
import sys
import os
import pyglet
from pyglet import shapes, clock, text, sprite
from pyglet.math import Vec2
from pyglet.window import key

window = pyglet.window.Window(1400, 900, resizable=True)
z = [pyglet.graphics.Group(order=x) for x in range(10)]  # z levels for layering shapes
batch = pyglet.graphics.Batch()  # rendering batch
w, h = window.width, window.height
center = (w / 2, h / 2)
keys = key.KeyStateHandler()
window.push_handlers(keys)
projectiles = []
asterisks = []
ents = [projectiles, asterisks]


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, relative_path)


def add_vec(tup1, tup2):
    (x1, y1), (x2, y2) = tup1, tup2
    return tuple((x1 + x2, y1 + y2))


def sub_vec(tup1, tup2):
    (x1, y1), (x2, y2) = tup1, tup2
    return tuple((x1 - x2, y1 - y2))


def mul_vec(tup1, tup2):
    (x1, y1), (x2, y2) = tup1, tup2
    return tuple((x1 * x2, y1 * y2))


class Player(sprite.Sprite):  # resizing this triangle is a nightmare don't do it
    def __init__(self):
        super(Player, self).__init__(
            player_img,
            x=center[0],
            y=center[1],
            batch=batch,
            group=z[9])
        self.vector = (0, 0)
        self.cooldown = 15
        self.bounds = 20

    def update(self):
        dir_x = sin(radians(self.rotation)) / 8  # don't ask me why these are reversed
        dir_y = cos(radians(self.rotation)) / 8

        if keys[key.D]:
            self.rotation += 5
        if keys[key.A]:
            self.rotation -= 5
        if keys[key.W]:
            self.vector = add_vec((dir_x, dir_y), self.vector)
        if keys[key.S]:
            self.vector = add_vec((dir_x * -1, dir_y * -1), self.vector)
        if keys[key.SPACE]:
            if self.cooldown <= 0:
                projectiles.append(Projectile(self.rotation, (self.x, self.y)))
                self.cooldown = 15

        (self.x, self.y) = add_vec(self.vector, (self.x, self.y))
        self.rotation %= 360
        self.y %= h
        self.x %= w
        self.cooldown -= 1


class Projectile(shapes.Rectangle):
    def __init__(self, r, p):
        super(Projectile, self).__init__(
            *p, 5, 20,  # (x,y) , width, height
            color=(225, 50, 30),
            batch=batch,
            group=z[8])
        self.rotation = r
        self.bounds = 15

    def update(self):
        direction = (sin(radians(self.rotation)) * 10,
                     cos(radians(self.rotation)) * 10)

        self.position = add_vec(direction, self.position)
        if self.x < 0 or self.x > w or self.y < 0 or self.y > h \
                and self in projectiles:
            print('projectile deleted')
            projectiles.remove(self)


class Asterisk(sprite.Sprite):
    def __init__(self):
        side = choice(('top', 'bottom', 'left', 'right'))  # choose a random side
        coords = {'top': (randint(0, w), h),
                  'bottom': (randint(0, w), 0),
                  'left': (0, randint(0, h)),
                  'right': (w, randint(0, h))
                  }[side]  # choose random coordinate along that side of the screen

        super(Asterisk, self).__init__(
            choice((scoopah, doopah)),
            x=coords[0],
            y=coords[1],
            batch=batch,
            blend_src=770,
            blend_dest=771,
            subpixel=False
        )
        self.bounds = 22
        self.scale = 1
        direction_player = Vec2(*sub_vec((player.x, player.y), (self.x, self.y))).normalize()
        self.vector = mul_vec(direction_player, (2.5, 2.5))

    def update(self):
        if self.x < -5 or self.x > w + 5 or self.y < -5 or self.y > h + 5 \
                and self in asterisks:
            print('asterisk deleted')
            asterisks.remove(self)

        for ent in projectiles:  # collision detection (done poorly)
            if Vec2(self.x, self.y).distance(Vec2(ent.x, ent.y)) - (self.bounds + ent.bounds) <= 0 \
                    and self in asterisks:
                score.add_score()
                print('asterisk deleted')
                asterisks.remove(self)

        self.x, self.y = add_vec(self.vector, (self.x, self.y))


class Score(text.Label):
    def __init__(self):
        self.hit_timer = 0  # Score object keeps track of a number of frames so collisions aren't duplicated
        self.score = 0
        super(Score, self).__init__(
            str(self.score),
            font_name='NotoSansArmenian-CondensedMedium',
            font_size=48,
            x=w // 2, y=h - 80,
            batch=batch, group=z[9]
        )

    def update(self):
        if self.hit_timer > 0:
            self.hit_timer -= 1

    def add_score(self):
        if self.hit_timer == 0:
            self.hit_timer = 30
            self.score += 1
            self.text = str(self.score)


@window.event
def on_draw():
    window.clear()
    batch.draw()


@window.event
def on_resize(width, height):
    global w, h, score
    w = width
    h = height
    (score.x, score.y) = (w // 2, h - 80)


def update(dt):
    score.update()
    player.update()
    for ls in ents:
        for ent in ls:
            ent.update()


scoopah = pyglet.image.load(resource_path('S.svg'))  # initialize things
doopah = pyglet.image.load(resource_path('D.svg'))
player_img = pyglet.image.load(resource_path('spaceship_low_white.svg'))
(scoopah.anchor_x, scoopah._y) = (scoopah.width // 2, scoopah.height // 2)
(doopah.anchor_x, doopah._y) = (doopah.width // 2, doopah.height // 2)
(player_img.anchor_x, player_img.anchor_y) = (player_img.width // 2, player_img.height // 2)
score = Score()
player = Player()
asterisks.append(Asterisk())
clock.schedule_interval(update, 1 / 60)
clock.schedule_interval(lambda _: asterisks.append(Asterisk()), 1)
pyglet.app.run()
