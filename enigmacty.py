from enum import IntEnum
from typing import Iterable
from crypto import acode, OFFSET_UPPER


def letter(a):
	return chr(OFFSET_UPPER + a)


class Direction(IntEnum):
	FORWARD = 0
	BACKWARD = 1


class Rotor:

	def __init__(self, offsets: list[int], name):
		self.name = name
		self.pos = 0
		rev_offsets = [0] * 26
		for i, d in enumerate(offsets):
			rev_offsets[(i + d) % 26] = -d
		self.wiring = list(zip(offsets, rev_offsets))

	@classmethod
	def from_str(cls, alpha, name=None):
		if name is None:
			name = alpha
		return cls([(acode(a) - i) % 26 for i, a in enumerate(alpha)], name)

	def forward(self, a):
		return self._apply(a, Direction.FORWARD)

	def backward(self, a):
		return self._apply(a, Direction.BACKWARD)

	def _apply(self, a, direction: Direction):
		return (a + self.wiring[(a - self.pos) % 26][direction]) % 26

	def rotate(self):
		self.pos = (self.pos + 1) % 26
		return self.pos == 0

	def set_position(self, pos):
		self.pos = pos % 26

	def __repr__(self):
		return self.name


def _check_alpha(table):
	unique = set(table)
	if len(unique) != 26:
		missing = ''.join(letter(a) for a in sorted(set(range(26)) - unique))
		raise ValueError(f"Rotor was missing letters: {missing}")
	if len(table) != 26:
		raise ValueError(f"Rotor had invalid length {len(alpha)}")


def create_plugboard(plugs: Iterable[Iterable[str]]):
	table = list(range(26))
	for a, b in plugs:
		a = acode(a)
		b = acode(b)
		if a == b:
			raise ValueError(f"Plugboard cannot map {letter(a)} to itself")
		table[a] = b
		table[b] = a
	return table


def create_reflector(alpha):
	table = [acode(c) for c in alpha]
	_check_alpha(table)
	for i, a in enumerate(table):
		if table[a] != i:
			raise ValueError(f"{letter(i)} and {letter(a)} are not inverses")
		if i == a:
			raise ValueError(f"Reflector cannot map {letter(a)} to itself")
	return table


def create_rotor(alpha, name=None):
	table = [acode(c) for c in alpha]
	_check_alpha(table)
	return


class Enigma:
	def __init__(self, rotors: list[Rotor], reflector):
		self.plugboard = create_plugboard([])
		self._rotors = rotors
		self.rotor_order = list(rotors)
		self.reflector = reflector

	def process_text(self, text):
		return ''.join(letter(a) for a in self.process(acode(c) for c in text))

	def process(self, seq):
		for a in seq:
			yield self.apply(a)
			self.advance()

	def apply(self, a):
		a = self.plugboard[a]
		for rotor in self.rotor_order:
			a = rotor.forward(a)
		a = self.reflector[a]
		for rotor in reversed(self.rotor_order):
			a = rotor.backward(a)
		a = self.plugboard[a]
		return a

	def advance(self, amount=1):
		for _ in range(amount):
			for rotor in self.rotor_order:
				complete_revolution = rotor.rotate()
				if not complete_revolution:
					break

	def set_rotor_order(self, order):
		self.rotor_order = [self._rotors[i] for i in order]

	def set_positions(self, positions):
		for rotor, pos in zip(self.rotor_order, positions):
			rotor.set_position(pos)

	def set_trigraph(self, tri):
		self.set_positions([acode(a) for a in tri])

	@property
	def trigraph(self):
		return ''.join(letter(r.pos) for r in self.rotor_order)

	@property
	def positions(self):
		return tuple(r.pos for r in self.rotor_order)


r1 = Rotor.from_str('Enigma I-1', 'EKMFLGDQVZNTOWYHXUSPAIBRCJ')
r2 = Rotor.from_str('Enigma I-2', 'AJDKSIRUXBLHWTMCQGZNPYFVOE')
r3 = Rotor.from_str('Enigma I-3', 'BDFHJLCPRTXVZNYEIWGAKMUSQO')
ref = create_reflector('YRUHQSLDPXNGOKMIEBFZCWVJAT')

enigma = Enigma([r1, r2, r3], ref)
