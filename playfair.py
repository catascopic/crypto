import sys
from itertools import chain
from string import ascii_uppercase


ALPHA = ascii_uppercase[:9] + ascii_uppercase[10:]

def chunks(list_, n):
	for i in range(0, len(list_), n):
		yield list_[i:i + n]

		
def create_lookup(grid):
	lookup = {}
	for i, row in enumerate(grid):
		for j, c in enumerate(row):
			lookup[c] = i, j
	lookup['J'] = lookup['I']
	return lookup


def make_key(keyword):
	letters = chain(keyword.upper().replace('J', 'I'), ALPHA)
	seen = set()
	while len(seen) < 25:
		c = next(letters)
		if c not in seen:
			yield c
			seen.add(c)


class Playfair:

	def __init__(self, grid):
		self.grid = grid
		self.lookup = create_lookup(grid)

	@classmethod
	def from_keyword(cls, keyword):
		return cls(list(chunks(list(make_key(keyword)), 5)))

	def encode_pair(self, c1, c2, shift=1):
		row1, col1 = self.lookup[c1]
		row2, col2 = self.lookup[c2]
		if row1 == row2:
			return (self.grid[row1][(col1 + shift) % 5], 
			        self.grid[row1][(col2 + shift) % 5])
		if col1 == col2:
			return (self.grid[(row1 + shift) % 5][col1], 
			        self.grid[(row2 + shift) % 5][col1])
		return self.grid[row1][col2], self.grid[row2][col1]
	
	def encrypt(self, message, shift=1):
		message = message.upper()
		i = 0
		result = []
		while i < len(message):
			c1 = message[i]
			if i == len(message) - 1:
				c2 = 'X'
			else:
				c2 = message[i + 1]

			if c1 == c2:
				c2 = 'X' if c1 != 'X' else 'Q'	
				i += 1
			else:
				i += 2

			result.extend(self.encode_pair(c1, c2, shift))

		return ''.join(result)

	def decrypt(self, message):
		return self.encrypt(message, -1).lower()


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(prog='playfair',
		description='Applies the Playfair Cipher to a message. A message starting with a lower-case letter is assumed plaintext to be encrypted (with upper-case output), and the inverse is also true. Encrypt/decrypt can be forced with optional flags.')
	input_group = parser.add_mutually_exclusive_group(required=True)
	input_group.add_argument('message', nargs='?', type=str, help='the text of the message')
	input_group.add_argument('-i', '--input', metavar='FILE', dest='in_file', type=str, help='a file containing the message')
	parser.add_argument('-k', '--key', type=str, required=True, help='the cipher key in one line')
	mode_group = parser.add_mutually_exclusive_group()
	mode_group.add_argument('-e', '--encrypt', action='store_true', help='encrypt mode')
	mode_group.add_argument('-d', '--decrypt', action='store_true', help='decrypt mode')
	parser.add_argument('-o', '--output', metavar='FILE', dest='out_file', type=str, help='destination for output; print to STDOUT by default')
	args = parser.parse_args()
	
	if args.message is not None:
		message = args.message
	else:
		with open(args.in_file) as f:
			message = f.read()
	
	cipher = Playfair.from_keyword(args.key)
	
	if args.encrypt:
		mode = cipher.encrypt
	elif args.decrypt:
		mode = cipher.decrypt
	elif message[0].islower():
		mode = cipher.encrypt
	else:
		mode = cipher.decrypt

	result = mode(message)
	
	if args.out_file is not None:
		with open(args.out_file, 'w') as f:
			f.write(result)
	else:
		print(result, end='')
