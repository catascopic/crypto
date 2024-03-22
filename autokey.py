from collections import deque

@join_result
def autokey(message, key, sign, offset):
	key = deque(acode(k) for k in key)
	for m in message:
		a = acode(m)
		k = key.popleft()
		
		yield chr((a + sign * k) % 26 + offset)
		key.append((a + sign * k) % 26)
