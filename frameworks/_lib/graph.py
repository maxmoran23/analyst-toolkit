"""
Taint propagation over a transaction graph, for on-chain exposure scoring.

The risk of a blockchain address is largely a function of the graph around it: how
close it sits to illicit funds, through how many hops, and whether a high-throughput
commingling service (a centralized exchange) breaks the trail before the funds
arrive. This module propagates severity-weighted taint forward from labeled illicit
seed nodes, decaying with each hop and with each edge's transfer fraction, and
STOPS at breaker nodes (attribution is lost in an omnibus pool). Pure standard
library.

This is the chain-analytics layer in miniature — in production a vendor computes
exposure like this and a compliance engine dispositions it. `address_exposure`
returns the per-address features a disposition engine consumes, including the
`via_breaker` flag (the address is reachable from illicit funds only through a
commingling intermediary, so the exposure is not attributable).
"""
from __future__ import annotations

from collections import deque

_EPS = 1e-4


def _adjacency(edges):
    adj = {}
    for src, dst, frac in edges:
        adj.setdefault(src, []).append((dst, frac))
    return adj


def propagate_taint(edges, seeds, breakers=frozenset(), *, max_hops=6,
                    hop_decay=0.6, ignore_breakers=False):
    """Forward-propagate taint from `seeds` ({node: severity}) along `edges`
    ((src, dst, transfer_fraction)). A node's taint via a path is
    severity x prod(transfer_fraction) x hop_decay^hops; the strongest path wins.
    Propagation does not continue out of a breaker node (unless ignore_breakers).
    Returns {node: {"exposure", "hops", "seed"}} for all reached non-seed nodes."""
    adj = _adjacency(edges)
    best = {}
    for seed, sev in seeds.items():
        dq = deque([(seed, float(sev), 0)])
        while dq:
            node, taint, hops = dq.popleft()
            if hops >= max_hops:
                continue
            if node in breakers and hops > 0 and not ignore_breakers:
                continue  # commingling intermediary breaks attribution downstream
            for nb, frac in adj.get(node, []):
                nt = taint * frac * hop_decay
                nh = hops + 1
                cur = best.get(nb)
                if cur is None or nt > cur[0]:
                    best[nb] = (nt, nh, seed)
                if nt > _EPS:
                    dq.append((nb, nt, nh))
    return {n: {"exposure": v[0], "hops": v[1], "seed": v[2]} for n, v in best.items()}


def address_exposure(edges, seeds, target, breakers=frozenset(), *,
                     max_hops=6, hop_decay=0.6):
    """Exposure features for one target address. Runs propagation twice — honouring
    breakers (real, attributable exposure) and ignoring them (potential exposure) —
    so a `via_breaker` case (potential exposure exists but is broken by a commingling
    intermediary) is detectable. Returns a feature dict the disposition engine
    consumes."""
    real = propagate_taint(edges, seeds, breakers, max_hops=max_hops, hop_decay=hop_decay)
    potential = propagate_taint(edges, seeds, breakers, max_hops=max_hops,
                                hop_decay=hop_decay, ignore_breakers=True)
    r = real.get(target)
    p = potential.get(target)
    if r and r["exposure"] > _EPS:
        return {"exposure": r["exposure"], "hops": r["hops"], "seed": r["seed"],
                "via_breaker": False}
    if p and p["exposure"] > _EPS:
        # only reachable from illicit funds through a breaker -> not attributable
        return {"exposure": 0.0, "hops": p["hops"], "seed": p["seed"], "via_breaker": True}
    return {"exposure": 0.0, "hops": None, "seed": None, "via_breaker": False}
