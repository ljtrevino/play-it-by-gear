import sys, os
sys.path.insert(0, os.path.abspath('..'))

from common.core import BaseWidget, run, lookup
from common.gfxutil import topleft_label, resize_topleft_label, CEllipse, CLabelRect, KFAnim, CRectangle, AnimGroup
from common.audio import Audio
from common.mixer import Mixer

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle, Rotate, Translate, PushMatrix, PopMatrix
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label

from colors import colors, hex_to_rgb
from level_select import edit_progress_file
import time
from wavesrc import WaveFile, WaveGenerator

class GearArea(InstructionGroup):
    def __init__(self):
        super(GearArea, self).__init__()
        # gear container
        self.gear_area = Rectangle()
        self.add(colors['dark_grey'])
        self.add(self.gear_area)

        size_dim = min(Window.width/6, Window.height/6)
        self.position = (Window.width, Window.height)
        self.size = (Window.width/2, Window.height - (size_dim + Window.height/25))
        self.max_x = 0

        self.on_layout((Window.width, Window.height))

    def on_layout(self, winsize):
        size_dim = min(Window.width/6, Window.height/6)
        self.gear_area.pos = (0, size_dim + Window.height/25)
        self.position = (0, size_dim + Window.height/25)
        self.gear_area.size = (Window.width/2, Window.height - (size_dim + Window.height/25))
        self.size = (Window.width/2, Window.height - (size_dim + Window.height/25))
        self.max_x = Window.width/2

