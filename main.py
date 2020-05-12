from common.core import BaseWidget, run, lookup
from common.screen import ScreenManager, Screen

from notes import notes

# importing all the screens and levels
from level_select import LevelSelectScreen
from levels.level_easy_medium import LevelEasyMediumScreen
from levels.level_hard import LevelHardScreen

sm = ScreenManager()
sm.add_screen(LevelSelectScreen(name='level_select'))

###################################################
###              EASY LEVELS (1-4)              ###
###################################################
sm.add_screen(LevelEasyMediumScreen(level=1,
                              notes=notes['Level 1'],
                              goal_values=[    120,  # tempo value = bpm
                                           (0, 11),  # instrument values = program in form (a,b)
                                                 0,  # pitch values = number of semitones up
                                               110 ], # volume values = number in range (0, 127)))
                              gear_values=[   120,    180,     240,  # tempo values = bpm
                                           (0, 0), (0, 8), (0, 11),  # instrument values = program in form (a,b)
                                               -3,      0,       3,  # pitch values = number of semitones up
                                               45,      70,    110 ], # volume values = number in range (0, 127)
                              name='Level 1',
                ))

sm.add_screen(LevelEasyMediumScreen(level=2,
                              notes=notes['Level 2'],
                              goal_values=[    160,  # tempo value = bpm
                                           (0, 65),  # instrument values = program in form (a,b)
                                                -3,  # pitch values = number of semitones up
                                               70 ], # volume values = number in range (0, 127)))
                              gear_values=[   120,    160,     240,  # tempo values = bpm
                                          (0, 59), (0, 71), (0, 65),  # instrument values = program in form (a,b)
                                                -3,      0,       3,  # pitch values = number of semitones up
                                                 70,     95,    120 ], # volume values = number in range (0, 127)
                              name='Level 2',
                ))

sm.add_screen(LevelEasyMediumScreen(level=3,
                              notes=notes['Level 3'],
                              goal_values=[    80,  # tempo value = bpm
                                           (0, 60),  # instrument values = program in form (a,b)
                                                -8,  # pitch values = number of semitones up
                                                120 ], # volume values = number in range (0, 127)))
                              gear_values=[   80,    160,     240,  # tempo values = bpm
                                          (0, 59), (0, 57), (0, 60),  # instrument values = program in form (a,b)
                                               -8,      0,       8,  # pitch values = number of semitones up
                                               70,     95,    120 ], # volume values = number in range (0, 127)
                              name='Level 3',
                ))

sm.add_screen(LevelEasyMediumScreen(level=4,
                              notes=notes['Level 4'],
                              goal_values=[    76,  # tempo value = bpm
                                          (0, 40),  # instrument values = program in form (a,b)
                                                1,  # pitch values = number of semitones up
                                               95 ], # volume values = number in range (0, 127)))
                              gear_values=[   66,    76,     86,  # tempo values = bpm
                                         (0, 24), (0, 46), (0, 40),  # instrument values = program in form (a,b)
                                              -1,      0,       1,  # pitch values = number of semitones up
                                              70,     95,    120 ], # volume values = number in range (0, 127)
                             name='Level 4',
                ))

sm.add_screen(LevelEasyMediumScreen(level=5,
                              notes=notes['Level 5'],
                              goal_values=[    115,  # tempo value = bpm
                                          (0, 21),  # instrument values = program in form (a,b)
                                                -1,  # pitch values = number of semitones up
                                               90 ], # volume values = number in range (0, 127)))
                              gear_values=[   70,    85,     100,  115, 130, # tempo values = bpm
                                         (0, 21), (0, 11), (0, 56), (0, 65), (0, 71), # instrument values = program in form (a,b)
                                              -2,     -1,       0,      +1,      +2, # pitch values = number of semitones up
                                              30,     50,      70,      90,      110], # volume values = number in range (0, 127)
                             name='Level 5',
                ))

sm.add_screen(LevelEasyMediumScreen(level=6,
                              notes=notes['Level 6'],
                              goal_values=[    130,  # tempo value = bpm
                                          (0, 11),  # instrument values = program in form (a,b)
                                                +3,  # pitch values = number of semitones up
                                               60 ], # volume values = number in range (0, 127)))
                              gear_values=[   70,    85,     100,  115, 130, # tempo values = bpm
                                         (0, 0), (0, 8), (0, 46), (0, 13), (0, 11), # instrument values = program in form (a,b)
                                              -5,     -3,       0,      +3,      +5, # pitch values = number of semitones up
                                              40,     60,      80,      100,      120], # volume values = number in range (0, 127)
                             name='Level 6',
                ))

