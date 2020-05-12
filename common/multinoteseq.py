from common.clock import kTicksPerQuarter, quantize_tick_up

class MultiNoteSequencer(object):
    """
    Plays a Sequence of notes. The sequence is a python list containing
    notes. Each note is ``(dur, pitches)``.
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
        super(MultiNoteSequencer, self).__init__()
        self.sched = sched
        self.synth = synth
        self.channel = channel
        self.program = program

        self.notes = notes
        self.loop = loop
        self.on_cmd = None
        self.on_notes = []
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
            dur, pitches = self.notes[idx]
            for pitch in pitches:
                if pitch:
                    self.synth.noteon(self.channel, pitch, 60)
                    self.on_notes.append(pitch)

            # schedule the next note:
            self.on_cmd = self.sched.post_at_tick(self._note_on, tick+dur, idx+1)


    def _note_off(self):
        # terminate current notes:
        if self.on_notes:
            for note in self.on_notes:
                self.synth.noteoff(self.channel, note)
            self.on_notes = []
