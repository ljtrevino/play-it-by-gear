import sys, os
sys.path.insert(0, os.path.abspath('..'))

from common.core import BaseWidget, run, lookup
from common.gfxutil import topleft_label, resize_topleft_label, CEllipse, CLabelRect, KFAnim, CRectangle, AnimGroup
from common.screen import ScreenManager, Screen
from common.audio import Audio
from common.mixer import Mixer

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle, Rotate, Translate, PushMatrix, PopMatrix
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label

from wavesrc import WaveFile, WaveGenerator
from colors import colors, hex_to_rgb
import time

class LevelSelectScreen(Screen):
    def __init__(self, **kwargs):
        super(LevelSelectScreen, self).__init__(**kwargs)

        Window.clearcolor = colors['grey'].rgba

        self.anim_group = AnimGroup()
        self.canvas.add(self.anim_group)

        self.label = Label(text='Play it by Gear', font_name='./fonts/PassionOne-Regular', color=(.165, .718, .792, 1))
        self.add_widget(self.label)

        self.buttons = []
        self.id_counter = 0

        self.audio = Audio(2)
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)
        self.start_time = None
        self.switch_level = None

        self.border_color = colors['dark_grey']
        self.border = Line(rectangle=(0, 0, Window.width, Window.height), width=Window.width*0.03)
        self.anim_group.add(self.border_color)
        self.anim_group.add(self.border)

        self.on_layout((Window.width, Window.height))

    def generate_buttons(self, row_pos, num_buttons, max_num_buttons, num_rows, margin):
        for i in range(num_buttons):
            self.id_counter += 1
            square_dim = min(Window.width/(max_num_buttons+2), Window.height/(num_rows+1))
            button = LevelButton(pos=(i/6*(Window.width) + margin, row_pos), size=(square_dim, square_dim), id=self.id_counter)
            self.buttons.append(button)
            self.anim_group.add(button)

    def on_touch_up(self, touch):
        for b in self.buttons:
            if b.is_clicked(touch):
                self.mixer.add(WaveGenerator(WaveFile("./data/button_press.wav")))
                self.start_time = time.time()
                edit_progress_file(b.id, 'y')
                self.switch_level = 'Level ' + str(b.id)

    def on_enter(self):
        # update button colors by regenerating buttons
        self.on_layout((Window.width, Window.height))

    def on_layout(self, winsize):
        # update level buttons
        self.anim_group.remove_all()
        self.id_counter = 0
        self.buttons = []
        self.generate_buttons(row_pos=(3 * Window.height / 5 - Window.height/10), num_buttons=4, max_num_buttons=5, num_rows=3, margin=Window.width/6)
        self.generate_buttons(row_pos=(2 * Window.height / 5 - Window.height/10), num_buttons=5, max_num_buttons=5, num_rows=3, margin=Window.width/12)
        self.generate_buttons(row_pos=(1 * Window.height / 5 - Window.height/10), num_buttons=4, max_num_buttons=5, num_rows=3, margin=Window.width/6)

        # update title label
        self.label.center_x = Window.width/2
        self.label.center_y = 5*Window.height/6
        self.label.font_size = str(Window.width//15) + 'sp'

        # update border
        self.border_color = colors['dark_grey']
        self.border = Line(rectangle=(0, 0, Window.width, Window.height), width=Window.width*0.03)
        self.anim_group.add(self.border_color)
        self.anim_group.add(self.border)

    def on_update(self):
        self.audio.on_update()
        if self.start_time and time.time() - self.start_time > 0.13:
            self.start_time = None
            self.switch_to(self.switch_level)


class LevelButton(InstructionGroup):
    def __init__(self, pos, size, id):
        super(LevelButton, self).__init__()
        self.id = id
        self.add(colors[self.get_color()])
        self.rect = Rectangle(pos=pos, size=(size[0]*0.9, size[1]*0.9), texture=CoreImage('images/level-gear-' + str(id) + '.png').texture)
        self.add(self.rect)

    def get_color(self):
        # if progress file does not exist, create one
        if not os.path.isfile('progress.txt'):
            create_progress_file()

        parsed_file = open('progress.txt').read().split()
        id_str = str(self.id) if len(str(self.id)) == 2 else "0" + str(self.id)
        color = parsed_file[parsed_file.index(id_str) + 1]
        return color

    def is_clicked(self, touch):
        return self.rect.pos[0] < touch.x < self.rect.pos[0] + self.rect.size[0] \
        and self.rect.pos[1] < touch.y < self.rect.pos[1] + self.rect.size[1]


####################################
###    PROGRESS FILE FUNCTIONS   ###
####################################
def create_progress_file():
    f = open('progress.txt', 'a+')  # open file in append mode
    file_content = ''
    for i in range(1,14):
        if i < 10:
            file_content += '0'
        file_content += str(i) + ' ' + 'b' + '\n'
    f.write(file_content)
    f.close()

def edit_progress_file(level, new_char):
    # b means blue (for never entered)
    # y means yellow (for attempted)
    # g means green (for completed)
    with open('progress.txt', 'r') as file :
        filedata = file.read()

    # only overwrite if going from blue (never attempted) => yellow (attempted)
    # or from yellow (attempted) => green (completed) or from yellow (attempted) => red (failed)
    # or from red (failed) ==> green (completed)
    current_char = filedata[level*5 - 2]
    if (current_char == 'b' and new_char == 'y') or (current_char == 'y' and new_char == 'g') or (current_char == 'r' and new_char == 'g') or (current_char == 'y' and new_char == 'r'):
        i = level*5 - 2
        filedata = filedata[:i] + new_char + filedata[i + 1:]

    with open('progress.txt', 'w') as file:
        file.write(filedata)