sm.add_screen(LevelEasyMediumScreen(level=7,
                              notes=notes['Level 7'],
                              goal_values=[    100,  # tempo value = bpm
                                          (0, 60),  # instrument values = program in form (a,b)
                                                +8,  # pitch values = number of semitones up
                                               120 ], # volume values = number in range (0, 127)))
                              gear_values=[   80,    90,     100,  110, 120, # tempo values = bpm
                                         (0, 56), (0, 60), (0, 75), (0, 65), (0, 57), # instrument values = program in form (a,b)
                                              -8,     -4,       0,      +4,      +8, # pitch values = number of semitones up
                                              40,     60,      80,      100,      120], # volume values = number in range (0, 127)
                             name='Level 7',
                ))

sm.add_screen(LevelEasyMediumScreen(level=8,
                              notes=notes['Level 8'],
                              goal_values=[    85,  # tempo value = bpm
                                           (0, 71),  # instrument values = program in form (a,b)
                                                -4,  # pitch values = number of semitones up
                                               80 ], # volume values = number in range (0, 127)))
                              gear_values=[   70,    85,     100,  115, 130, # tempo values = bpm
                                         (0, 71), (0, 65), (0, 59), (0, 40), (0, 21), # instrument values = program in form (a,b)
                                              -8,     -4,       0,      +4,      +8, # pitch values = number of semitones up
                                              40,     60,      80,      100,      120], # volume values = number in range (0, 127)
                             name='Level 8',
                ))

sm.add_screen(LevelEasyMediumScreen(level=9,
                              notes=notes['Level 9'],
                              goal_values=[    150,  # tempo value = bpm
                                           (0, 75),  # instrument values = program in form (a,b)
                                                0,  # pitch values = number of semitones up
                                               100 ], # volume values = number in range (0, 127)))
                              gear_values=[   90, 110,    130,     150,  170, # tempo values = bpm
                                         (0, 75), (0, 8), (0, 11), (0, 13), (0, 71), # instrument values = program in form (a,b)
                                              -8,     -4,       0,      +4,      +8, # pitch values = number of semitones up
                                              40,     60,      80,      100,      120], # volume values = number in range (0, 127)
                             name='Level 9',
                ))

sm.add_screen(LevelHardScreen(level=10,
                              notes=notes['Level 10'],
                              goal_values=[[ 80, (0, 24),  0,  120 ], # goal values for melody must be in first three gear values for each type
                                           [ 80, (0, 32),  0,  100 ]],
                              gear_values=[   80, 100, 120,     80, 130, 150, # tempo values = bpm
                                         (0, 40), (0, 24), (0, 46), (0, 105), (0, 21), (0, 32), # instrument values = program in form (a,b)
                                              -4,     0,    +2,      -2,   0, +4, # pitch values = number of semitones up
                                             80,      100,      120, 60 , 80,     100], # volume values = number in range (0, 127)
                             name='Level 10',
                ))

sm.add_screen(LevelHardScreen(level=11,
                              notes=notes['Level 11'],
                              goal_values=[[ 100, (0, 11),  -1,  120 ], # goal values for melody must be in first three gear values for each type
                                           [ 50, (0, 60),  +3,  80 ]],
                              gear_values=[   50, 100, 150, 50, 100, 150, # tempo values = bpm
                                         (0, 0), (0, 8), (0, 11), (0, 60), (0, 59), (0, 57), # instrument values = program in form (a,b)
                                              -1,     0,    +1,   -3,   0, +3, # pitch values = number of semitones up
                                              80,  100,  120,  60,  80, 100], # volume values = number in range (0, 127)
                             name='Level 11',
                ))

sm.add_screen(LevelHardScreen(level=12,
                              notes=notes['Level 12'],
                              goal_values=[[ 120, (0, 0),  0,  60 ], # goal values for melody must be in first three gear values for each type
                                           [ 90, (0, 40),  -1,  80 ]],
                              gear_values=[   90, 105, 120,     90, 105, 120, # tempo values = bpm
                                         (0, 0), (0, 8), (0, 11), (0, 24), (0, 40), (0, 105), # instrument values = program in form (a,b)
                                              -2,     0,    +1,      -1,   0, +2, # pitch values = number of semitones up
                                              60 , 80,     100,      60 , 80,     100,], # volume values = number in range (0, 127)
                             name='Level 12',
                ))

sm.add_screen(LevelHardScreen(level=13,
                              notes=notes['Level 13'],
                              goal_values=[[ 100, (0, 46),  0,  100 ], # goal values for melody must be in first three gear values for each type
                                           [ 100, (0, 75),  0,  60 ]],
                              gear_values=[   80, 100, 120,     100, 130, 150, # tempo values = bpm
                                         (0, 105), (0, 24), (0, 46), (0, 32), (0, 75), (0, 71), # instrument values = program in form (a,b)
                                              -4,     0,    +2,      -2,   0, +4, # pitch values = number of semitones up
                                              60 , 80,     100,      60 , 80,     100], # volume values = number in range (0, 127)
                             name='Level 13',
                ))
run(sm)
