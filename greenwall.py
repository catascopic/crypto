import itertools


MULT_INV = [None] + [pow(i, -1, 29) for i in range(1, 29)]
ORD_A = ord('A')
PUNCT = ' ,.'
punct_codes = {c: i for i, c in enumerate(PUNCT, start=26)}

def chunks(list_, n):
	for i in range(0, len(list_), n):
		yield list_[i:i + n]

def to_code(c):
	x = ord(c.upper()) - ORD_A
	return x if 0 <= x <= 25 else punct_codes[c]

def to_code_list(s, start=0):
	return [to_code(c) + start for c in s]

def to_char(x):
	return chr(x + ORD_A) if x < 26 else PUNCT[x - 26]

def apply_enc(x, h, v, b):
	return ((b * x + h) * v) % 29

def apply_dec(x, h, v, b):
	return ((MULT_INV[v] * x - h) * MULT_INV[b]) % 29


def stream(code, horiz, vert, mode):
	for block_num, chunk in enumerate(chunks(code, len(horiz) * len(vert))):
		for i, (v, h) in zip(chunk, itertools.product(vert, horiz)):
			yield mode(i, h, v, block_num % 28 + 1)


def greenwall(message, key_horiz, key_vert, mode):
	horiz = to_code_list(key_horiz)
	vert = to_code_list(key_vert, 1)
	code = to_code_list(message)	
	result = ''.join(to_char(i) for i in stream(code, horiz, vert, mode))
	return result


def encrypt(message, key_horiz, key_vert):
	return greenwall(message, key_horiz, key_vert, apply_enc)

def decrypt(message, key_horiz, key_vert):
	return greenwall(message, key_horiz, key_vert, apply_dec).lower()


if __name__ == '__main__':
	import argparse
	
	def probe_text(s):
		for c in s:
			if c.isalpha():
				return c.islower()
		return True
	
	parser = argparse.ArgumentParser(
		prog='greenwall',
		description='Applies the world-famous Greenwall Cipher to a message.',
		epilog='Algorithm by Max Koren and Oliver Hammond.')
	input_group = parser.add_mutually_exclusive_group(required=True)
	input_group.add_argument('message', nargs='?', type=str, help='the text of the message')
	input_group.add_argument('-i', '--input', type=str, dest='in_file', metavar='FILE', help='a file containing the message')
	parser.add_argument('-z', '--horizontal', type=str, required=True, metavar='HORIZ', help='the horizontal (additive) keyword')
	parser.add_argument('-v', '--vertical', type=str, required=True, metavar='VERT', help='the vertical (multiplicative) keyword')
	mode_group = parser.add_mutually_exclusive_group()
	mode_group.add_argument('-e', '--encrypt', action='store_true', help='encrypt mode')
	mode_group.add_argument('-d', '--decrypt', action='store_true', help='decrypt mode')
	parser.add_argument('-o', '--output', type=str, dest='out_file', metavar='FILE', help='destination for output')
	args = parser.parse_args()
	
	if args.message is not None:
		message = args.message
	else:
		with open(args.in_file) as f:
			message = f.read()
	
	if args.encrypt:
		mode = encrypt
	elif args.decrypt:
		mode = decrypt
	elif probe_text(message):
		mode = encrypt
	else:
		mode = decrypt

	result = mode(message, args.horizontal, args.vertical)

	if args.out_file is not None:
		with open(args.out_file, 'w') as f:
			f.write(result)
	else:
		print(result)
