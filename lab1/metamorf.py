"""
Метаморфное тестирование 3 инвариантов для двух систем: T' и KB

Каждый инвариант реализован отдельной функцией, которая
возвращает True/False для одной случайной цепочки переписываний.
"""

from __future__ import annotations
import random
from typing import List, Tuple, Set

T: List[Tuple[str, str]] = [
    ("aabbbaa", "abbaba"),
    ("abab",    "aaa"),
    ("baaab",   "abba"),
    ("bbbb",    "ba"),
]

KB: List[Tuple[str, str]] = [
    ("bba",   "bab"),
    ("aaaa",  "aaa"),
    ("aaab",  "aaa"),
    ("abaa",  "aaa"),
    ("abab",  "aaa"),
    ("baaa",  "aaa"),
    ("baba",  "baab"),
    ("bbbb",  "ba"),
    ("baaba", "aaa"),
    ("baabb", "aaa"),
    ("babbb", "baa"),
]

ALPHABET = ("a", "b")

def _find_all(text: str, pat: str) -> List[int]:
    out, i = [], 0
    while True:
        j = text.find(pat, i)
        if j < 0:
            return out
        out.append(j)
        i = j + 1

def _neighbors_forward(word: str, rules: List[Tuple[str, str]]) -> Set[str]:
    outs: Set[str] = set()
    for lhs, rhs in rules:
        for i in _find_all(word, lhs):
            outs.add(word[:i] + rhs + word[i + len(lhs):])
    outs.discard(word)
    return outs

def _random_word(min_len: int = 1, max_len: int = 20) -> str:
    L = random.randint(min_len, max_len)
    return "".join(random.choice(ALPHABET) for _ in range(L))

def _random_chain_forward(w: str, rules: List[Tuple[str, str]], min_steps=1, max_steps=20) -> List[str]:
    steps = random.randint(min_steps, max_steps)
    chain = [w]
    cur = w
    for _ in range(steps):
        candidates = list(_neighbors_forward(cur, rules))
        if not candidates:
            break
        cur = random.choice(candidates)
        chain.append(cur)
    return chain

def _phi(word: str) -> int:
    a = word.count("a")
    b = word.count("b")
    return a + 2*b


"""
1. Если в слове есть хотя бы одна a, то ни в T', ни в минимальной системе нельзя получить слово без a.
"""
def inv_has_a_preserved_random(rules: List[Tuple[str, str]],
                               *,
                               min_len=1, max_len=25,
                               min_steps=1, max_steps=20) -> bool:
    w0 = _random_word(min_len, max_len)
    chain = _random_chain_forward(w0, rules, min_steps, max_steps)

    if "a" not in chain[0]:
        return True

    return all(("a" in w) for w in chain)


"""
2. Из непустого слова нельзя получить пустое.
"""
def inv_nonempty_preserved_random(rules: List[Tuple[str, str]],
                                  *,
                                  min_len=1, max_len=25,
                                  min_steps=1, max_steps=20) -> bool:
    w0 = _random_word(min_len, max_len)
    assert len(w0) > 0
    chain = _random_chain_forward(w0, rules, min_steps, max_steps)
    return all(len(w) > 0 for w in chain)


"""
3) 3. функция phi = a+2b не растёт
"""
def inv_phi_nonincreasing_random(rules: List[Tuple[str, str]],
                                 *,
                                 min_len=1, max_len=25,
                                 min_steps=1, max_steps=20) -> bool:
    w0 = _random_word(min_len, max_len)
    chain = _random_chain_forward(w0, rules, min_steps, max_steps)
    prev_phi = _phi(chain[0])
    for w in chain[1:]:
        cur_phi = _phi(w)
        if cur_phi > prev_phi:
            return False
        prev_phi = cur_phi
    return True

def run_one_sample(system_name: str, rules: List[Tuple[str, str]]) -> None:
    ok1 = inv_has_a_preserved_random(rules)
    ok2 = inv_nonempty_preserved_random(rules)
    ok3 = inv_phi_nonincreasing_random(rules)
    print(f"{system_name}:  has_a={ok1}  nonempty={ok2}  phi={ok3}")

def run_many(trials: int, seed: int) -> None:
    random.seed(seed)
    c = {"T'": T, "KB": KB}
    results = {name: [0, 0, 0] for name in c}

    for _ in range(trials):
        for name, rules in c.items():
            results[name][0] += inv_has_a_preserved_random(rules)
            results[name][1] += inv_nonempty_preserved_random(rules)
            results[name][2] += inv_phi_nonincreasing_random(rules)

    for name in c:
        a,b,p = results[name]
        print(f"{name}  |  has_a: {a}/{trials}  nonempty: {b}/{trials}  phi: {p}/{trials}")

if __name__ == "__main__":
    run_one_sample("T'", T)
    run_one_sample("KB", KB)

    run_many(500, 123)
