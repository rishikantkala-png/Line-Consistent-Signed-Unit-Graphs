# Signed Unit Graphs of Z_n

Implementation of balance and line-consistency checking for six signed
unit graphs defined on the ring Z_n.

## Background

Let R = Z_n. The **unit graph** of R has vertex set R, with distinct
vertices a, b adjacent iff a + b is a unit of R. This repository fixes
that underlying graph and studies three signing schemes and their
negations:

| Graph          | Edge is positive iff                                  |
|----------------|--------------------------------------------------------|
| G_S1(R)        | at least one endpoint is a unit                        |
| G_S2(R)        | both endpoints are units                                |
| G_S3(R)        | both endpoints are the same type (unit/unit or non/non) |
| eta(G_Si(R))   | negation (flip all signs) of the corresponding G_Si(R)  |

For each of the six signed graphs, the script checks:

- **Balance** (Harary): whether every cycle has an even number of
  negative edges, tested via BFS two-colouring.
- **Line consistency**: the line graph L(G) is built (vertices = edges
  of G, marked with that edge's sign; adjacency = shared endpoint in
  G), and consistency is tested via a fundamental cycle basis
  (Beineke & Harary): every cycle in L(G) must contain an even number
  of negatively marked vertices.

## Requirements

None beyond the Python standard library (Python 3.7+).

## Usage

```bash
python3 signed_unit_graph.py
```

This runs the analysis for a handful of example values of n and prints
a comparison table. To use it programmatically:

```python
from signed_unit_graph import analyze, print_table

print_table(12)          # pretty-print all six graphs for n = 12
results = analyze(12)    # list of dicts, one per scheme, for further processing
```

Each entry of `results` contains:

```
{
    "scheme": "Sigma2",
    "n": 12,
    "num_vertices": 12,
    "num_edges": 24,
    "positive_edges": 0,
    "negative_edges": 24,
    "balanced": True,
    "line_consistent": False,
}
```

## Citation

Line Consistent Signed Unit Graphs
## License

NA