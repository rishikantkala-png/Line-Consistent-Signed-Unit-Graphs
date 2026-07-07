"""
signed_unit_graph.py

Constructs the unit graph of Z_n and evaluates six signing schemes on it:

    G_S1(R)        : positive iff at least one endpoint is a unit
    G_S2(R)        : positive iff both endpoints are units
    G_S3(R)        : positive iff both endpoints are the same type
                     (both units, or both non-units)
    eta(G_S1(R))   : negation of G_S1(R)
    eta(G_S2(R))   : negation of G_S2(R)
    eta(G_S3(R))   : negation of G_S3(R)

For each of the six signed graphs it reports:
    - balance (Harary): every cycle has an even number of negative edges
    - line consistency: build the line graph L(G), mark each L(G)-vertex
      with the sign of the corresponding G-edge, and test whether every
      cycle in L(G) has an even number of negatively marked vertices

No third-party dependencies -- only the Python standard library.

Author: (add your name)
"""

from math import gcd
from collections import deque
from itertools import product


# ---------------------------------------------------------------------------
# 1. Underlying unit graph of Z_n
# ---------------------------------------------------------------------------

def unit_graph_edges(n):
    """
    Return (units, edges) for the unit graph of Z_n.

    units : sorted list of a in {0,...,n-1} with gcd(a, n) == 1
    edges : list of (a, b) pairs with a < b such that a + b (mod n) is a unit
    """
    is_unit = lambda a: gcd(a, n) == 1
    units = [a for a in range(n) if is_unit(a)]
    edges = []
    for a in range(n):
        for b in range(a + 1, n):
            if is_unit((a + b) % n):
                edges.append((a, b))
    return units, edges


# ---------------------------------------------------------------------------
# 2. The six signing schemes
# ---------------------------------------------------------------------------

def sign_sigma1(a, b, is_unit):
    return 1 if (is_unit(a) or is_unit(b)) else -1


def sign_sigma2(a, b, is_unit):
    return 1 if (is_unit(a) and is_unit(b)) else -1


def sign_sigma3(a, b, is_unit):
    return 1 if (is_unit(a) == is_unit(b)) else -1


SCHEMES = {
    "Sigma1":      (sign_sigma1, False),
    "Sigma2":      (sign_sigma2, False),
    "Sigma3":      (sign_sigma3, False),
    "eta(Sigma1)": (sign_sigma1, True),
    "eta(Sigma2)": (sign_sigma2, True),
    "eta(Sigma3)": (sign_sigma3, True),
}


def signed_edges(edges, is_unit, sign_fn, negate):
    """Attach a sign to every edge according to sign_fn (optionally negated)."""
    out = []
    for a, b in edges:
        s = sign_fn(a, b, is_unit)
        if negate:
            s = -s
        out.append((a, b, s))
    return out


# ---------------------------------------------------------------------------
# 3. Balance test (Harary): BFS two-colouring
# ---------------------------------------------------------------------------

def check_balance(vertices, signed_edge_list):
    """
    Returns (balanced: bool, bipartition: dict or None).

    A signed graph is balanced iff vertices can be split into V+ and V-
    such that every edge inside V+ or inside V- is positive, and every
    edge between V+ and V- is negative. Tested via BFS 2-colouring:
    colour(u) * colour(v) must equal sign(u, v) for every edge.
    """
    adj = {v: [] for v in vertices}
    for a, b, s in signed_edge_list:
        adj[a].append((b, s))
        adj[b].append((a, s))

    colour = {}
    for start in vertices:
        if start in colour:
            continue
        colour[start] = 1
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v, s in adj[u]:
                expected = colour[u] * s
                if v not in colour:
                    colour[v] = expected
                    queue.append(v)
                elif colour[v] != expected:
                    return False, None

    return True, colour


# ---------------------------------------------------------------------------
# 4. Line graph + line consistency test
# ---------------------------------------------------------------------------

