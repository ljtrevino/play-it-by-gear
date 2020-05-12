#####################################################################
#
# noteseq.py
#
# Copyright (c) 2017, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

from common.clock import kTicksPerQuarter, quantize_tick_up

class NoteSequencer(object):
    """
    Plays a single Sequence of notes. The sequence is a python list containing
    notes. Each note is ``(dur, pitch)``.
    """

    def __init__(self, sched, synth, channel, program, notes, loop=True):
        """
        :param sched: The Scheduler object. Should keep track of ticks and
            allow commands to be scheduled.
        :param synth: The Synthesizer object that will generate audio.
        :param channel: The channel to use for playing audio.
        :param program: A tuple (bank, preset). Allows an instrument to be specified.
        :param notes: The sequence of notes to play, a list containing ``(dur, pitch)``.
        :param loop: When True, restarts playback from the first note.
        """
        super(NoteSequencer, self).__init__()
        self.sched = sched
        self.synth = synth
        self.channel = channel
        self.program = program

        self.notes = notes
        self.loop = loop
        self.on_cmd = None
        self.on_note = 0
        self.playing = False

    def start(self):
        """
        Starts playback.
        """

        if self.playing:
            return

        self.playing = True
        self.synth.program(self.channel, self.program[0], self.program[1])

        # post the first note on the next quarter-note:
        now = self.sched.get_tick()
        tick = quantize_tick_up(now, kTicksPerQuarter)
        self.on_cmd = self.sched.post_at_tick(self._note_on, tick, 0)

    def stop(self):
        """
        Stops playback.
        """

        if not self.playing:
            return

        self.playing = False
        self.sched.cancel(self.on_cmd)
        self.on_cmd = None
        self._note_off()

    def toggle(self):
        """
        Toggles playback.
        """

        if self.playing:
            self.stop()
        else:
            self.start()

    def _note_on(self, tick, idx):
        # terminate current note:
        self._note_off()

        # if looping, go back to beginning
        if self.loop and idx >= len(self.notes):
            idx = 0
        elif not self.loop and idx >= len(self.notes):
            self.playing = False

        # play new note if available
        if idx < len(self.notes):
            dur, pitch = self.notes[idx]
            if pitch: # pitch 0 is a rest
                self.synth.noteon(self.channel, pitch, 60)
                self.on_note = pitch

            # schedule the next note:
            self.on_cmd = self.sched.post_at_tick(self._note_on, tick+dur, idx+1)


    def _note_off(self):
        # terminate current note:
        if self.on_note:
            self.synth.noteoff(self.channel, self.on_note)
            self.on_note = 0


