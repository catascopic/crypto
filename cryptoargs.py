import crypto

MODE_INSTRUCTIONS = 'A message starting with a lower-case letter is assumed plaintext to be encrypted (with upper-case output), and the inverse is also true. Encrypt/decrypt can be forced with optional flags.'

MESSAGE = 'message'
IN_FILE = 'in_file'


def add_input(parser):
	input_group = parser.add_mutually_exclusive_group(required=True)
	input_group.add_argument(MESSAGE, nargs='?', type=str, help='the text of the message')
	input_group.add_argument('-i', '--input', type=str, dest=IN_FILE, metavar='FILE', help='a file containing the message')


def add_mode(parser):
	mode_group = parser.add_mutually_exclusive_group()
	mode_group.add_argument('-e', '--encrypt', action='store_true', help='encrypt mode')
	mode_group.add_argument('-d', '--decrypt', action='store_true', help='decrypt mode')


def add_output(parser):
	parser.add_argument('-o', '--output', type=str, dest='out_file', metavar='FILE', help='destination for output; print to STDOUT by default')


def str_or_file(args, text_arg, file_arg):
	text = getattr(args, text_arg)
	if text is not None:
		return text
	with open(getattr(args, file_arg)) as f:
		return f.read()


def get_input(args):
	return str_or_file(args, MESSAGE, IN_FILE)


def write_result(args, result):
	file = args.out_file
	if file is not None:
		with open(file, 'w') as f:
			f.write(result)
	else:
		print(result, end='')


def get_mode(args, encrypt=True, decrypt=False, default=None):
	if args.encrypt:
		return encrypt
	if args.decrypt:
		return decrypt
	return default


def probe_text(text):
	for c in text:
		if c.isalpha():
			return c.islower()
	return True
