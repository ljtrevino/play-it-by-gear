#pset6.py


import sys, os
sys.path.insert(0, os.path.abspath('..'))

from common.core import BaseWidget, run, lookup
from common.gfxutil import topleft_label, resize_topleft_label, CEllipse, CLabelRect, KFAnim, CRectangle

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle, Rotate, Translate, PushMatrix, PopMatrix
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage

from random import random, randint
from math import sqrt
from colors import colors, hex_to_rgb

gear_type_map = {0: 'tempo', 1: 'instrument', 2: 'pitch', 3: 'volume'}

class GearLocation(InstructionGroup):
    def __init__(self, position, size, x, y, gear_type):
        super(GearLocation, self).__init__()

        self.x = x
        self.y = y
        self.type = gear_type

        self.add(self.get_color())
        self.location_holder = CEllipse(cpos = position, csize = (size, size))
        self.add(self.location_holder)

    def on_layout(self, pos, size):
        self.location_holder.set_cpos(pos)
        self.location_holder.set_csize((size, size))

    def get_color(self):
        if self.type == 'volume':
            return colors["light_red"]
        elif self.type == 'pitch':
            return colors["light_orange"]
        elif self.type == 'tempo':
            return colors["light_purple"]
        elif self.type == 'instrument':
            return colors["light_yellow"]
        else:
            return Color(255, 255, 255)

class GearCenter(InstructionGroup):
    def __init__(self, x, y, storage_pos, box_pos, type, size, background_color):
        super(GearCenter, self).__init__()

        self.color = background_color
        self.size = size
        self.storage_pos = storage_pos
        self.box_pos = box_pos
        self.type = type
        self.x = x
        self.y = y

        self.add(self.color)
        if self.type == 'center':
            self.middle_black = CEllipse(texture=CoreImage('images/play.png').texture)
        else:
            self.middle_black = CEllipse(cpos = self.storage_pos, csize = (self.size, self.size))

        self.add(self.middle_black)

        self.is_draggable = False
        self.in_music_box = False

    def update_music_pos(self, pos):
        self.box_pos = pos

    def update_storage_pos(self, pos):
        self.storage_pos = pos

    def reset(self):
        self.middle_black.set_cpos(self.storage_pos)
        self.in_music_box = False

    def on_layout(self, pos, size):
        if self.in_music_box:
            self.middle_black.set_cpos(self.box_pos)

        else:
            self.middle_black.set_cpos(pos)

        self.middle_black.set_csize((size, size))

    def get_distance_from_center(self, touch):
        return sqrt((touch[0] - self.middle_black.get_cpos()[0])**2 + (touch[1] - self.middle_black.get_cpos()[1])**2)

    def on_touch_down(self, touch):

        distance = self.get_distance_from_center(touch)

        if distance <= self.size and distance >= self.size / 2:
            self.is_draggable = True
            self.touch_x_diff = touch[0] - self.middle_black.get_cpos()[0]
            self.touch_y_diff = touch[1] - self.middle_black.get_cpos()[1]

            return True

        return False

    def on_touch_up(self, touch, gear_box_x, can_add_gear):
        # if it was previously dragged, update it to the correct location
        if self.is_draggable:
            if touch[0] <= gear_box_x or not can_add_gear(self):
                self.middle_black.set_cpos(self.storage_pos)
                self.in_music_box = False
            else:
                self.middle_black.set_cpos(self.box_pos)
                self.in_music_box = True

        self.is_draggable = False
        return self.in_music_box

    def on_touch_move(self, touch):
        if self.is_draggable:
            self.middle_black.set_cpos((touch[0] - self.touch_x_diff, touch[1] - self.touch_y_diff))
            return True
        return False


