from collections import Counter
from difflib import SequenceMatcher
from .model import Alignment
from .normalize import nfkc


def key(text):
    return "".join(nfkc(text).split())


def align(source, target):
    """Unique exact matches support reordering; monotone DP permits 1:2 and 2:1.

    Similarity is a heuristic alignment signal, never semantic proof.
    """
    if len(source) > 500 or len(target) > 500:
        raise ValueError("Alignment supports at most 500 sentence chunks per document")
    sk, tk = [key(s.text) for s in source], [key(t.text) for t in target]
    sc, tc = Counter(sk), Counter(tk)
    matches, used_s, used_t = [], set(), set()
    target_index = {value: j for j, value in enumerate(tk)}
    for i, value in enumerate(sk):
        if value and sc[value] == tc[value] == 1:
            j = target_index[value]
            matches.append(Alignment((source[i].id,), (target[j].id,), 1.0))
            used_s.add(i)
            used_t.add(j)
    sr = [s for i, s in enumerate(source) if i not in used_s]
    tr = [t for j, t in enumerate(target) if j not in used_t]
    n, m = len(sr), len(tr)
    dp = [[float("inf")] * (m + 1) for _ in range(n + 1)]
    back = {}
    dp[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            for a, b in ((1, 1), (1, 2), (2, 1), (1, 0), (0, 1)):
                if i + a > n or j + b > m:
                    continue
                if a and b:
                    left = key("".join(s.text for s in sr[i:i+a]))
                    right = key("".join(t.text for t in tr[j:j+b]))
                    score = SequenceMatcher(None, left, right, autojunk=False).ratio()
                    cost = (1 - score) + 0.12 * (a + b - 2)
                else:
                    score, cost = 0.0, 0.62
                value = dp[i][j] + cost
                if value < dp[i+a][j+b]:
                    dp[i+a][j+b] = value
                    back[i+a, j+b] = i, j, a, b, score
    i, j = n, m
    while i or j:
        pi, pj, a, b, score = back[i, j]
        matches.append(Alignment(tuple(s.id for s in sr[pi:pi+a]), tuple(t.id for t in tr[pj:pj+b]), round(score, 4)))
        i, j = pi, pj
    return tuple(sorted(matches, key=lambda x: (min(x.source_ids, default=10**9), min(x.target_ids, default=10**9))))
