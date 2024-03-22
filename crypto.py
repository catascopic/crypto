import itertools
import collections
import string
from abc import ABC


OFFSET_UPPER = ord('A')
OFFSET_LOWER = ord('a')


def acode(c):
	return (ord(c) - OFFSET_UPPER) & 0x1F


def fill(keyword, alphabet):
	letters = itertools.chain(keyword, alphabet)
	seen = set()
	while len(seen) < 25:
		c = next(letters)
		if c not in seen:
			yield c
			seen.add(c)


def grid_lookup(grid, size=26, code=acode):
	lookup = [None] * size
	for i, row in enumerate(grid):
		for j, c in enumerate(row):
			lookup[code(c)] = (i, j)	
	return lookup


def grid_lookup25(grid, alias='I', missing='J'):
	lookup = grid_lookup(grid, 26)
	lookup[acode(missing)] = lookup[acode(alias)]
	return lookup


def create_trans(chars=''):
	trans = [''] * 128
	for c in itertools.chain(string.ascii_letters, chars):
		trans[ord(c)] = c
	return trans


TRANS_DEFAULT = create_trans()


def normalize(text):
	return text.translate(TRANS_DEFAULT)


class Alphabet(ABC):

	def encode(self, c):
		raise NotImplementedError
	
	def decode(self, a):
		raise NotImplementedError


class StandardAlphabet(Alphabet):
	
	def encode(self, c):
		return acode(c)
	
	def decode(self, a):
		return chr(a + OFFSET_UPPER)


ALPHABET = StandardAlphabet()


class CustomAlphabet(Alphabet):
	
	def __init__(self, alphabet):
		self.seq = alphabet
		table = [None] * 128
		for a, c in enumerate(alphabet):
			table[ord(c.upper())] = a
			table[ord(c.lower())] = a
		self._table = table

	def encode(self, c):
		a = self._table[ord(c)]
		if a is None:
			raise ValueError
		return a
	
	def decode(self, a):
		return self.alphabet[a]


def join_result(func):
	def joiner(*args, **kwargs):
		return ''.join(func(*args, **kwargs))
	return joiner


def chunks(seq, size):
	for i in range(0, len(seq), size):
		yield seq[i:i + size]


def chunks_iter(iterator, size):
	# if our iterator is actually an iterable, we end up in an infinite loop.
	# we could check and throw an exception, but it's easier to just call iter().
	# zip_longest(*[iterator]*size)
	iterator = iter(iterator)
	while True:
		chunk = list(itertools.islice(iterator, size))
		if not chunk:
			return
		yield chunk
