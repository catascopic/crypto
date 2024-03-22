from string import ascii_uppercase
from crypto import fill, grid_lookup, acode, chunks_iter, normalize


ALPHA = ascii_uppercase.replace('J', '')


class Playfair:

	def __init__(self, grid):
		self.grid = grid
		self.lookup = grid_lookup(grid, 26)

	@classmethod
	def from_keyword(cls, keyword):
		keyword = keyword.upper().replace('I', 'J')
		return cls(list(chunks_iter(fill(keyword, ALPHA), 5)))

	def encrypt_pair(self, c1, c2, shift=1):
		row1, col1 = self.lookup[acode(c1)]
		row2, col2 = self.lookup[acode(c2)]
		if row1 == row2:
			return (self.grid[row1][(col1 + shift) % 5], 
			        self.grid[row1][(col2 + shift) % 5])
		if col1 == col2:
			return (self.grid[(row1 + shift) % 5][col1], 
			        self.grid[(row2 + shift) % 5][col1])
		return self.grid[row1][col2], self.grid[row2][col1]
	
	def encrypt(self, message, shift=1):
		result = []
		i = 0
		while i < len(message):
			c1 = message[i]
			i += 1
			c2 = message[i] if i < len(message) else 'X'

			if c1 == c2:
				c2 = 'X' if c1 != 'X' else 'Q'	
			else:
				i += 1

			result.extend(self.encrypt_pair(c1, c2, shift))

		return ''.join(result)

	def decrypt(self, message):
		return self.encrypt(message, -1).lower()


if __name__ == '__main__':
	import argparse
	import cryptoargs

	parser = argparse.ArgumentParser(prog='playfair',
		description='Applies the Playfair Cipher to a message. ' + cryptoargs.MODE_INSTRUCTIONS)
	cryptoargs.add_input(parser)
	parser.add_argument('-k', '--key', type=str, required=True, help='the key (in one line), or a keyword')
	# TODO: keyfile
	cryptoargs.add_mode(parser)
	cryptoargs.add_output(parser)
	args = parser.parse_args()

	message = normalize(cryptoargs.get_input(args))
	pf = Playfair.from_keyword(normalize(args.key))
	mode = cryptoargs.get_mode(args, pf.encrypt, pf.decrypt)
	if mode is None:
		mode = pf.encrypt if message[0].islower() else pf.decrypt

	cryptoargs.write_result(args, mode(message))
