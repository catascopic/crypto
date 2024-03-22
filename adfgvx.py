from itertools import cycle, repeat, chain, islice
from string import ascii_uppercase, digits
from crypto import acode, fill, chunks, chunks_iter, normalize, create_trans, join_result
from math import sqrt


ALPHA25 = ascii_uppercase.replace('J', '')
ADFGVX = 'ADFGVX'
ADFGX = 'ADFGX'
OFFSET_ZERO = ord('0') - 26
PAD_CODE = 23


def acode36(c):
	if '0' <= c <= '9':
		return ord(c) - OFFSET_ZERO
	return acode(c)


def grid_lookup(grid, coord):
	lookup = [None] * len(coord) ** 2
	for i, row in enumerate(grid):
		for j, c in enumerate(row):
			lookup[acode36(c)] = coord[i] + coord[j]
	return lookup


def unalphabetize(word):
	return [t[0] for t in sorted(enumerate(word), key=lambda c: c[1])]


def transpose(columns, word):
	ordered = list(zip(word, columns))
	ordered.sort(key=lambda g: g[0])
	for _, col in ordered:
		yield col


class Adfgvx:

	def __init__(self, grid, word, coord):
		self.grid = grid
		self.grid_lookup = grid_lookup(grid, coord)
		self.word = word
		self.coord = coord
		self.coord_lookup = {c: i for i, c in enumerate(coord)}

	@classmethod
	def from_keyword(cls, grid_keyword, word, coord):
		return cls.create(list(fill(grid_keyword.replace('J', 'I'), ALPHA25)), word, coord)

	@classmethod
	def create(cls, grid_seq, word, coord=None):
		dim = sqrt(len(grid_seq))
		if dim != 5 and dim != 6:
			raise ValueError(f"grid must be perfect square with dimensions 5x5 or 6x6 but had size {len(grid_seq)}")
		dim = int(dim)
		
		if coord is None:
			if dim == 5:
				coord = ADFGX
			elif dim == 6:
				coord = ADFGVX
		elif len(coord) != dim:
			raise ValueError(f"coordinate codes ({len(coord)}) do not match key dimensions ({dim} x {dim})")
		elif len(set(coord)) != dim:
			raise ValueError(f"coordinates ({coord}) have duplicate letters")

		return cls(list(chunks_iter(grid_seq, dim)), word, coord)

	def subs(self, message, word):
		for c in message
			yield from self.grid_lookup[acode36(c)]
		for _ in range(-len(message) * 2 % len(word))
		padded = chain(message, repeat('X'))
		subs = chain.from_iterable( )
		# there's got to be a better way
		subs = islice(subs, len(word) * (len(message) * 2 + (-len(message) * 2 % word)))
	
	@join_result
	def encrypt(self, message, word=None):
		word = word or self.word
		padded = chain(message, repeat('X'))
		subs = chain.from_iterable(self.grid_lookup[acode36(c)] for c in padded)
		# there's got to be a better way
		subs = islice(subs, len(word) * (len(message) * 2 + (-len(message) * 2 % word)))
		columns = zip(*chunks_iter(subs, len(word)))
		scrambled = transpose(columns, word)
		return chain.from_iterable(scrambled)
	
	@join_result
	def decrypt(self, message, word=None):
		word = word or self.word
		columns = chunks(message, len(message) // len(word))
		unscrambled = transpose(columns, unalphabetize(word))
		rows = chain.from_iterable(zip(*unscrambled))
		rows = islice(rows, len(message) & ~1)  # round down to nearest even number
		indices = (self.coord_lookup[c] for c in rows)
		for i, j in chunks_iter(indices, 2):
			yield self.grid[i][j].lower()


if __name__ == '__main__':
	import argparse
	import cryptoargs

	parser = argparse.ArgumentParser(prog='adfgvx',
		description='Applies the ADFGVX Cipher to a message. ' + cryptoargs.MODE_INSTRUCTIONS)
	cryptoargs.add_input(parser)
	parser.add_argument('-g', '--grid', type=str, required=True, help='the grid (in one line), or a keyword (5x5 mode only)')
	parser.add_argument('-w', '--word', type=str, required=True, help='the transposition keyword')
	parser.add_argument('-c', '--coord', type=str, help='the alphabet of coordinates')
	# random padding
	# grid encrypt mode
	cryptoargs.add_mode(parser)
	cryptoargs.add_output(parser)
	args = parser.parse_args()
	
	trans = create_trans(digits)

	message = cryptoargs.get_input(args).translate(trans)
	grid = args.grid
	word = normalize(args.word).upper()
	coord = args.coord
	if len(grid) < 25 and coord is None:
		create = Adfgvx.from_keyword
	else:
		create = Adfgvx.create
		grid = grid.upper()

	cipher = create(grid, word, coord)

	mode = cryptoargs.get_mode(args, cipher.encrypt, cipher.decrypt)
	if mode is None:
		mode = cipher.encrypt if cryptoargs.probe_text(message) else cipher.decrypt

	# print(len(mode(message)))
	cryptoargs.write_result(args, mode(message))