class MusicBoxArea(InstructionGroup):
    def __init__(self):
        super(MusicBoxArea, self).__init__()
        # gear container
        self.music_box_area = Rectangle()
        self.add(colors['dark_brown'])
        self.add(self.music_box_area)

        self.border = Line(width=Window.width*0.01)
        self.add(colors['light_brown'])
        self.add(self.border)

        self.on_layout((Window.width, Window.height))

    def on_layout(self, winsize):
        size_dim = min(Window.width/6, Window.height/6)
        self.music_box_area.pos = (Window.width//2, size_dim + Window.height/25)
        self.music_box_area.size = (Window.width/2, Window.height - (size_dim + Window.height/25))
        self.border.rectangle = (Window.width//2 + self.border.width/2, size_dim + Window.height/25 + self.border.width/2, Window.width/2-self.border.width/2, Window.height - (size_dim + Window.height/25) - self.border.width/2)


class LevelOptions(InstructionGroup):
    def __init__(self, level, goal_music_seq, duration, edit_goal_play_status=None):
        super(LevelOptions, self).__init__()
        self.level = level # level number
        self.audio = Audio(2)
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)

        self.options_bar = Rectangle(pos = (0,0))
        self.home_button = Rectangle(texture=CoreImage('images/home.png').texture)
        self.play_button = Rectangle(texture=CoreImage('images/play.png').texture)
        self.reset_button = Rectangle(texture=CoreImage('images/reset.png').texture)
        self.check_button = Rectangle(texture=CoreImage('images/check.png').texture)
        self.on_layout((Window.width, Window.height))

        self.add(colors['grey'])
        self.add(self.options_bar)
        self.add(colors['green'])
        self.add(self.home_button)
        self.add(self.play_button)
        self.add(self.reset_button)
        self.add(self.check_button)

        self.is_playing = False
        self.start_time = None
        self.duration = 0
        self.goal_music_seq = None

        self.duration_circle = Line()
        self.add(self.duration_circle)

        # true iff you recently lost or won the game
        self.win_or_lose = False

        self.win_gen = WaveGenerator(WaveFile("./data/win_sound.wav"))
        self.lose_gen = WaveGenerator(WaveFile("./data/lose_sound.wav"))

        self.goal_music_seq = goal_music_seq
        self.duration = duration

        self.button_press_time = None

        self.edit_goal_play_status = edit_goal_play_status


    def on_layout(self, winsize):
        size_dim = min(Window.width/6, Window.height/6)
        self.options_bar.size = (Window.width, size_dim + Window.height/25)
        self.home_button.pos = (Window.width - 5*size_dim, Window.height/50)
        self.home_button.size = (size_dim, size_dim)
        self.play_button.pos = (Window.width - 3.75*size_dim, Window.height/50)
        self.play_button.size = (size_dim, size_dim)
        self.reset_button.pos = (Window.width - 2.5*size_dim, Window.height/50)
        self.reset_button.size = (size_dim, size_dim)
        self.check_button.pos = (Window.width - 1.25*size_dim, Window.height/50)
        self.check_button.size = (size_dim, size_dim)


    def on_touch_up(self, switch_screen, gear_music_seq, level_complete, win_particle, you_win_label, lose_particle, you_lose_label, reset_fn, touch):

        self.switch_screen = switch_screen

        def reset():
            reset_fn()
            win_particle.stop()
            you_win_label.text = ' '
            lose_particle.stop()
            you_lose_label.text = ' '
            if self.win_gen in self.mixer.generators:
                self.mixer.remove(self.win_gen)
            elif self.lose_gen in self.mixer.generators:
                self.mixer.remove(self.lose_gen)

        # When you win/you lose is displayed, clicking anywhere on the
        # screen should bring you back to the home screen
        if self.win_or_lose:
            reset()
            switch_screen('level_select')
            self.win_or_lose = False

        elif self.is_clicked(self.home_button, touch):
            # play button press sound
            self.mixer.add(WaveGenerator(WaveFile("./data/button_press.wav")))
            self.button_press_time = time.time()
            # go back to level select screen
            reset()

        elif self.is_clicked(self.play_button, touch):
            # play button press sound
            self.mixer.add(WaveGenerator(WaveFile("./data/button_press.wav")))

            if self.edit_goal_play_status:
                self.edit_goal_play_status('started')

            # play/stop goal music
            self.is_playing = not self.is_playing
            if self.is_playing:
                self.goal_music_seq.start()
                self.start_time = time.time()
                self.play_button.texture=CoreImage('images/stop.png').texture
            else:
                self.goal_music_seq.stop()
                self.start_time = None
                self.play_button.texture=CoreImage('images/play.png').texture

        elif self.is_clicked(self.reset_button, touch):
            # play button press sound
            self.mixer.add(WaveGenerator(WaveFile("./data/button_press.wav")))
            # reset gear positions
            reset()

        elif self.is_clicked(self.check_button, touch):
            # play button press sound
            self.mixer.add(WaveGenerator(WaveFile("./data/button_press.wav")))

            # if gear placement is correct
            self.win_or_lose = True

            self.goal_music_seq.stop()
            if gear_music_seq:
                gear_music_seq.stop()

            if level_complete:
                # show particle effect, you win label, and play sound
                win_particle.start()
                you_win_label.text = 'YOU WIN'
                edit_progress_file(self.level, 'g')
                # generate and play winning music
                self.win_gen = WaveGenerator(WaveFile("./data/win_sound.wav"))
                self.mixer.add(self.win_gen)
            else:
                lose_particle.start()
                you_lose_label.text = 'YOU LOSE'
                edit_progress_file(self.level, 'r')
                self.lose_gen = WaveGenerator(WaveFile("./data/lose_sound.wav"))
                self.mixer.add(self.lose_gen)

    def on_update(self):
        self.audio.on_update()

        if self.button_press_time and time.time() - self.button_press_time > 0.13:
            self.button_press_time = None
            self.switch_screen('level_select')


        # if goal sound played completely, switch back to play icon
        if self.start_time and time.time() - self.start_time >= self.duration:
            self.goal_music_seq.stop()
            self.is_playing = False
            self.play_button.texture=CoreImage('images/play.png').texture
            self.duration_circle.width = 0.01

            if self.edit_goal_play_status:
                self.edit_goal_play_status('finished')

        elif self.start_time and self.is_playing:
            size_dim = min(Window.width/6, Window.height/6)
            self.duration_circle.width = 10
            self.duration_circle.circle = (Window.width - 3.25*size_dim, Window.height/50 + size_dim/2, size_dim/2, 0, (self.start_time and time.time() - self.start_time) / self.duration * 360)
        else:
            self.duration_circle.width = 0.01

    def is_clicked(self, button, touch):
        return button.pos[0] < touch.x < button.pos[0] + button.size[0] \
        and button.pos[1] < touch.y < button.pos[1] + button.size[1]



class HardLevelOptions(InstructionGroup):
    def __init__(self, level, goal_music_seqs, duration, edit_goal_play_status=None):
        super(HardLevelOptions, self).__init__()
        self.level = level # level number
        self.audio = Audio(2)
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)

        self.options_bar = Rectangle(pos = (0,0))
        self.home_button = Rectangle(texture=CoreImage('images/home.png').texture)
        self.play_button = Rectangle(texture=CoreImage('images/play.png').texture)
        self.reset_button = Rectangle(texture=CoreImage('images/reset.png').texture)
        self.check_button = Rectangle(texture=CoreImage('images/check.png').texture)
        self.on_layout((Window.width, Window.height))

        self.add(colors['grey'])
        self.add(self.options_bar)
        self.add(colors['green'])
        self.add(self.home_button)
        self.add(self.play_button)
        self.add(self.reset_button)
        self.add(self.check_button)

        self.is_playing = False
        self.start_time = None
        self.duration = 0
        self.goal_music_seqs = None

        self.duration_circle = Line()
        self.add(self.duration_circle)

        # true iff you recently lost or won the game
        self.win_or_lose = False

        self.win_gen = WaveGenerator(WaveFile("./data/win_sound.wav"))
        self.lose_gen = WaveGenerator(WaveFile("./data/lose_sound.wav"))

        self.goal_music_seqs = goal_music_seqs
        self.duration = duration

        self.button_press_time = None

        self.edit_goal_play_status = edit_goal_play_status


    def on_layout(self, winsize):
        size_dim = min(Window.width/6, Window.height/6)
        self.options_bar.size = (Window.width, size_dim + Window.height/25)
        self.home_button.pos = (Window.width - 5*size_dim, Window.height/50)
        self.home_button.size = (size_dim, size_dim)
        self.play_button.pos = (Window.width - 3.75*size_dim, Window.height/50)
        self.play_button.size = (size_dim, size_dim)
        self.reset_button.pos = (Window.width - 2.5*size_dim, Window.height/50)
        self.reset_button.size = (size_dim, size_dim)
        self.check_button.pos = (Window.width - 1.25*size_dim, Window.height/50)
        self.check_button.size = (size_dim, size_dim)


    def on_touch_up(self, switch_screen, gear_music_seqs, level_complete, win_particle, you_win_label, lose_particle, you_lose_label, reset_fn, touch):

        self.switch_screen = switch_screen

        def reset():
            reset_fn()
            win_particle.stop()
            you_win_label.text = ' '
            lose_particle.stop()
            you_lose_label.text = ' '
            if self.win_gen in self.mixer.generators:
                self.mixer.remove(self.win_gen)
            elif self.lose_gen in self.mixer.generators:
                self.mixer.remove(self.lose_gen)

        # When you win/you lose is displayed, clicking anywhere on the
        # screen should bring you back to the home screen
        if self.win_or_lose:
            reset()
            switch_screen('level_select')
            self.win_or_lose = False

        elif self.is_clicked(self.home_button, touch):
            # play button press sound
            self.mixer.add(WaveGenerator(WaveFile("./data/button_press.wav")))
            self.button_press_time = time.time()
            # go back to level select screen
            reset()

        elif self.is_clicked(self.play_button, touch):
            # play button press sound
            self.mixer.add(WaveGenerator(WaveFile("./data/button_press.wav")))

            if self.edit_goal_play_status:
                self.edit_goal_play_status('started')

            # play/stop goal music
            self.is_playing = not self.is_playing
            if self.is_playing:
                for seq in self.goal_music_seqs:
                    seq.start()
                self.start_time = time.time()
                self.play_button.texture=CoreImage('images/stop.png').texture
            else:
                for seq in self.goal_music_seqs:
                    seq.stop()
                self.start_time = None
                self.play_button.texture=CoreImage('images/play.png').texture

        elif self.is_clicked(self.reset_button, touch):
            # play button press sound
            self.mixer.add(WaveGenerator(WaveFile("./data/button_press.wav")))
            # reset gear positions
            reset()

        elif self.is_clicked(self.check_button, touch):
            # play button press sound
            self.mixer.add(WaveGenerator(WaveFile("./data/button_press.wav")))

            # if gear placement is correct
            self.win_or_lose = True

            for seq in self.goal_music_seqs:
                seq.stop()

            if gear_music_seqs:
                for seq in self.gear_music_seqs:
                    seq.stop()

            if level_complete:
                # show particle effect, you win label, and play sound
                win_particle.start()
                you_win_label.text = 'YOU WIN'
                edit_progress_file(self.level, 'g')
                # generate and play winning music
                self.win_gen = WaveGenerator(WaveFile("./data/win_sound.wav"))
                self.mixer.add(self.win_gen)
            else:
                lose_particle.start()
                you_lose_label.text = 'YOU LOSE'
                edit_progress_file(self.level, 'r')
                self.lose_gen = WaveGenerator(WaveFile("./data/lose_sound.wav"))
                self.mixer.add(self.lose_gen)

    def on_update(self):
        self.audio.on_update()

        if self.button_press_time and time.time() - self.button_press_time > 0.13:
            self.button_press_time = None
            self.switch_screen('level_select')


        # if goal sound played completely, switch back to play icon
        if self.start_time and time.time() - self.start_time >= self.duration:
            for seq in self.goal_music_seqs:
                seq.stop()
            self.is_playing = False
            self.play_button.texture=CoreImage('images/play.png').texture
            self.duration_circle.width = 0.01

            if self.edit_goal_play_status:
                self.edit_goal_play_status('finished')

        elif self.start_time and self.is_playing:
            size_dim = min(Window.width/6, Window.height/6)
            self.duration_circle.width = 10
            self.duration_circle.circle = (Window.width - 3.25*size_dim, Window.height/50 + size_dim/2, size_dim/2, 0, (self.start_time and time.time() - self.start_time) / self.duration * 360)
        else:
            self.duration_circle.width = 0.01

    def is_clicked(self, button, touch):
        return button.pos[0] < touch.x < button.pos[0] + button.size[0] \
        and button.pos[1] < touch.y < button.pos[1] + button.size[1]
