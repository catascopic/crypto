import itertools
from string import ascii_uppercase
from crypto import chunks, join_result, create_trans, acode as base_acode, OFFSET_UPPER


MULT_INV = [None] + [pow(i, -1, 29) for i in range(1, 29)]
PUNCT = ' ,.'
ALPHA = ascii_uppercase + PUNCT
punct_codes = {c: i for i, c in enumerate(PUNCT, start=26)}


def acode(c):
	# could be improved with full ascii lookup table
	# as is, we start with a map lookup that misses most of the time
	if a := punct_codes.get(c):
		return a
	return base_acode(c)

def acodes(s, start=0):
	return [acode(c) + start for c in s]

def enc_func(a, h, v, b):
	return ((b * a + h) * v) % 29

def dec_func(a, h, v, b):
	return ((MULT_INV[v] * a - h) * MULT_INV[b]) % 29


@join_result
def greenwall(message, key_horiz, key_vert, func):
	horiz = acodes(key_horiz)
	vert = acodes(key_vert, 1)
	code = acodes(message)
	for block_num, chunk in enumerate(chunks(code, len(horiz) * len(vert))):
		for a, (v, h) in zip(chunk, itertools.product(vert, horiz)):
			# use variable offset rather than explicit .lower()?
			yield ALPHA[func(a, h, v, block_num % 28 + 1)]


def encrypt(message, key_horiz, key_vert):
	return greenwall(message, key_horiz, key_vert, enc_func)

def decrypt(message, key_horiz, key_vert):
	return greenwall(message, key_horiz, key_vert, dec_func).lower()


if __name__ == '__main__':
	import argparse
	import cryptoargs
	
	parser = argparse.ArgumentParser(
		prog='greenwall',
		description='Applies the world-famous Greenwall Cipher to a message. ' + cryptoargs.MODE_INSTRUCTIONS,
		epilog='Algorithm by Max Koren and Oliver Hammond.')
	cryptoargs.add_input(parser)
	parser.add_argument('-z', '--horizontal', type=str, required=True, metavar='HORIZ', help='the horizontal (additive) keyword')
	parser.add_argument('-v', '--vertical',   type=str, required=True, metavar='VERT',  help='the vertical (multiplicative) keyword')
	cryptoargs.add_mode(parser)
	cryptoargs.add_output(parser)
	args = parser.parse_args()

	trans = create_trans(' ,.')
	message = cryptoargs.get_input(args).translate(trans)
	mode = cryptoargs.get_mode(args, encrypt, decrypt)
	if mode is None:
		mode = encrypt if cryptoargs.probe_text(message) else decrypt

	cryptoargs.write_result(args, mode(message, args.horizontal, args.vertical))