class Gear(InstructionGroup):
    def __init__(self, x, y, size, num_teeth, gear_type, gear_value, storage_pos, box_pos, gear_id, background_color = Color(0, 0, 0), part = 0):
        super(Gear, self).__init__()

        # part is 0 for melody and 1 for bassline
        self.part = part

        self.type = gear_type # 'volume', 'pitch', 'speed', 'instrument', 'center'
        self.color = self._get_color()

        self.value = gear_value
        self.x = x
        self.y = y

        self.storage_pos = storage_pos
        self.box_pos = box_pos
        self.gear_id = gear_id
        self.size = size

        self.add(self.color)
        self.main_circle = CEllipse(cpos = self.storage_pos, csize = (self.size, self.size))
        self.add(self.main_circle)

        self.middle_size = self.size/2

        self.teeth = []
        self.num_teeth = num_teeth
        self.add_teeth(self.storage_pos, self.num_teeth)

        self.is_draggable = False
        self.in_music_box = False

        self.touch_x_diff = None
        self.touch_y_diff = None

        self.time = 0
        self.rpm = 0.1
        self.is_rotating = False

    def update_music_pos(self, pos):
        self.box_pos = pos

    def update_storage_pos(self, pos):
        self.storage_pos = pos

    def _get_color(self):
        if self.type == 'volume':
            return colors["red"]
        elif self.type == 'pitch':
            return colors["orange"]
        elif self.type == 'tempo':
            return colors["purple"]
        elif self.type == 'center':
            return Color(rgb=hex_to_rgb('#5e6f81'))
        elif self.type == 'center1':
            return colors["trout"]
        else:
            return colors["yellow"]

    def add_teeth(self, center, num_teeth):
        for tooth in self.teeth:
            self.remove(tooth)

        self.teeth = []
        self.add(self.color)
        self.add(PushMatrix())
        self.add(Translate(center))

        # use this Rotate to animate rotation for the whole flower
        self.rot = Rotate(angle = 0, origin = self.storage_pos)
        self.add(self.rot)

        # make petals ellipses with these width and height:
        self.middle_size = self.size/2
        w = self.size / 5
        h = self.size / 5

        # how much to rotate each petal.
        d_theta =  360. / num_teeth

        for n in range(num_teeth):
            self.add(Rotate(angle = d_theta, origin=center))
            self.add(Translate(self.middle_size, 0))
            rect = CRectangle(cpos = center, csize = (h, w))
            self.teeth.append(rect)
            self.add(rect)
            self.add(Translate(-self.middle_size, 0))

        self.add(PopMatrix())

    def on_layout(self, pos, size):
        self.size = size
        if self.in_music_box:
            self._update_graphics(self.box_pos)
            self.rot.origin = self.box_pos
        else:
            self._update_graphics(pos)
            self.rot.origin = pos

        self.main_circle.set_csize((size, size))

    def stop(self):
        self.is_rotating = False

    def toggle_rotate(self):
        self.is_rotating = not self.is_rotating
        return self.is_rotating

    def _update_graphics(self, position):
        self.main_circle.set_cpos(position)
        self.add_teeth(position, self.num_teeth)

    def reset(self):
        self._update_graphics(self.storage_pos)
        self.rot.origin = self.storage_pos
        self.in_music_box = False

    def get_distance_from_center(self, touch):
        return sqrt((touch[0] - self.main_circle.get_cpos()[0])**2 + (touch[1] - self.main_circle.get_cpos()[1])**2)

    def on_touch_down(self, touch):
        distance = self.get_distance_from_center(touch)

        if distance <= self.size / 2 and distance >= self.middle_size / 2:
            self.is_draggable = True
            self.touch_x_diff = touch[0] - self.main_circle.get_cpos()[0]
            self.touch_y_diff = touch[1] - self.main_circle.get_cpos()[1]

            return True

        if self.type == 'center' and distance <= self.size:
            self.is_draggable = True
            self.touch_x_diff = touch[0] - self.main_circle.get_cpos()[0]
            self.touch_y_diff = touch[1] - self.main_circle.get_cpos()[1]
            return True

        return False

    def on_touch_up(self, touch, gear_box_x, can_add_gear):
        # if it was previously dragged, update it to the correct location
        if self.is_draggable:
            if touch[0] <= gear_box_x or not can_add_gear(self):
                self._update_graphics(self.storage_pos)
                self.rot.origin = self.storage_pos
                self.in_music_box = False
            else:
                self._update_graphics(self.box_pos)
                self.rot.origin = self.box_pos
                self.in_music_box = True

        self.is_draggable = False
        return self.in_music_box

    def on_touch_move(self, touch):
        if self.is_draggable:
            self._update_graphics((touch[0] - self.touch_x_diff, touch[1] - self.touch_y_diff))
            self.rot.origin = (touch[0] - self.touch_x_diff, touch[1] - self.touch_y_diff)
            return True
        return False

    def on_update(self, dt, multiple = False):
        if not multiple:
            if self.type == 'center':
                direction = -1
            else:
                direction = 1
        else:
            if self.type == 'center':
                direction = -1
            elif self.type == 'center1':
                direction = 1
            else:
                direction = -1

        if self.is_rotating:
            degrees_per_sec = self.rpm * 360 / 60
            self.rot.angle = degrees_per_sec * self.time
            self.time += direction * dt
