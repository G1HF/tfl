import random

ALPHABET = ['a', 'b']

class Rule:
    def __init__(self, left, right):
        self.left = left
        self.right = right

T = [
    Rule("aabbbaa", "abbaba"),
    Rule("abab", "aaa"),
    Rule("baaab", "abba"),
    Rule("bbbb", "ba"),
]

KB = [
    Rule("bba", "bab"),
    Rule("aaaa", "aaa"),
    Rule("aaab", "aaa"),
    Rule("abaa", "aaa"),
    Rule("abab", "aaa"),
    Rule("baaa", "aaa"),
    Rule("baba", "baab"),
    Rule("bbbb", "ba"),
    Rule("baaba", "aaa"),
    Rule("baabb", "aaa"),
    Rule("babbb", "baa"),
]

MAX_WORD_LEN = 10
MAX_STEPS = 20

class Node:
    def __init__(self, word, parent=None, path=None):
        self.word = word
        self.parent = parent
        self.path = [] if path is None else path

class FIFO:
    def __init__(self):
        self.data = []
        self.capacity = 0
        self.count = 0
        self.head = 0
        self.tail = 0

    def put(self, x):
        self.data.append(x)
        self.tail += 1
        self.count += 1
        self.capacity += 1

    def get(self):
        x = self.data[self.head]
        self.head += 1
        self.count -= 1
        return x

def make_queue():
    return FIFO()

def find_occurrences(s, sub):
    idxs = []
    n = len(sub)
    for i in range(len(s) - n + 1):
        if s[i:i+n] == sub:
            idxs.append(i)
    return idxs

def replace_once_from(s, left, right, index):
    return s[:index] + right + s[index+len(left):]

def make_random_word():
    length = random.randint(0, MAX_WORD_LEN - 1)
    out = []
    for _ in range(length):
        out.append(random.choice(ALPHABET))
    return "".join(out)

def build_chain(start_word, rules):
    chain = []
    steps = random.randint(0, MAX_STEPS - 1)
    current = start_word
    chain.append(current)

    for _ in range(steps):
        order = random.sample(range(len(rules)), len(rules))
        applied = False

        for k in order:
            rule = rules[k]
            positions = find_occurrences(current, rule.left)
            if positions:
                pos = random.choice(positions)
                current = replace_once_from(current, rule.left, rule.right, pos)
                chain.append(current)
                applied = True
                break
        if not applied:
            break

    return chain, current

def enumerate_variants(word, rules):
    results = []
    for rule in rules:
        places = find_occurrences(word, rule.left)
        if places:
            for j in places:
                results.append(replace_once_from(word, rule.left, rule.right, j))
    return results

def bfs_build_tree(start_word, finish_word, rules):
    q = make_queue()
    root = Node(start_word, None, None)

    visited = {start_word: True}

    q.put(root)
    while q.count > 0:
        cur = q.get()
        if cur.word == finish_word:
            return cur.path, cur.word

        new_words = enumerate_variants(cur.word, rules)
        print(cur.word, end="")
        print(new_words)
        print()

        for nw in new_words:
            if visited.get(nw) or len(nw) < len(finish_word):
                continue

            new_path = [] if cur.path is None else list(cur.path)
            new_path.append(cur.word)
            w = Node(nw, cur, new_path)
            visited[nw] = True
            q.put(w)

    return None, ""

def connect_words(w0, w1, rules):
    if w0 == w1:
        print(f"{w0} и {w1} одинаковы")
    elif len(w0) > len(w1):
        chain, _ = bfs_build_tree(w0, w1, rules)
        print(f"Переход из {w0} в {w1}. Путь {chain}")
    elif len(w0) < len(w1):
        chain, _ = bfs_build_tree(w1, w0, rules)
        print(f"Переход из {w1} в {w0}. Путь {chain}")

def fuzz_equivalence(w0, w1, rules):
    if w0 == w1:
        chain0, nf0 = build_chain(w0, rules)
        print(f"{w0} и {w1} одинаковы")
        print(f"Нормальная форма {nf0}")
        print(f"Путь {chain0}")
        return

    _, nf_a = build_chain(w0, rules)
    _, nf_b = build_chain(w1, rules)

def main():
    s = make_random_word()
    print(s)
    chain, w = build_chain(s, T)
    print(chain)
    print(w)
    connect_words(w, s, KB)

if __name__ == "__main__":
    main()
