MESSAGE = 'message'
IN_FILE = 'in_file'

def input_args(parser):
	input_group = parser.add_mutually_exclusive_group(required=True)
	input_group.add_argument(MESSAGE, nargs='?', type=str, help='the text of the message')
	input_group.add_argument('-i', '--input', metavar='FILE', dest=IN_FILE, type=str, help='a file containing the message')


def mode_args(parser):
	mode_group = parser.add_mutually_exclusive_group()
	mode_group.add_argument('-e', '--encrypt', action='store_true', help='encrypt mode')
	mode_group.add_argument('-d', '--decrypt', action='store_true', help='decrypt mode')


def output_args(parser):
	parser.add_argument('-o', '--output', metavar='FILE', dest='out_file', type=str, help='destination for output; print to STDOUT by default')


def str_or_file(args, text_arg, file_arg):
	text = getattr(args, text_arg)
	if text_arg is not None:
		return text_arg
	with open(getattr(args, file_arg)) as f:
		return f.read()


def get_input(args):
	return str_or_file(args, MESSAGE, IN_FILE)


def write_result(result, args):
	file = args.out_file
	if file is not None:
		with open(file, 'w') as f:
			f.write(result)
	else:
		print(result, end='')


def _first_char_lower(message):
	return message[0].islower()


def get_mode(args, encrypt, decrypt, test=_first_char_lower)
	if args.encrypt:
		return encrypt
	if args.decrypt:
		return decrypt
	if test(message):
		return encrypt
	return decrypt

