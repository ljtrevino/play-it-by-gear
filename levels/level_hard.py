import sys, os, math, time
sys.path.insert(0, os.path.abspath('..'))

from common.core import BaseWidget, run, lookup
from common.gfxutil import topleft_label, resize_topleft_label, CEllipse, CLabelRect, KFAnim, CRectangle, AnimGroup
from common.screen import ScreenManager, Screen
from common.audio import Audio
from common.synth import Synth
from common.clock import SimpleTempoMap, AudioScheduler
from common.kivyparticle import ParticleSystem

from gear import gear_type_map, Gear, GearCenter, GearLocation
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle, Rotate, Translate, PushMatrix, PopMatrix
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label

from level_setup import GearArea, MusicBoxArea, HardLevelOptions
from colors import colors, hex_to_rgb
from music import MusicPlayer
from instruments import instruments

class LevelHardScreen(Screen):
    def __init__(self, level, notes, goal_values, gear_values, **kwargs):
        super(LevelHardScreen, self).__init__(**kwargs)

        # set up notes for the level
        self.notes = notes

        # set up gear values for the levels
        self.goal_values = goal_values

        # set up gear values for the levels
        self.gear_values = gear_values

        self.level = level

        # only turn on tutorial for level 1
        if self.level == 10:
            self.use_tutorial = True
            self.tutorial_screen = 'A'
            self.goal_play_status = None
            self.gear_play_status = None
            self.size_dim = min(Window.width/6, Window.height/6)
            self.tutorial_full_overlay = CRectangle(cpos=(Window.width/2, Window.height/2),csize=(Window.width, Window.height))
            self.tutorial_options_overlay = Rectangle(pos=(0,0),size=(Window.width, self.size_dim + Window.height/25))
            self.tutorial_musicbox_overlay_melody = Rectangle(pos=(Window.width//2, self.size_dim + Window.height/25 + (Window.height - (self.size_dim + Window.height/25))/2),size=(Window.width/2, (Window.height - (self.size_dim + Window.height/25))/2))
            self.tutorial_musicbox_overlay_bass = Rectangle(pos=(Window.width//2, self.size_dim + Window.height/25),size=(Window.width/2, (Window.height - (self.size_dim + Window.height/25))/2))
            self.tutorial_gearbox_overlay_melody = Rectangle(pos=(0, self.size_dim + Window.height/25),size=(Window.width/4, Window.height - (self.size_dim + Window.height/25)))
            self.tutorial_gearbox_overlay_bass = Rectangle(pos=(Window.width/4, self.size_dim + Window.height/25),size=(Window.width/4, Window.height - (self.size_dim + Window.height/25)))
            self.skip_image = CoreImage('images/skip_tutorial.png')
            self.tutorial_skip_button = Rectangle(pos=(0.98*Window.width-(self.skip_image.width*self.size_dim/300), 0.98*Window.height-self.skip_image.height*self.size_dim/300), size=(self.skip_image.width*self.size_dim/300, self.skip_image.height*self.size_dim/300), texture=self.skip_image.texture)
        else:
            self.use_tutorial = False

        ############################################
        ###              GOAL MUSIC              ###
        ############################################
        self.goal_audios = [Audio(2), Audio(2)]
        self.goal_synths = [Synth('./data/FluidR3_GM.sf2') for i in range(len(self.goal_audios))]

        # create TempoMap, AudioScheduler
        self.goal_tempo_maps = [SimpleTempoMap(120) for i in range(len(self.goal_audios))]
        self.goal_scheds = [AudioScheduler(self.goal_tempo_maps[i]) for i in range(len(self.goal_audios))]

        # connect scheduler into audio system
        for i in range(len(self.goal_audios)):
            self.goal_audios[i].set_generator(self.goal_scheds[i])
            self.goal_scheds[i].set_generator(self.goal_synths[i])

        # generate goal music
        self.goal_musics = [MusicPlayer(notes=self.notes[i], sched=self.goal_scheds[i], synth=self.goal_synths[i], channel=1, tempo_map=self.goal_tempo_maps[i]) for i in range(len(self.goal_audios))]
        for i in range(len(self.goal_audios)):
            self.goal_musics[i].update_tempo(self.goal_values[i][0])
            self.goal_musics[i].update_instrument(self.goal_values[i][1])
            self.goal_musics[i].update_pitch(self.goal_values[i][2])
            self.goal_musics[i].update_volume(self.goal_values[i][3])

        self.goal_music_seqs = [self.goal_musics[i].generate() for i in range(len(self.goal_audios))]

        ############################################
        ###              GEAR MUSIC              ###
        ############################################
        self.gear_audios = [Audio(2), Audio(2)]
        self.gear_synths = [Synth('./data/FluidR3_GM.sf2') for i in range(len(self.gear_audios))]

        # create TempoMap, AudioScheduler
        self.gear_tempo_maps  = [SimpleTempoMap(120) for i in range(len(self.gear_audios))]
        self.gear_scheds = [AudioScheduler(self.gear_tempo_maps[i]) for i in range(len(self.gear_audios))]

        # connect scheduler into audio system
        for i in range(len(self.gear_audios)):
            self.gear_audios[i].set_generator(self.gear_scheds[i])
            self.gear_scheds[i].set_generator(self.gear_synths[i])

        # generate gear music
        self.gear_musics = [MusicPlayer(notes=self.notes[i], sched=self.gear_scheds[i], synth=self.gear_synths[i], channel=1, tempo_map=self.gear_tempo_maps[i]) for i in range(len(self.gear_audios))]
        self.gear_music_seqs = []


        ############################################
        ###       BACKGROUND UI COMPONENTS       ###
        ############################################
        self.gear_area = GearArea()
        self.canvas.add(self.gear_area)

        self.music_box_area = MusicBoxArea()
        self.canvas.add(self.music_box_area)

        self.options = HardLevelOptions(level=level, goal_music_seqs=self.goal_music_seqs, duration=max(self.goal_musics[i].duration for i in range(len(self.goal_musics))), edit_goal_play_status=self.edit_goal_play_status)
        self.canvas.add(self.options)

        self.label = Label(text=kwargs['name'], font_name='./fonts/PassionOne-Regular', color=(.165, .718, .792, 1))
        self.add_widget(self.label)


        ###########################################
        ###             GEAR LABELS             ###
        ###########################################
        self.tempo_label = Label(text='Tempo (bpm)', font_name='./fonts/PassionOne-Regular', color=(0.7254901960784313, 0.5529411764705883, 0.8196078431372549, 1), center_x=(Window.width/4), center_y=(Window.height/5.25 * (0.5+0.5) + self.gear_area.position[1]), font_size=str(Window.width//50) + 'sp')
        self.instrument_label = Label(text='Instrument', font_name='./fonts/PassionOne-Regular', color=(0.996078431372549, 0.8431372549019608, 0.4, 1), center_x=(Window.width/4), center_y=(Window.height/5.25 * (1.5+0.5) + self.gear_area.position[1]), font_size=str(Window.width//50) + 'sp')
        self.pitch_label = Label(text='Pitch (semitones)', font_name='./fonts/PassionOne-Regular', color=(1.0, 0.6509803921568628, 0.09019607843137255, 1), center_x=(Window.width/4), center_y=(Window.height/5.25 * (2.5+0.5) + self.gear_area.position[1]), font_size=str(Window.width//50) + 'sp')
        self.volume_label = Label(text='Volume', font_name='./fonts/PassionOne-Regular', color=(0.9254901960784314, 0.32941176470588235, 0.3176470588235294, 1), center_x=(Window.width/4), center_y=(Window.height/5.25 * (3.5+0.5) + self.gear_area.position[1]), font_size=str(Window.width//50) + 'sp')
        self.add_widget(self.volume_label)
        self.add_widget(self.pitch_label)
        self.add_widget(self.instrument_label)
        self.add_widget(self.tempo_label)

        ###########################################
        ###          GEAR CONSTRUCTION          ###
        ###########################################

        self.gears = []
        self.gear_centers = []
        self.gears_group = AnimGroup()
        self.canvas.add(self.gears_group)


        ###########################################
        ###                GEARS                ###
        ###########################################
        self.gear_storage_locations = []
        self.gear_music_locations = []
        self.gear_labels = []
        self.set_up_gears()


        ###########################################
        ###           PARTICLE EFFECT           ###
        ###########################################
        self.win_ps = ParticleSystem('particles/star_particle.pex')
        self.win_ps.emitter_x = Window.width/2
        self.win_ps.emitter_y = Window.height/2
        self.add_widget(self.win_ps)
        self.you_win_label = Label(text=' ', font_name='./fonts/PassionOne-Regular', color=(0.5843137254901961, 0.796078431372549, 0.37254901960784315, 1), center_x=Window.width/2, center_y=Window.height/2, font_size = str(Window.width//10) + 'sp')
        self.add_widget(self.you_win_label)

        self.lose_ps = ParticleSystem('particles/lose_particle.pex')
        self.lose_ps.emitter_x = Window.width/2
        self.lose_ps.emitter_y = Window.height/2
        self.add_widget(self.lose_ps)
        self.you_lose_label = Label(text=' ', font_name='./fonts/PassionOne-Regular', color=(0.9254901960784314, 0.32941176470588235, 0.3176470588235294, 1), center_x=Window.width/2, center_y=Window.height/2, font_size = str(Window.width//10) + 'sp')
        self.add_widget(self.you_lose_label)

        ###########################################
        ###            ERROR MESSAGE            ###
        ###########################################
        self.error_msg = Label(text=' ', font_name='./fonts/PassionOne-Regular', color=(0.9254901960784314, 0.32941176470588235, 0.3176470588235294, 1), center_x=Window.width/2, center_y=Window.height/2, font_size = str(Window.width//20) + 'sp')
        self.add_widget(self.error_msg)

        # ###########################################
        # ###        ADD TUTORIAL OVERLAYS        ###
        # ###########################################
        if self.use_tutorial:
            self.canvas.add(Color(rgba=(0,0,0,0.85)))
            self.canvas.add(self.tutorial_full_overlay)
            self.tutorial_label = Label(markup=True, text="[font=./fonts/lato-bold]Welcome to the\n[/font] [font=./fonts/options-icons]|[/font] [font=./fonts/PassionOne-Regular]Play It By Gear Tutorial[/font] [font=./fonts/options-icons]|[/font] [font=./fonts/lato-bold]\n\nThe goal of this game is to make the \n goal song match the song you create by \nplacing the correct gears in a music box \n\n[/font] [font=./fonts/lato-light] (click to see the next \nstep of the tutorial)[/font]", color=(86/255, 	189/255, 205/255, 1), center_x=Window.width/2, center_y=Window.height/2, font_size = str(Window.width//40) + 'sp', halign='center')
            self.add_widget(self.tutorial_label)
            self.canvas.add(self.tutorial_skip_button)


        self.on_layout((Window.width, Window.height))


    def clear_overlays(self):
        if self.tutorial_full_overlay in self.canvas.children:
            self.canvas.remove(self.tutorial_full_overlay)
        if self.tutorial_options_overlay in self.canvas.children:
            self.canvas.remove(self.tutorial_options_overlay)
        if self.tutorial_gearbox_overlay_melody in self.canvas.children:
            self.canvas.remove(self.tutorial_gearbox_overlay_melody)
        if self.tutorial_gearbox_overlay_bass in self.canvas.children:
            self.canvas.remove(self.tutorial_gearbox_overlay_bass)
        if self.tutorial_musicbox_overlay_melody in self.canvas.children:
            self.canvas.remove(self.tutorial_musicbox_overlay_melody)
        if self.tutorial_musicbox_overlay_bass in self.canvas.children:
            self.canvas.remove(self.tutorial_musicbox_overlay_bass)
        while self.tutorial_skip_button in self.canvas.children:
            self.canvas.remove(self.tutorial_skip_button)


    def activate_overlays(self, overlay_names):
        self.clear_overlays()
        self.canvas.add(Color(rgba=(0,0,0,0.85)))
        if 'full' in overlay_names:
            self.canvas.add(self.tutorial_full_overlay)
        if 'options' in overlay_names:
            self.canvas.add(self.tutorial_options_overlay)
        if 'gearbox_melody' in overlay_names:
            self.canvas.add(self.tutorial_gearbox_overlay_melody)
        if 'gearbox_bass' in overlay_names:
            self.canvas.add(self.tutorial_gearbox_overlay_bass)
        if 'musicbox_melody' in overlay_names:
            self.canvas.add(self.tutorial_musicbox_overlay_melody)
        if 'musicbox_bass' in overlay_names:
            self.canvas.add(self.tutorial_musicbox_overlay_bass)

    def get_scaled_x_y(self, winsize, x, y):
        width, height = winsize
        # scaled_x = width/8 * (x+1)
        scaled_x = width/(len(self.gear_values)//4 * 2) * (x+0.5)
        scaled_y = height/5.25 * (y+0.5) + self.gear_area.position[1]

        return scaled_x, scaled_y

    def set_up_gears(self):
        self.gears = []
        self.gears_group.remove_all()

        center_gear_location = (Window.width / 6 * 4.5, Window.height / 4 * 2.5)
        center_gear_size = min(Window.width/12, Window.height/12)
        self.center_gear = Gear(None, None, center_gear_size, 10, 'center', 0, center_gear_location, center_gear_location, 1, colors['dark_grey'], None)
        self.canvas.add(self.center_gear.color)
        self.gears_group.add(self.center_gear)

        self.center_gear_center = GearCenter(None, None, center_gear_location, center_gear_location, 'center', center_gear_size/2, colors['dark_grey'])
        self.canvas.add(colors['dark_grey'])
        self.canvas.add(self.center_gear_center)

        melody_center_gear_loc = (center_gear_location[0], center_gear_location[1] + center_gear_size + center_gear_size/5)
        self.melody_center_gear = Gear(None, None, center_gear_size, 10, 'center1', 0, melody_center_gear_loc, melody_center_gear_loc, 1, colors['dark_grey'], None)
        self.canvas.add(self.melody_center_gear.color)
        self.gears_group.add(self.melody_center_gear)

        self.melody_center = GearCenter(None, None, melody_center_gear_loc, melody_center_gear_loc, 'center1', center_gear_size/2, colors['dark_grey'])
        self.canvas.add(colors['dark_grey'])
        self.canvas.add(self.melody_center)

        bass_center_gear_loc = (center_gear_location[0], center_gear_location[1] - center_gear_size - center_gear_size/5)
        self.bass_center_gear = Gear(None, None, center_gear_size, 10, 'center1', 0, bass_center_gear_loc, bass_center_gear_loc, 1, colors['dark_grey'], None)
        self.canvas.add(self.bass_center_gear.color)
        self.gears_group.add(self.bass_center_gear)

        self.bass_center = GearCenter(None, None, bass_center_gear_loc, bass_center_gear_loc, 'center1', center_gear_size/2, colors['dark_grey'])
        self.canvas.add(colors['dark_grey'])
        self.canvas.add(self.bass_center)

        self.play_center_gear = False

        self.music_gears = []

        tempo_location_melody = (center_gear_location[0] + center_gear_size + center_gear_size/5, center_gear_location[1] + center_gear_size + center_gear_size/5)
        instrument_location_melody = (center_gear_location[0]+center_gear_size/2 + center_gear_size/10, center_gear_location[1] + center_gear_size + center_gear_size/5 + (center_gear_size+2*center_gear_size/5)/(math.sqrt(3)) + center_gear_size/5)
        pitch_location_melody = (center_gear_location[0] - center_gear_size/2 - center_gear_size/10, center_gear_location[1] + center_gear_size + center_gear_size/5 + (center_gear_size+2*center_gear_size/5)/(math.sqrt(3)) + center_gear_size/5)
        volume_location_melody = (center_gear_location[0] - center_gear_size - center_gear_size/5, center_gear_location[1] + center_gear_size + center_gear_size/5)
        tempo_location_bass = (center_gear_location[0] + center_gear_size + center_gear_size/5, center_gear_location[1] - center_gear_size - center_gear_size/5)
        instrument_location_bass = (center_gear_location[0]+center_gear_size/2 + center_gear_size/10, center_gear_location[1] - center_gear_size - center_gear_size/5 - (center_gear_size+2*center_gear_size/5)/(math.sqrt(3)) - center_gear_size/5)
        pitch_location_bass = (center_gear_location[0]-center_gear_size/2 - center_gear_size/10, center_gear_location[1] - center_gear_size - center_gear_size/5 - (center_gear_size+2*center_gear_size/5)/(math.sqrt(3)) - center_gear_size/5)
        volume_location_bass = (center_gear_location[0] - center_gear_size - center_gear_size/5, center_gear_location[1] - center_gear_size - center_gear_size/5)

        self.music_box_gear_locations = [tempo_location_melody, instrument_location_melody, pitch_location_melody, volume_location_melody, tempo_location_bass, instrument_location_bass, pitch_location_bass, volume_location_bass]

        counter = 0

        label_font_size = min(Window.width//80, Window.height//80)
        for y in range(0, 4):
            for x in range(len(self.gear_values)//4):
                gear_type = gear_type_map[y]
                size = min(Window.width/12, Window.height/12)

                bass_addition = 0
                if counter%6 >= 3:
                    # bass values
                    bass_addition = 1

                music_pos = self.music_box_gear_locations[y+4*bass_addition]
                scaled_x, scaled_y = self.get_scaled_x_y((Window.width, Window.height), x, y)
                gear = Gear(x, y, size, 8, gear_type, self.gear_values[counter], (scaled_x, scaled_y), music_pos, 0, colors['dark_grey'], bass_addition)
                self.gears.append(gear)
                self.canvas.add(gear.color)
                self.gears_group.add(gear)

                gear_center = GearCenter(x, y, (scaled_x, scaled_y), music_pos, gear_type, size/2, colors['dark_grey'])
                self.gear_centers.append(gear_center)
                self.canvas.add(gear_center)

                ## white dots for storage purposes
                gear_loc = GearLocation((scaled_x, scaled_y), size/2, x, y, gear_type)
                self.gear_storage_locations.append(gear_loc)
                self.canvas.add(gear_loc)

                text = str(self.gear_values[counter])
                font_name = './fonts/PassionOne-Regular'
                if y == 3:
                    # get volume as percent
                    text = str(100*self.gear_values[counter] // 127) + '%'
                if y == 1:
                    # get icon for instrument
                    font_name = './fonts/music-instruments'
                    text = instruments[self.gear_values[counter]]

                label = Label(text=text, font_name=font_name, color=(0, 0, 0, 1), center_x=scaled_x, center_y=scaled_y, font_size=str(label_font_size) + 'sp')
                self.gear_labels.append(label)
                self.add_widget(label)

                counter += 1

        for indx, loc in enumerate(self.music_box_gear_locations):
            gear_type = gear_type_map[indx%4]
            gear_loc = GearLocation(loc, center_gear_size/2, None, None, gear_type)
            self.gear_music_locations.append(gear_loc)
            self.canvas.add(gear_loc)

    def edit_goal_play_status(self, value):
        if self.use_tutorial:
            if self.goal_play_status == None and value == 'started':
                self.goal_play_status = 'started'
            elif self.goal_play_status == 'started' and value == 'finished':
                self.goal_play_status = 'finished'

    def _can_add_gear(self, new_gear):
        for gear in self.music_gears:
            if gear.type == new_gear.type and gear.box_pos == new_gear.box_pos:
                return False
        return True

    def _check_music_gears(self):
        all_locs = self.music_box_gear_locations[:]
        for gear in self.music_gears:
            if gear.box_pos in all_locs:
                all_locs.remove(gear.box_pos)
        return len(all_locs) == 0

    def update_center_gear_on_layout(self, winsize):
        width, height = winsize
        center_gear_location = (width / 6 * 4.5, height / 4 * 2.5)
        center_gear_size = min(Window.width/12, Window.height/12)

        self.center_gear_center.update_storage_pos(center_gear_location)
        self.center_gear_center.update_music_pos(center_gear_location)
        self.center_gear.update_storage_pos(center_gear_location)
        self.center_gear.update_music_pos(center_gear_location)

        self.center_gear.on_layout(center_gear_location, center_gear_size)
        self.center_gear_center.on_layout(center_gear_location, center_gear_size/2)


        melody_center_gear_location = (width / 6 * 4.5, height / 4 * 2.5 + center_gear_size + center_gear_size / 5)

        self.melody_center_gear.update_storage_pos(melody_center_gear_location)
        self.melody_center_gear.update_music_pos(melody_center_gear_location)
        self.melody_center.update_storage_pos(melody_center_gear_location)
        self.melody_center.update_music_pos(melody_center_gear_location)

        self.melody_center_gear.on_layout(melody_center_gear_location, center_gear_size)
        self.melody_center.on_layout(melody_center_gear_location, center_gear_size/2)


        bass_center_gear_location = (width / 6 * 4.5, height / 4 * 2.5 - center_gear_size - center_gear_size / 5)

        self.bass_center_gear.update_storage_pos(bass_center_gear_location)
        self.bass_center_gear.update_music_pos(bass_center_gear_location)
        self.bass_center.update_storage_pos(bass_center_gear_location)
        self.bass_center.update_music_pos(bass_center_gear_location)

        self.bass_center_gear.on_layout(bass_center_gear_location, center_gear_size)
        self.bass_center.on_layout(bass_center_gear_location, center_gear_size/2)



        tempo_location_melody = (center_gear_location[0] + center_gear_size + center_gear_size/5, center_gear_location[1] + center_gear_size + center_gear_size/5)
        instrument_location_melody = (center_gear_location[0]+center_gear_size/2 + center_gear_size/10, center_gear_location[1] + center_gear_size + center_gear_size/5 + (center_gear_size+2*center_gear_size/5)/(math.sqrt(3)) + center_gear_size/5)
        pitch_location_melody = (center_gear_location[0] - center_gear_size/2 - center_gear_size/10, center_gear_location[1] + center_gear_size + center_gear_size/5 + (center_gear_size+2*center_gear_size/5)/(math.sqrt(3)) + center_gear_size/5)
        volume_location_melody = (center_gear_location[0] - center_gear_size - center_gear_size/5, center_gear_location[1] + center_gear_size + center_gear_size/5)
        tempo_location_bass = (center_gear_location[0] + center_gear_size + center_gear_size/5, center_gear_location[1] - center_gear_size - center_gear_size/5)
        instrument_location_bass = (center_gear_location[0]+center_gear_size/2 + center_gear_size/10, center_gear_location[1] - center_gear_size - center_gear_size/5 - (center_gear_size+2*center_gear_size/5)/(math.sqrt(3)) - center_gear_size/5)
        pitch_location_bass = (center_gear_location[0]-center_gear_size/2 - center_gear_size/10, center_gear_location[1] - center_gear_size - center_gear_size/5 - (center_gear_size+2*center_gear_size/5)/(math.sqrt(3)) - center_gear_size/5)
        volume_location_bass = (center_gear_location[0] - center_gear_size - center_gear_size/5, center_gear_location[1] - center_gear_size - center_gear_size/5)

        self.music_box_gear_locations = [tempo_location_melody, instrument_location_melody, pitch_location_melody, volume_location_melody, tempo_location_bass, instrument_location_bass, pitch_location_bass, volume_location_bass]


        for indx, loc in enumerate(self.gear_music_locations):
            loc.on_layout(self.music_box_gear_locations[indx], center_gear_size/2)

    def on_enter(self):
        if not self.use_tutorial and self.level == 10:
            while self.tutorial_skip_button in self.canvas.children:
                self.canvas.remove(self.tutorial_skip_button)

    def on_layout(self, winsize):
        mapped_dic = {'tempo': 0, 'instrument': 1, 'pitch': 2, 'volume': 3}
        self.update_center_gear_on_layout(winsize)

        self.size_dim = min(Window.width/6, Window.height/6)
        size = min(Window.width/12, Window.height/12)
        label_font_size = min(Window.width//80, Window.height//80)

        for loc in self.gear_storage_locations:
            scaled_x, scaled_y = self.get_scaled_x_y(winsize, loc.x, loc.y)
            loc.on_layout((scaled_x, scaled_y), size/2)

        for indx, gear in enumerate(self.gears):
            scaled_x, scaled_y = self.get_scaled_x_y(winsize, gear.x, gear.y)
            gear.update_storage_pos((scaled_x, scaled_y))
            bass_addition = 0
            if indx%6 >= 3:
                # bass values
                bass_addition = 1
            # music_pos = self.music_box_gear_locations[y+4*bass_addition]
            gear.update_music_pos(self.music_box_gear_locations[mapped_dic[gear.type]+4*bass_addition])
            gear.on_layout((scaled_x, scaled_y), size)

            self.gear_labels[indx].center_x = scaled_x
            self.gear_labels[indx].center_y = scaled_y
            self.gear_labels[indx].font_size = str(label_font_size) + 'sp'

        for center in self.gear_centers:
            scaled_x, scaled_y = self.get_scaled_x_y(winsize, center.x, center.y)
            center.update_storage_pos((scaled_x, scaled_y))
            center.update_music_pos(self.music_box_gear_locations[mapped_dic[center.type]])
            center.on_layout((scaled_x, scaled_y), size/2)

        # update level label
        self.label.center_x = self.size_dim*1.5
        self.label.center_y = self.size_dim*3/5
        self.label.font_size = str(Window.width//20) + 'sp'

        # update you win label
        self.you_win_label.center_x = (Window.width/2)
        self.you_win_label.center_y = (Window.height/2)
        self.you_win_label.font_size = str(Window.width//10) + 'sp'

        self.tempo_label.center_x=(Window.width/4)
        self.tempo_label.center_y=(Window.height/5.25 * (0.5+0.5) + self.gear_area.position[1])
        self.tempo_label.font_size=str(Window.width//50) + 'sp'
        self.instrument_label.center_x=(Window.width/4)
        self.instrument_label.center_y=(Window.height/5.25 * (1.5+0.5) + self.gear_area.position[1])
        self.instrument_label.font_size=str(Window.width//50) + 'sp'
        self.pitch_label.center_x=(Window.width/4)
        self.pitch_label.center_y=(Window.height/5.25 * (2.5+0.5) + self.gear_area.position[1])
        self.pitch_label.font_size=str(Window.width//50) + 'sp'
        self.volume_label.center_x=(Window.width/4)
        self.volume_label.center_y=(Window.height/5.25 * (3.5+0.5) + self.gear_area.position[1])
        self.volume_label.font_size=str(Window.width//50) + 'sp'

        # update child components
        self.gear_area.on_layout((Window.width, Window.height))
        self.music_box_area.on_layout((Window.width, Window.height))
        self.options.on_layout((Window.width, Window.height))

        # update particle effect and win/lose labels
        self.win_ps.emitter_x = Window.width/2
        self.win_ps.emitter_y = Window.height/2
        self.you_win_label.center_x=Window.width/2
        self.you_win_label.center_y=Window.height/2
        self.you_win_label.font_size = str(Window.width//10) + 'sp'

        self.lose_ps.emitter_x = Window.width/2
        self.lose_ps.emitter_y = Window.height/2
        self.you_lose_label.center_x=Window.width/2
        self.you_lose_label.center_y=Window.height/2
        self.you_lose_label.font_size = str(Window.width//10) + 'sp'

        # update error message location
        self.error_msg.center_x=Window.width/2
        self.error_msg.center_y=Window.height/2
        self.error_msg.font_size = str(Window.width//20) + 'sp'

        # update tutorial overlays, label, and skip button
        if self.use_tutorial:
            self.update_tutorial_screen(self.tutorial_screen)
            self.tutorial_full_overlay.cpos=(Window.width/2, Window.height/2)
            self.tutorial_full_overlay.csize=(Window.width, Window.height)
            self.tutorial_options_overlay.size=(Window.width, self.size_dim + Window.height/25)

            self.tutorial_musicbox_overlay_melody.pos=(Window.width//2, self.size_dim + Window.height/25 + (Window.height - (self.size_dim + Window.height/25))/2)
            self.tutorial_musicbox_overlay_melody.size=(Window.width/2, (Window.height - (self.size_dim + Window.height/25))/2)
            self.tutorial_musicbox_overlay_bass.pos=(Window.width//2, self.size_dim + Window.height/25)
            self.tutorial_musicbox_overlay_bass.size=(Window.width/2, (Window.height - (self.size_dim + Window.height/25))/2)

            self.tutorial_gearbox_overlay_melody.pos=(0, self.size_dim + Window.height/25)
            self.tutorial_gearbox_overlay_melody.size=(Window.width/4, Window.height - (self.size_dim + Window.height/25))
            self.tutorial_gearbox_overlay_bass.pos=(Window.width/4, self.size_dim + Window.height/25)
            self.tutorial_gearbox_overlay_bass.size=(Window.width/4, Window.height - (self.size_dim + Window.height/25))

            self.tutorial_skip_button.pos=(0.98*Window.width-(self.skip_image.width*self.size_dim/300), 0.98*Window.height-self.skip_image.height*self.size_dim/300)
            self.tutorial_skip_button.size=(self.skip_image.width*self.size_dim/300, self.skip_image.height*self.size_dim/300)


    def reset(self):
        for gear in self.gears:
            # reset gear position
            gear.reset()
            # stop gear from rotating
            gear.stop()
        # stop center gear from rotating
        self.center_gear.stop()
        # stop music
        for seq in self.goal_music_seqs:
            seq.stop()
        if self.gear_music_seqs:
            for seq in self.gear_music_seqs:
                seq.stop()

        # end tutorial
        if self.use_tutorial:
            self.tutorial_label.text = ''
            self.use_tutorial = False
            self.clear_overlays()
            while self.tutorial_skip_button in self.canvas.children:
                self.canvas.remove(self.tutorial_skip_button)


    def skip_tutorial_pressed(self, touch):
        if self.use_tutorial:
            if 0.98*Window.width-(self.skip_image.width*self.size_dim/300) < touch.pos[0] < 0.98*Window.width and 0.98*Window.height-self.skip_image.height*self.size_dim/300 < touch.pos[1] < 0.98*Window.height:
                return True
        return False


    def on_touch_up(self, touch):
        # if click is on one of the lower menu buttons, perform the appropriate action
        self.options.on_touch_up(self.switch_to, self.gear_music_seqs, self.check_level_complete(), self.win_ps, self.you_win_label, self.lose_ps, self.you_lose_label, self.reset, touch)

        for index, gear in enumerate(self.gears):
            # response is true if you click the current gear
            response = gear.on_touch_up(touch.pos, self.gear_area.max_x, self._can_add_gear)
            self.gear_centers[index].on_touch_up(touch.pos, self.gear_area.max_x, self._can_add_gear)

            if response:
                if gear not in self.music_gears:
                    self.music_gears.append(gear)
                    i = gear.part
                    # update the gear music based on the gear that is selected
                    function = 'self.gear_musics[i].update_' + gear.type + '(' + str(gear.value) + ')'
                    eval(function)

            else:
                if gear in self.music_gears:
                    self.music_gears.remove(gear)

        self.center_gear.on_touch_up(touch.pos, self.gear_area.max_x, self._can_add_gear)

        if self.use_tutorial:
            # if skip button pressed, quit out of tutorial mode
            if self.skip_tutorial_pressed(touch):
                self.use_tutorial = False
                self.remove_widget(self.tutorial_label)
                self.clear_overlays()
                while self.tutorial_skip_button in self.canvas.children:
                    self.canvas.remove(self.tutorial_skip_button)

            elif self.tutorial_screen == 'A':
                # show screen B
                self.tutorial_screen = 'B'
                self.update_tutorial_screen('B')

            elif self.tutorial_screen == 'B':
                # show screen C
                self.tutorial_screen = 'C'
                self.update_tutorial_screen('C')

            elif self.tutorial_screen == 'C':
                # show screen D
                self.tutorial_screen = 'D'
                self.update_tutorial_screen('D')

            elif self.tutorial_screen == 'D':
                self.use_tutorial = False
                self.remove_widget(self.tutorial_label)
                self.clear_overlays()
                while self.tutorial_skip_button in self.canvas.children:
                    self.canvas.remove(self.tutorial_skip_button)

    def update_tutorial_screen(self, screen):
        if not self.use_tutorial:
            return

        self.remove_widget(self.tutorial_label)

        if self.tutorial_screen == 'A':
            self.activate_overlays(['full'])
            self.tutorial_label.center_x=Window.width/2
            self.tutorial_label.center_y=Window.height/2
            self.tutorial_label.text = "[font=./fonts/lato-bold]Welcome to the first hard level!\n\n There are a few new hard level features\nof which you should be aware\n\n[/font] [font=./fonts/lato-light] (click to continue)[/font]"
            self.tutorial_label.font_size = font_size = str(Window.width//40) + 'sp'

        if self.tutorial_screen == 'B':
            self.activate_overlays(['options', 'gearbox_bass', 'gearbox_melody'])
            self.tutorial_label.center_x=1/4*Window.width
            self.tutorial_label.center_y=Window.height/2 + (min(Window.width/6, Window.height/6) + Window.height/25)/2
            self.tutorial_label.text = "[font=./fonts/lato-bold]The music box now has two\nparts: melody and bass\n\n Gears placed in the top half of\nthe music box modify the melody\n and gears placed in the bottom\nhalf modify the bass part \n\n[/font] [font=./fonts/lato-light](click to continue)[/font]"
            self.tutorial_label.font_size = font_size = str(Window.width//60) + 'sp'

        elif self.tutorial_screen == 'C':
            self.activate_overlays(['gearbox_bass', 'musicbox_bass', 'options'])
            self.tutorial_label.center_x=5/8*Window.width
            self.tutorial_label.center_y= (Window.height-(min(Window.width/6, Window.height/6) + Window.height/25))/2 - (min(Window.width/6, Window.height/6) + Window.height/25)/2
            self.tutorial_label.text = "[font=./fonts/lato-bold]Gears in the left half of the music\nbox can only be used for the melody\n\n[/font] [font=./fonts/lato-light](click to continue)[/font]"
            self.tutorial_label.font_size = font_size = str(Window.width//50) + 'sp'

        elif self.tutorial_screen == 'D':
            self.activate_overlays(['gearbox_melody', 'musicbox_melody', 'options'])
            self.tutorial_label.center_x=Window.width/2
            self.tutorial_label.center_y=(min(Window.width/6, Window.height/6) + Window.height/25)/2
            self.tutorial_label.text = "[font=./fonts/lato-bold]Gears in the right half of the music\nbox can only be used for the bass part\n[/font] [font=./fonts/lato-light](click to exit the tutorial)[/font]"
            self.tutorial_label.font_size = font_size = str(Window.width//60) + 'sp'

        self.add_widget(self.tutorial_label)
        self.canvas.add(self.tutorial_skip_button)


    def on_touch_down(self, touch):
        other_gears = False
        for index, gear in enumerate(self.gears):
            cur_gear = gear.on_touch_down(touch.pos)
            other_gears = other_gears or cur_gear
            self.gear_centers[index].on_touch_down(touch.pos)

        if other_gears:
            if self.gear_music_seqs:
                for gear in self.music_gears:
                    gear.stop()
                self.center_gear.stop()
                for seq in self.gear_music_seqs:
                    seq.stop()
                self.gear_music_seqs = []

        else:
            response = self.center_gear.on_touch_down(touch.pos)

            if response:
                if self._check_music_gears():
                    for gear in self.music_gears:
                        gear.toggle_rotate()

                    is_rotating = self.center_gear.toggle_rotate()
                    self.melody_center_gear.toggle_rotate()
                    self.bass_center_gear.toggle_rotate()

                    if is_rotating:
                        self.gear_music_seqs = [self.gear_musics[i].generate() for i in range(len(self.gear_musics))]
                        for seq in self.gear_music_seqs[::-1]:
                            seq.start()

                        if self.use_tutorial and self.gear_play_status == None:
                            self.gear_play_status = 'started'
                    else:
                        if self.gear_music_seqs:
                            for seq in self.gear_music_seqs:
                                seq.stop()
                            self.gear_music_seqs = []
                else:
                    if not self.use_tutorial:
                        self.error_msg.text = 'Place all 8 gears'

            else:
                self.error_msg.text = ' '
            return

        self.error_msg.text = ' '

    def on_touch_move(self, touch):
        for index, gear in enumerate(self.gears):
            gear.on_touch_move(touch.pos)
            self.gear_centers[index].on_touch_move(touch.pos)

    def on_update(self):
        for aud in self.goal_audios:
            aud.on_update()
        for aud in self.gear_audios:
            aud.on_update()
        self.options.on_update()

        for gear in self.gears:
            gear.on_update(1, True)

        self.center_gear.on_update(1, True)
        self.melody_center_gear.on_update(1, True)
        self.bass_center_gear.on_update(1, True)

        if self.gear_music_seqs and not self.gear_music_seqs[0].playing:
            for gear in self.music_gears:
                gear.stop()
            self.center_gear.stop()
            self.melody_center_gear.stop()
            self.bass_center_gear.stop()
            self.gear_music_seqs = []
            if self.use_tutorial and self.gear_play_status == 'started':
                self.gear_play_status = 'finished'

    def check_level_complete(self):
        return all(self.goal_musics[i].is_equal(self.gear_musics[i]) for i in range(len(self.goal_musics)))
