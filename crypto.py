import itertools
import string

OFFSET_UPPER = ord('A')
OFFSET_LOWER = ord('a')


def create_trans(chars=''):
	trans = [''] * 256
	for c in itertools.chain(string.ascii_letters, chars):
		trans[ord(c)] = c
	return trans


TRANS_DEFAULT = create_trans()


def normalize(text):
	return text.translate(TRANS_DEFAULT)


def to_code(c):
	return (ord(c) - OFFSET_UPPER) & 0x1F

	
def join_result(func):
	def joiner(*args, **kwargs):
		return ''.join(func(*args, **kwargs))
	return joiner
