from math import cos, sin, radians, atan2, sqrt, tan
from random import randint, choice
import pyglet
from pyglet import shapes, clock, text, sprite
from pyglet.math import Vec2
from pyglet.window import key

window = pyglet.window.Window(1400, 900)
z = [pyglet.graphics.Group(order=x) for x in range(10)]  # z levels for layering shapes
batch = pyglet.graphics.Batch()  # rendering batch
w, h = window.width, window.height
center = (w / 2, h / 2)
keys = key.KeyStateHandler()
window.push_handlers(keys)
projectiles = []
asterisks = []
ents = [projectiles, asterisks]
scoopah = pyglet.image.load('scoopa3W.bmp')
doopah = pyglet.image.load('Doopa.bmp')

def add_vec(tup1, tup2):
    (x1, y1), (x2, y2) = tup1, tup2
    return tuple((x1 + x2, y1 + y2))


def sub_vec(tup1, tup2):
    (x1, y1), (x2, y2) = tup1, tup2
    return tuple((x1 - x2, y1 - y2))


def mul_vec(tup1, tup2):
    (x1, y1), (x2, y2) = tup1, tup2
    return tuple((x1 * x2, y1 * y2))


class Player(shapes.Polygon):  # resizing this triangle is a nightmare don't do it
    def __init__(self):
        super(Player, self).__init__(
            (w / 2 - 10, h / 2),  # (x1, y1)
            (w / 2, h / 2 + 30),  # (x2, y2)
            (w / 2 + 10, h / 2),  # (x3, y3)
            color=(50, 225, 30),
            batch=batch,
            group=z[9])
        self.position = center
        self.anchor_x += 10  # x center of rotation
        self.anchor_y += 15  # y center of rotation
        self.vector = (0, 0)
        self.cooldown = 15

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
                projectiles.append(Projectile(self.rotation, self.position))
                self.cooldown = 15

        self.position = add_vec(self.vector, self.position)
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

    def update(self):
        direction = (sin(radians(self.rotation)) * 10,
                     cos(radians(self.rotation)) * 10)

        self.position = add_vec(direction, self.position)
        if self.x < 0 or self.x > w or self.y < 0 or self.y > h:
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
        self.scale = 0.6

    def update(self):
        if self.x < -5 or self.x > w + 5 or self.y < -5 or self.y > h + 5:
            print('asterisk deleted')
            asterisks.remove(self)

        direction_player = Vec2(*sub_vec(player.position, (self.x, self.y))).normalize()
        direction_mult = mul_vec(direction_player, (2.5, 2.5))
        self.x, self.y = add_vec(direction_mult, (self.x, self.y))



@window.event
def on_draw():
    window.clear()
    batch.draw()


def update(dt):
    player.update()
    for ls in ents:
        for ent in ls:
            ent.update()


player = Player()
asterisks.append(Asterisk())
clock.schedule_interval(update, 1 / 60)
clock.schedule_interval(lambda _: asterisks.append(Asterisk()), 3)
pyglet.app.run()
