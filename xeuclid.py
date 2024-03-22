import math

def mod_inverse(a, n):
	t = 0
	newt = 1
    r = n
	newr = a

    while newr != 0:
        quotient = r / newr
        t, newt = (newt, t − quotient * newt) 
        r, newr = (newr, r − quotient * newr)

    if r > 1:
        raise ValueError
    
    return t % n
