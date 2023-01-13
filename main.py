from math import cos, sin, radians
import pyglet
from pyglet import shapes, clock
from pyglet.window import key

window = pyglet.window.Window(1400, 900)
z = [pyglet.graphics.Group(order=x) for x in range(10)]
batch = pyglet.graphics.Batch()
w, h = window.width, window.height
center = (w / 2, h / 2)
keys = key.KeyStateHandler()
window.push_handlers(keys)
ents = []


class Player(shapes.Polygon):
    def __init__(self):
        super(Player, self).__init__(
            (w / 2 - 20, h / 2),  # (x1, y1)
            (w / 2, h / 2 + 50),  # (x2, y2)
            (w / 2 + 20, h / 2),  # (x3, y3)
            color=(50, 225, 30),
            batch=batch,
            group=z[9])
        self.position = center
        self.anchor_x += 20  # x center of rotation
        self.anchor_y += 10  # y center of rotation
        self.vector = (0, 0)
        self.cooldown = 15

    def update(self):
        if keys[key.D]:
            self.rotation += 5
        if keys[key.A]:
            self.rotation -= 5
        if keys[key.W]:
            self.vector = tuple(sum(x) for x in
                                zip((sin(radians(self.rotation)) / 8,
                                     cos(radians(self.rotation)) / 8), self.vector))
        if keys[key.S]:
            self.vector = tuple(sum(x) for x in
                                zip((-1 * sin(radians(self.rotation)) / 8,
                                     -1 * cos(radians(self.rotation)) / 8), self.vector))
        if keys[key.SPACE]:
            if self.cooldown <= 0:
                ents.append(Projectile(self.rotation, self.position))
                self.cooldown = 15

        self.position = tuple(sum(x) for x in zip(self.vector, self.position))
        self.rotation %= 360
        self.y %= h
        self.x %= w
        self.cooldown -= 1


class Projectile(shapes.Rectangle):
    def __init__(self, r, p):
        super(Projectile, self).__init__(
            p[0], p[1], 10, 40,
            color=(225, 50, 30),
            batch=batch,
            group=z[8])
        self.rotation = r
        self.position = p

    def update(self):
        self.position = tuple(sum(x) for x in
                              zip((sin(radians(self.rotation)) * 10,
                                   cos(radians(self.rotation)) * 10),
                                  self.position))
        if self.x < 0 or self.x > w or self.y < 0 or self.y > h:
            ents.remove(self)


class Asterisk(shapes.Star):
    def __init__(self):
        super(Asterisk, self).__init__(

        )


@window.event
def on_draw():
    window.clear()
    batch.draw()


def update(dt):
    for ent in ents:
        ent.update()


ents.append(Player())
clock.schedule_interval(update, 1 / 60)
pyglet.app.run()
