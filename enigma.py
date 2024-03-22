import itertools
from enum import IntEnum
from collections import Counter, deque
from typing import Iterable

ORD_A = ord('A')
TOTAL_POSITIONS = 26**3
TOTAL_SETTINGS = TOTAL_POSITIONS * 6


def letter(a):
    return chr(ORD_A + a)


def code(a):
    return ord(a) - ORD_A


class Direction(IntEnum):
    FORWARD = 0
    BACKWARD = 1


class Rotor:

    def __init__(self, name, offsets: list[int]):
        self.name = name
        self.pos = 0
        rev_offsets = [0] * 26
        for i, d in enumerate(offsets):
            rev_offsets[(i + d) % 26] = -d
        self.wiring = list(zip(offsets, rev_offsets))

    @classmethod
    def from_str(cls, name, s):
        return cls(name, [(code(a) - i) % 26 for i, a in enumerate(s)])

    def forward(self, a):
        return self._apply(a, Direction.FORWARD)

    def backward(self, a):
        return self._apply(a, Direction.BACKWARD)

    def _apply(self, a, direction: Direction):
        return (a + self.wiring[(a - self.pos) % 26][direction]) % 26

    def rotate(self):
        self.pos += 1
        self.pos %= 26
        return self.pos == 0

    def set_position(self, pos):
        self.pos = pos % 26

    def __repr__(self):
        return self.name


def create_plugboard(plugs: Iterable[tuple[str, str]]):
    table = list(range(26))
    for a, b in plugs:
        a = code(a)
        b = code(b)
        table[a] = b
        table[b] = a
    return table


def create_reflector(s):
    table = [code(a) for a in s]
    if len(table) != 26:
        raise ValueError(f"Rotor had invalid length {len(table)}")
    for i, a in enumerate(table):
        if table[a] != i:
            raise ValueError(f"{letter(i)} and {letter(a)} are not inverses")
    return table


class Enigma:
    def __init__(self, rotors: list[Rotor], reflector):
        self.plugboard = create_plugboard([])
        self._rotors = rotors
        self.rotor_order = list(rotors)
        self.reflector = reflector

    def process_text(self, text):
        return ''.join(letter(a) for a in self.process(code(c) for c in text))

    def process(self, seq):
        for a in seq:
            yield self.apply(a)
            self.advance()

    def apply(self, a):
        a = self.plugboard[a]
        for rotor in self.rotor_order:
            a = rotor.forward(a)
        a = self.reflector[a]
        for rotor in reversed(self.rotor_order):
            a = rotor.backward(a)
        a = self.plugboard[a]
        return a

    def advance(self, amount=1):
        for _ in range(amount):
            for rotor in self.rotor_order:
                complete_revolution = rotor.rotate()
                if not complete_revolution:
                    break

    def set_rotor_order(self, order):
        self.rotor_order = [self._rotors[i] for i in order]

    def set_positions(self, positions):
        for rotor, pos in zip(self.rotor_order, positions):
            rotor.set_position(pos)

    def set_trigraph(self, tri):
        self.set_positions([code(a) for a in tri])

    @property
    def trigraph(self):
        return ''.join(letter(r.pos) for r in self.rotor_order)

    @property
    def positions(self):
        return tuple(r.pos for r in self.rotor_order)


r1 = Rotor.from_str('Rotor 1', 'EKMFLGDQVZNTOWYHXUSPAIBRCJ')
r2 = Rotor.from_str('Rotor 2', 'AJDKSIRUXBLHWTMCQGZNPYFVOE')
r3 = Rotor.from_str('Rotor 3', 'BDFHJLCPRTXVZNYEIWGAKMUSQO')
ref = create_reflector('YRUHQSLDPXNGOKMIEBFZCWVJAT')

enigma = Enigma([r1, r2, r3], ref)
# print(enigma.encrypt('AAAAA'))


def create_lookup(table):
    lookup = [0] * 26
    for i, a in enumerate(table):
        lookup[a] = i
    return lookup


def letters(seq):
    return ''.join(letter(c) for c in seq)


def get_cycle_structure(enigma: Enigma):
    positions = enigma.positions
    table = [enigma.apply(a) for a in range(26)]
    enigma.advance(3)
    table_plus3 = [enigma.apply(a) for a in range(26)]
    enigma.set_positions(positions)
    seen = set()
    cycles = []
    for a in table:
        if a not in seen:
            start = a
            cycle = [a]
            while True:
                a = table_plus3[table[a]]
                seen.add(a)
                if a == start:
                    break
                cycle.append(a)
            cycles.append(cycle)
    return cycles


def fmt_cycles(structure: set[tuple[int, int]]):
    for length, count in sorted(structure, reverse=True):
        for _ in range(count // 2):
            yield str(length)


def compute_cycles():
    fingerprints = Counter()

    for positions in itertools.permutations(range(3)):
        enigma.set_rotor_order(positions)
        enigma.set_trigraph('AAA')
        print(enigma.rotor_order, enigma.process_text('AAAAA'))
        enigma.set_trigraph('AAA')

        history: deque = deque([None])
        for _ in range(3):
            history.append([enigma.apply(a) for a in range(26)])
            enigma.advance()

        cycle_structures = []
        for _ in range(TOTAL_POSITIONS):
            history.rotate(-1)
            future = [enigma.apply(a) for a in range(26)]
            enigma.advance()
            history[3] = future
            current = history[0]
            lookup = create_lookup(current)

            seen = set()
            cycles = Counter()
            for a in current:
                if a in seen:
                    continue
                start = a
                cycle_length = 1
                while True:
                    seen.add(a)
                    a = future[lookup[a]]
                    if a == start:
                        break
                    cycle_length += 1
                cycles[cycle_length] += 1

            cycle_structures.append(cycles)

        # TODO: fancy way of reducing space

        for i in range(TOTAL_POSITIONS):
            fingerprints[tuple(frozenset(cycle_structures[(i + j) % TOTAL_POSITIONS].items()) for j in range(3))] += 1

    total = 0
    for structures, count in sorted(fingerprints.items(), key=lambda t: t[1]):
        total += count
        print(f"{count:4} instances ({count / TOTAL_SETTINGS:.2%}; {total / TOTAL_SETTINGS:.2%}): "
              f"{'/'.join(','.join(fmt_cycles(s)) for s in structures)}")

    # print(f"{total / TOTAL_SETTINGS:.2%}")


# compute_cycles()


def get_code(rotor: Rotor):
    print(letters(rotor.forward(a) for a in range(26)))


def test():
    for _ in range(50):
        cycles = get_cycle_structure(enigma)
        if len(cycles) >= 6:
            print('*' * 79)
            print(enigma.trigraph)
            for cycle in cycles:
                print(f"({letters(cycle)})")
        enigma.advance()


print(enigma.apply(0))
