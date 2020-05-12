
from common.noteseq import NoteSequencer
from common.multinoteseq import MultiNoteSequencer
from kivy.graphics.instructions import InstructionGroup
from common.clock import SimpleTempoMap, AudioScheduler

class MusicPlayer(InstructionGroup):
	def __init__(self, notes, sched, synth, channel, tempo_map):
		super(MusicPlayer, self).__init__()

		self.notes = notes

		self.tempo_map = tempo_map
		self.sched = sched
		self.synth = synth
		self.channel = channel

		self.tempo = 0
		self.instrument = (0,0) # grand piano
		self.pitch = -60
		self.volume = 0
		self.synth.cc(self.channel, 7, self.volume)

		self.duration = 0

	def generate(self):
		"""
		generates an unlooped NoteSequencer based on self.notes,
			self.tempo, self.volume, self.instrument, and self.pitch
		"""
		# return NoteSequencer(sched=self.sched, synth=self.synth, channel=self.channel, program=self.instrument, notes=self.get_transposed_pitches(), loop=False)
		return MultiNoteSequencer(sched=self.sched, synth=self.synth, channel=self.channel, program=self.instrument, notes=self.get_transposed_pitches(), loop=False)

	def update_tempo(self, new_tempo):
		"""
		if there's no arg, resets the tempo to None
		"""
		self.tempo = new_tempo
		self.tempo_map.set_tempo(new_tempo, self.sched.get_time())
		self.duration = sum([note[0] for note in self.notes]) / self.tempo / 8


	def update_volume(self, new_volume = 100):
		"""
		if there's no arg, resets the volume to None
		"""
		if new_volume and 0 <= new_volume <= 127:
			self.volume = new_volume
			self.synth.cc(self.channel, 7, new_volume)

	def update_instrument(self, new_program):
		"""
		if there's no arg, resets the instrument to None
		"""
		self.instrument = new_program

	def update_pitch(self, semitones):
		"""
		if there's no arg, resets the pitch to None
		"""
		self.pitch = semitones

	def get_transposed_pitches(self):
		# return [(note[0], note[1] + self.pitch) for note in self.notes]
		return [(note[0], [n + self.pitch for n in note[1]]) for note in self.notes]

	def is_equal(self, other):
		return other.pitch == self.pitch \
		and other.tempo == self.tempo \
		and other.instrument == self.instrument \
		and other.volume == self.volume
