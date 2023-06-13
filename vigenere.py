from itertools import cycle


# who needs .upper() and .lower() with hacks like this?
OFFSET_UPPER = ord('A')
OFFSET_LOWER = ord('a')

def to_code(ch):
	return (ord(ch) - OFFSET_UPPER) & 0x1F
	
def vigenere(message, key, sign, offset):
	key = [sign * to_code(k) for k in key]
	for m, k in zip(message, cycle(key)):
		yield chr((to_code(m) + k) % 26 + offset)

def encrypt(message, key):
	return vigenere(message, key, 1, OFFSET_UPPER)

def decrypt(message, key):
	return vigenere(message, key, -1, OFFSET_LOWER)


if __name__ == '__main__':
	import argparse
	
	def str_or_file(s, file):
		if s is not None:
			return s
		else:
			with open(file) as f:
				return f.read()

	parser = argparse.ArgumentParser(prog='vigenere',
		description='Applies the Vigenère Cipher to a message. A message starting with a lower-case letter is assumed plaintext to be encrypted (with upper-case output), and the inverse is also true. Encrypt/decrypt can be forced with optional flags.')
	input_group = parser.add_mutually_exclusive_group(required=True)
	input_group.add_argument('message', nargs='?', type=str, help='the text of the message')
	input_group.add_argument('-i', '--input', metavar='FILE', dest='in_file', type=str, help='a file containing the message')
	key_group = parser.add_mutually_exclusive_group(required=True)
	key_group.add_argument('-k', '--key', type=str, help='the cipher key')
	key_group.add_argument('-p', '--keyfile', metavar='FILE', type=str, help='a file containing the cipher key')
	# TODO: make p a flag that forces file read?
	mode_group = parser.add_mutually_exclusive_group()
	mode_group.add_argument('-e', '--encrypt', action='store_true', help='encrypt mode')
	mode_group.add_argument('-d', '--decrypt', action='store_true', help='decrypt mode')
	parser.add_argument('-o', '--dest', metavar='FILE', dest='out_file', type=str, help='destination for output; printed to STDOUT by default')
	args = parser.parse_args()
	
	key = str_or_file(args.key, args.keyfile)
	message = str_or_file(args.message, args.in_file)
		
	if args.encrypt:
		mode = encrypt
	elif args.decrypt:
		mode = decrypt
	elif message[0].islower():
		mode = encrypt
	else:
		mode = decrypt
	
	result = ''.join(mode(message, key))
	if args.out_file is not None:
		with open(args.out_file, 'w') as f:
			f.write(result)
	else:
		print(result)