# Copyright 2019 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import pyglet

WHITE = [255, 255, 255, 255]
GREEN = [0, 255, 0, 123]
BLUE = [0, 0, 128, 255]
BLACK = [0, 0, 0, 255]
RED = [255, 0, 0, 123]
LIGHT = [255, 150, 150, 123]


class PygletWindow:

    def __init__(self, width, height):
        self.active = True
        self.display_surface = pyglet.window.Window(width=width, height=height)
        self.top = height
        self.main_batch = pyglet.graphics.Batch()

        pyglet.gl.glLineWidth(3)

        # make OpenGL context current
        self.display_surface.switch_to()
        self.reset()

    def text(self, text, x, y, font_size=20, color=BLACK):
        y = self.translate(y)
        label = pyglet.text.Label(text, font_size=font_size,
                                  x=x, y=y, anchor_x='left', anchor_y='top',
                                  color=color)
        label.draw()

    def translate(self, y):
        y = self.top - y
        return y

    def rectangle(self, x, y, dx, dy, color=BLACK):
        y = self.translate(y)
        self.main_batch.add(4, pyglet.gl.GL_LINE_LOOP, None,
                            ("v2f", [x, y, x + dx, y, x + dx, y - dy, x, y - dy]),
                            ('c4B', 4 * color))

    def line(self, start, end, color=BLACK):
        x, y, destx, desty = start[0], start[1], end[0], end[1]
        y = self.translate(y)
        desty = self.translate(desty)

        self.main_batch.add(2, pyglet.gl.GL_LINES, None,
                            ('v2f', [x, y, destx, desty]),
                            ('c4B', 2 * color))

    def reset(self):
        """New frame"""
        pyglet.clock.tick()
        self.display_surface.dispatch_events()
        pyglet.gl.glClearColor(1, 1, 1, 1)
        from pyglet.gl import glClear
        glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)

        self.main_batch = pyglet.graphics.Batch()

    def update(self):
        """Draw the current state on screen"""

        self.main_batch.draw()
        self.display_surface.flip()

    def close(self):
        self.display_surface.close()

if __name__ == '__main__':
    pg = PygletWindow(400, 400)

    pg.reset()
    pg.rectangle(100, 100, 50, 50)
    pg.line((10, 10), (150, 150))
    pg.text("Test", 10, 10)
    pg.text("Test2", 30, 30, color=BLACK)
    pg.update()
    input()