def build_line_graph(signed_edge_list):
    """
    Build L(G): one vertex per edge of G, marked with that edge's sign.
    Two L(G)-vertices are adjacent iff the corresponding G-edges share
    an endpoint.

    Returns (num_vertices, marks, adjacency_list)
    """
    m = len(signed_edge_list)
    marks = [s for (_, _, s) in signed_edge_list]
    adj = [[] for _ in range(m)]

    incident = {}
    for i, (a, b, _) in enumerate(signed_edge_list):
        incident.setdefault(a, []).append(i)
        incident.setdefault(b, []).append(i)

    for idx_list in incident.values():
        for i in range(len(idx_list)):
            for j in range(i + 1, len(idx_list)):
                u, v = idx_list[i], idx_list[j]
                adj[u].append(v)
                adj[v].append(u)

    return m, marks, adj


def check_line_consistency(m, marks, adj):
    """
    Consistency test for a marked graph via a fundamental cycle basis:
    build a BFS spanning forest, then for every non-tree edge recover the
    fundamental cycle (walk both endpoints up to their common ancestor)
    and check that it contains an even number of negatively marked
    vertices. The marked graph is consistent iff this holds for every
    fundamental cycle (Beineke & Harary).

    Returns (consistent: bool, violating_cycle_length: int or None)
    """
    parent = [-1] * m
    visited = [False] * m
    consistent = True
    violating_len = None

    for s in range(m):
        if visited[s] or not consistent:
            continue
        visited[s] = True
        queue = deque([s])
        while queue and consistent:
            u = queue.popleft()
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    parent[v] = u
                    queue.append(v)
                elif v != parent[u]:
                    # non-tree edge -> fundamental cycle
                    seen = set()
                    path_from_u = []
                    x = u
                    while x != -1:
                        seen.add(x)
                        path_from_u.append(x)
                        x = parent[x]

                    path_from_v = []
                    cur = v
                    while cur not in seen:
                        path_from_v.append(cur)
                        cur = parent[cur]
                    lca = cur

                    cycle_vertices = path_from_u[: path_from_u.index(lca) + 1] + path_from_v
                    neg_count = sum(1 for idx in cycle_vertices if marks[idx] == -1)
                    if neg_count % 2 != 0:
                        consistent = False
                        violating_len = len(cycle_vertices)
                        break
            if not consistent:
                break

    return consistent, violating_len


# ---------------------------------------------------------------------------
# 5. Driver: evaluate all six schemes for a given n
# ---------------------------------------------------------------------------

def analyze(n):
    """
    Run all six signing schemes on the unit graph of Z_n and return a list
    of result dicts, one per scheme.
    """
    units, edges = unit_graph_edges(n)
    is_unit = lambda a: gcd(a, n) == 1
    vertices = list(range(n))

    results = []
    for name, (sign_fn, negate) in SCHEMES.items():
        s_edges = signed_edges(edges, is_unit, sign_fn, negate)
        balanced, _ = check_balance(vertices, s_edges)
        m, marks, adj = build_line_graph(s_edges)
        consistent, _ = check_line_consistency(m, marks, adj)
        pos = sum(1 for (_, _, s) in s_edges if s == 1)
        neg = len(s_edges) - pos

        results.append({
            "scheme": name,
            "n": n,
            "num_vertices": n,
            "num_edges": len(s_edges),
            "positive_edges": pos,
            "negative_edges": neg,
            "balanced": balanced,
            "line_consistent": consistent,
        })
    return results


def print_table(n):
    results = analyze(n)
    header = f"{'Graph':<14}{'Edges':>7}{'Pos':>6}{'Neg':>6}{'Balanced':>11}{'LineConsistent':>16}"
    print(f"\nn = {n}")
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['scheme']:<14}{r['num_edges']:>7}{r['positive_edges']:>6}"
              f"{r['negative_edges']:>6}{str(r['balanced']):>11}{str(r['line_consistent']):>16}")


if __name__ == "__main__":
    # Example usage: run for a handful of n values.
    for n in (6, 7, 8, 9, 10, 12):
        print_table(n)
