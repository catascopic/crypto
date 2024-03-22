import itertools
from crypto import acode, join_result, normalize, OFFSET_UPPER, OFFSET_LOWER


@join_result
def vigenere(message, key, sign, offset):
	key = [sign * acode(k) for k in key]
	for m, k in zip(message, itertools.cycle(key)):
		yield chr((acode(m) + k) % 26 + offset)


def encrypt(message, key):
	return vigenere(message, key, +1, OFFSET_UPPER)

def decrypt(message, key):
	return vigenere(message, key, -1, OFFSET_LOWER)


if __name__ == '__main__':
	import argparse
	import cryptoargs
	
	parser = argparse.ArgumentParser(prog='vigenere',
		description='Applies the Vigenère Cipher to a message. ' + cryptoargs.MODE_INSTRUCTIONS)
	cryptoargs.add_input(parser)
	key_group = parser.add_mutually_exclusive_group(required=True)
	key_group.add_argument('-k', '--key', type=str, help='the cipher key')
	key_group.add_argument('-p', '--pad', type=str, metavar='FILE', help='a file containing the cipher key (ideal for one-time pads)')
	cryptoargs.add_mode(parser)
	cryptoargs.add_output(parser)
	args = parser.parse_args()

	message = normalize(cryptoargs.get_input(args))
	key = normalize(cryptoargs.str_or_file(args, 'key', 'pad'))
	mode = cryptoargs.get_mode(args, encrypt, decrypt)
	if mode is None:
		mode = encrypt if message[0].islower() else decrypt

	cryptoargs.write_result(args, mode(message, key))
