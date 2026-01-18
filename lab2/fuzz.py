import random
import re
from collections import defaultdict

ALPH = ("a", "b")

def gen_word(max_len=100):
    n = random.randint(0, max_len)
    return "".join(random.choice(ALPH) for _ in range(n))

class RegexChecker:
    def __init__(self):
        p1 = r"^(?:a|b)*abb(?:a|b)$"
        p2 = r"^(?:a|ba)*bb(?:a*b)*aba(?:a|b)$"
        self.r1 = re.compile(p1)
        self.r2 = re.compile(p2)

    def accept(self, w):
        return self.r1.fullmatch(w) is not None or self.r2.fullmatch(w) is not None

class DFA:
    def __init__(self):
        self.start = "S0"
        self.final = {"S5", "S6", "S11", "S13"}
        self.delta = {
            ("S0","a"):"S1",  ("S0","b"):"S7",
            ("S1","a"):"S1",  ("S1","b"):"S14",
            ("S2","a"):"S2",  ("S2","b"):"S9",
            ("S3","a"):"S2",  ("S3","b"):"S10",
            ("S4","a"):"S6",  ("S4","b"):"S11",
            ("S5","a"):"S2",  ("S5","b"):"S10",
            ("S6","a"):"S2",  ("S6","b"):"S9",
            ("S7","a"):"S1",  ("S7","b"):"S8",
            ("S8","a"):"S3",  ("S8","b"):"S8",
            ("S9","a"):"S3",  ("S9","b"):"S12",
            ("S10","a"):"S4", ("S10","b"):"S12",
            ("S11","a"):"S4", ("S11","b"):"S12",
            ("S12","a"):"S5", ("S12","b"):"S13",
            ("S13","a"):"S3", ("S13","b"):"S8",
            ("S14","a"):"S1", ("S14","b"):"S12",
        }

    def accept(self, w):
        q = self.start
        for ch in w:
            q = self.delta[(q, ch)]
        return q in self.final

class NFA:
    def __init__(self):
        self.start = 0
        self.final = {9}
        self.delta = defaultdict(set)

        def add(u, c, v):
            self.delta[(u, c)].add(v)

        add(0, "a", 0)
        add(0, "b", 0)
        add(0, "a", 1)
        add(0, "b", 2)

        add(1, "b", 4)
        add(2, "b", 3)

        add(3, "a", 5)
        add(3, "a", 6)

        add(4, "b", 7)

        add(5, "a", 5)
        add(5, "b", 3)

        add(6, "b", 8)

        add(8, "a", 7)

        add(7, "a", 9)
        add(7, "b", 9)

    def accept(self, w):
        cur = {self.start}
        for ch in w:
            nxt = set()
            for s in cur:
                nxt |= self.delta.get((s, ch), set())
            cur = nxt
            if not cur:
                return False
        return any(s in self.final for s in cur)

class AFA:
    def __init__(self):
        self.start = 0
        self.final = {4}

        self.or_delta = defaultdict(list)
        self.and_delta = defaultdict(list)

        def add_or(u, c, v):
            self.or_delta[(u, c)].append(v)

        def add_and(u, c, vs):
            self.and_delta[(u, c)].append(tuple(vs))

        add_or(0, "a", 0)
        add_or(0, "b", 0)
        add_or(0, "a", 1)

        add_and(0, "b", (5, 7))

        add_or(1, "b", 2)
        add_or(2, "b", 3)
        add_or(3, "a", 4)
        add_or(3, "b", 4)

        add_or(5, "b", 6)

        add_or(6, "a", 6)
        add_or(6, "b", 6)
        add_or(6, "a", 4)
        add_or(6, "b", 4)

        add_or(7, "a", 7)
        add_or(7, "b", 7)
        add_or(7, "b", 8)

        add_or(8, "a", 9)
        add_or(9, "b", 10)
        add_or(10, "a", 3)

    def _advance_one_state(self, s, ch):
        out = []

        for vs in self.and_delta.get((s, ch), []):
            out.append(("and", vs))

        for v in self.or_delta.get((s, ch), []):
            out.append(("or", (v,)))

        return out

    def accept(self, w):
        configs = {frozenset([self.start])}

        for ch in w:
            new_configs = set()

            for conf in configs:
                partial = {frozenset()}

                ok = True
                for s in conf:
                    moves = self._advance_one_state(s, ch)
                    if not moves:
                        ok = False
                        break

                    next_partial = set()
                    for pc in partial:
                        for kind, vs in moves:
                            if kind == "and":
                                next_partial.add(pc | frozenset(vs))
                            else:
                                next_partial.add(pc | frozenset(vs))
                    partial = next_partial

                if ok:
                    new_configs |= partial

            configs = new_configs
            if not configs:
                return False

        for conf in configs:
            if all(s in self.final for s in conf):
                return True
        return False

def fuzz(trials=100000, max_len=100, seed=1):
    random.seed(seed)

    rx = RegexChecker()
    dfa = DFA()
    nfa = NFA()
    afa = AFA()

    for i in range(1, trials + 1):
        w = gen_word(max_len)
        r = rx.accept(w)
        d = dfa.accept(w)
        n = nfa.accept(w)
        a = afa.accept(w)

        if not (r == d == n == a):
            print("Mismatch on test", i)
            print("w =", repr(w))
            print("regex =", r, "dfa =", d, "nfa =", n, "afa =", a)
            return False

    print("OK:", trials, "tests")
    return True

def test():
    yes = ["abba", "abbb", "aabba", "bbabba", "bbabaa", "bbabab", "aabbbabab"]
    no  = ["", "a", "b", "abb", "abab", "babaa", "bbaaaa", "abbaba"]

    rx = RegexChecker()
    dfa = DFA()
    nfa = NFA()
    afa = AFA()

    for w in yes:
        vals = (rx.accept(w), dfa.accept(w), nfa.accept(w), afa.accept(w))
        print(w, vals)
    for w in no:
        vals = (rx.accept(w), dfa.accept(w), nfa.accept(w), afa.accept(w))
        print(w, vals)

if __name__ == "__main__":
    test()
    fuzz()
