import random
import time


# Наивный парсер с возвратами
class NaiveParserStringSlice:
    # Правила грамматики с атрибутами:
    # 1. S → b T a a T        { S.a := T1.a + T2.a + 2 }
    # 2. S → a b              { S.a := 2 }
    # 3. T → a S T            { S.a > T1.a, T0.a := S.a + T1.a + 1 }
    # 4. T → b T              { T0.a := T1.a > 1 ? T1.a + 1 : 0 }
    # 5. T → a                { T.a := 1 }

    def parse(self, inp: str):
        res = self.parseS(inp)
        if res is not None and res["remaining"] == "":
            return {"success": True, "value": res["value"]}
        return {"success": False}

    def parseS(self, s: str):
        if not s:
            return None

        # S → b T a a T
        if s[0] == "b":
            for i in range(1, len(s) - 2):
                t1_str = s[1 : i + 1]
                t1_res = self.parseT(t1_str)
                if t1_res is not None:
                    if len(s) >= i + 3 and s[i + 1 : i + 3] == "aa":
                        t2_str = s[i + 3 :]
                        t2_res = self.parseT(t2_str)
                        if t2_res is not None and t2_res["remaining"] == "":
                            return {
                                "value": t1_res["value"] + t2_res["value"] + 2,
                                "remaining": "",
                            }

        # S → a b
        if len(s) >= 2 and s[:2] == "ab":
            return {"value": 2, "remaining": s[2:]}

        return None

    def parseT(self, s: str):
        if not s:
            return None

        # T → a S T
        if s[0] == "a":
            for i in range(1, len(s) + 1):
                s_str = s[1 : i + 1]
                s_res = self.parseS(s_str)
                if s_res is not None and s_res["remaining"] == "":
                    t1_str = s[i + 1 :]
                    t1_res = self.parseT(t1_str)
                    if t1_res is not None and t1_res["remaining"] == "":
                        if s_res["value"] > t1_res["value"]:
                            return {
                                "value": s_res["value"] + t1_res["value"] + 1,
                                "remaining": "",
                            }

        # T → b T
        if s[0] == "b":
            t1_res = self.parseT(s[1:])
            if t1_res is not None and t1_res["remaining"] == "":
                val = t1_res["value"] + 1 if t1_res["value"] > 1 else 0
                return {"value": val, "remaining": ""}

        # T → a
        if s[0] == "a":
            return {"value": 1, "remaining": s[1:]}

        return None


# Оптимизированный парсер
class TreeNode:
    def __init__(self, typ, value=None, children=None, a=None):
        self.type = typ
        self.value = value
        self.children = children or []
        self.a = a


class OptimizedParser:
    def parse_T(self, s: str):
        if not s:
            return None

        # Правило T -> a, T.a := 1
        if s == "a":
            node = TreeNode("T", "a")
            node.a = 1
            return node

        # Правило T -> aaba, T.a := 4
        if s == "aaba":
            node = TreeNode("T", "aaba")
            node.a = 4
            return node

        # Правило T -> b*ba, T.a := 0
        if len(s) >= 3 and s.endswith("ba") and all(ch == "b" for ch in s[:-2]) and len(s[:-2]) >= 1:
            node = TreeNode("T", s)
            node.a = 0
            return node

        # Правило T -> aabb*ba, T.a := 3
        # (^aabb+ba$)
        if s.startswith("aa") and len(s) >= 6:
            mid = s[2:]
            if mid.startswith("bb") and mid.endswith("ba"):
                bblock = mid[:-2]
                if len(bblock) >= 2 and all(ch == "b" for ch in bblock):
                    node = TreeNode("T", s)
                    node.a = 3
                    return node

        # Правило T -> bT, T1.a > 1, T0.a := T1.a + 1
        if s.startswith("b"):
            inner = s[1:]
            inner_node = self.parse_T(inner)
            if inner_node is not None and inner_node.a is not None and inner_node.a > 1:
                node = TreeNode("T")
                node.children = [inner_node]
                node.a = inner_node.a + 1
                return node

        # Правило T -> abTaaTT,
        # T1.a + T2.a + 2 > T3.a, T0 := T1.a + T2.a + T3.a + 3
        if s.startswith("ab"):
            remaining = s[2:]

            for i in range(0, len(remaining) - 1):
                if remaining[i : i + 2] == "aa":
                    first_part = remaining[:i]
                    after_aa = remaining[i + 2 :]

                    if first_part and after_aa:
                        t1 = self.parse_T(first_part)
                        if not t1:
                            continue

                        for j in range(1, len(after_aa)):
                            second_part = after_aa[:j]
                            third_part = after_aa[j:]

                            if second_part and third_part:
                                t2 = self.parse_T(second_part)
                                t3 = self.parse_T(third_part)

                                if (
                                    t2
                                    and t3
                                    and t1.a is not None
                                    and t2.a is not None
                                    and t3.a is not None
                                ):
                                    if t1.a + t2.a + 2 > t3.a:
                                        node = TreeNode("T")
                                        node.children = [t1, t2, t3]
                                        node.a = t1.a + t2.a + t3.a + 3
                                        return node

        return None

    def parse_S(self, s: str):
        if not s:
            return None

        # Правило S -> ab
        if s == "ab":
            node = TreeNode("S")
            return {"success": True, "node": node}

        # Правило S -> bTaaT
        if s.startswith("b"):
            remaining = s[1:]
            for i in range(0, len(remaining) - 1):
                if remaining[i : i + 2] == "aa":
                    first_part = remaining[:i]
                    second_part = remaining[i + 2 :]

                    if first_part is not None and second_part is not None:
                        t1 = self.parse_T(first_part)
                        t2 = self.parse_T(second_part)

                        if t1 and t2:
                            if 1 + len(first_part) + 2 + len(second_part) == len(s):
                                node = TreeNode("S")
                                node.children = [t1, t2]
                                return {"success": True, "node": node}

        return {"success": False}

    def parse(self, inp: str):
        res = self.parse_S(inp)
        return res if res is not None else {"success": False}


def generate_random_string(length: int) -> str:
    chars = "ab"
    return "".join(random.choice(chars) for _ in range(length))


if __name__ == "__main__":
    parser1 = NaiveParserStringSlice()
    parser2 = OptimizedParser()

    random_string = generate_random_string(50)
    print(f'Случайная строка: "{random_string}"')

    t0 = time.perf_counter()
    result1 = parser1.parse(random_string)
    time1 = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    result2 = parser2.parse(random_string)
    time2 = (time.perf_counter() - t0) * 1000

    print("\nРезультаты парсеров:")
    print(f"Наивный парсер: {'ПРИНЯТО' if result1.get('success') else 'ОТВЕРГНУТО'} ({time1:.2f} мс)")
    print(f"Оптимизированный парсер: {'ПРИНЯТО' if result2.get('success') else 'ОТВЕРГНУТО'} ({time2:.2f} мс)")

    if result1.get("success") == result2.get("success"):
        print("\nРезультаты совпадают!")
    else:
        print("\nРезультаты не совпадают!")
