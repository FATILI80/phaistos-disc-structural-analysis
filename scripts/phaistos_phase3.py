"""Phase 3 (Claude-Slots): B Mehrfachtest-Korrektur, G Trennschaerfe, Gegenrechnung Silhouette k=2..6 + Pilot-Tests. Basis: phaistos_test.py v2."""
import math, random
import numpy as np
from collections import Counter
from scipy.stats import binom, fisher_exact, mannwhitneyu
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
import phaistos_test as P
import phaistos_audit_v3 as Q

W = P.parse(P.DATA)
A = [w["signs"] for w in W if w["id"][0] == "A"]; B = [w["signs"] for w in W if w["id"][0] == "B"]

def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); m = len(ps); out = [False] * m
    for r, i in enumerate(o):
        if ps[i] <= 0.05 / (m - r): out[i] = True
        else: break
    return out

def bh(ps, q=0.05):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); m = len(ps); k = -1
    for r, i in enumerate(o):
        if ps[i] <= q * (r + 1) / m: k = r
    keep = set(o[:k + 1]); return [i in keep for i in range(m)]

def ledger():
    T = [("H1 Sequenz-Entropie (Wort-Perm.)", 0.0002), ("02 strikt initial", 0.0002), ("Bigramm 02-12 (Fisher)", 1e-11),
         ("A/B-Divergenz JSD (Wort-Perm.)", 0.0004), ("Max. Wiederholungen ALL", 0.002), ("Max. Wiederholungen STRICT", 0.005),
         ("A/B-Anteil 02 initial (Fisher)", 0.026), ("Silhouette k=5 vs Zufall", 0.010), ("Dorn je Wortform einheitlich (STRICT)", 0.040),
         ("Gemination", 0.213), ("Kadenz [28-01] STRICT", 0.143), ("Kompl. 02/01 (pos.-erh.)", 0.341), ("Kompl. 29/31", 0.350),
         ("Kompl. 24/25", 0.133), ("Revesz-Vokalharmonie", 0.055), ("Replik. A: 02-12", 1.2e-10), ("Replik. B: 02-12", 0.110),
         ("Max. Wiederh. Seite A", 0.005), ("Max. Wiederh. Seite B", 0.0175)]
    ps = [p for _, p in T]; h, b = holm(ps), bh(ps)
    print(f"[B] Ledger: {len(T)} Tests, Holm/BH ueber alle (alpha 0,05). Wahrscheinlichkeit mind. eines Zufallstreffers bei 19 Tests: {1-0.95**19:.2f}")
    for (n, p), x, y in sorted(zip(T, h, b), key=lambda t: t[0][1]):
        print(f"   p={p:<9g} Holm={'ja ' if x else 'nein'} BH={'ja ' if y else 'nein'}  {n}")

def power_prefix(m=50):
    print("[G1] Trennschaerfe Praefix-Test (Bonferroni m=50): Wahrscheinlichkeit, dass ein Zeichen mit n Vorkommen als Praefix erkannt wird, wenn f seiner Vorkommen initial sind")
    q0 = 61 / 241
    for n in (5, 8, 12, 19):
        kc = next((k for k in range(n + 1) if binom.sf(k - 1, n, q0) < 0.05 / m), None)
        if kc is None: print(f"   n={n:2d}: auch 100 % initial reicht bei Bonferroni m={m} nicht (nicht erkennbar)"); continue
        row = [f"f={f}: {binom.sf(kc - 1, n, f):.2f}" for f in (0.5, 0.7, 0.9, 1.0)]
        print(f"   n={n:2d} (kritisch >= {kc} initial)  " + " | ".join(row))

def h1(words):
    big = [(a, b) for w in words for a, b in zip(w, w[1:])]
    def H(c):
        t = sum(c.values()); return -sum(v / t * math.log2(v / t) for v in c.values())
    return H(Counter(big)) - H(Counter(a for a, b in big))

def within_null(words, rng, n=150):
    out = []
    for _ in range(n):
        out.append(h1([rng.sample(w, len(w)) for w in words]))
    return np.mean(out), np.std(out)

def power_h1(reps=60, seed=3):
    rng = random.Random(seed); lens = [len(w) for w in A + B]; V = list(range(1, 46))
    succ = {s: rng.sample(V, 3) for s in V}   # feste "Grammatik": je 3 bevorzugte Nachfolger
    w_uni = np.array([1 / (i + 3) for i in range(45)]); w_uni /= w_uni.sum()
    print("[G2] Trennschaerfe Sequenz-Entropie-Test (Wort-Perm.-Null, alpha 0,01): Anteil erkannter synthetischer Korpora (61 Woerter wie v2)")
    for lam in (0.0, 0.1, 0.2, 0.3, 0.5):
        hit = 0
        for _ in range(reps):
            ws = []
            for L in lens:
                w = [rng.choices(V, w_uni)[0]]
                while len(w) < L: w.append(rng.choice(succ[w[-1]]) if rng.random() < lam else rng.choices(V, w_uni)[0])
                ws.append(w)
            m, s = within_null(ws, rng); hit += (h1(ws) - m) / s < -2.33
        print(f"   Strukturanteil lambda={lam}: erkannt {hit/reps:.2f}")

def silh_scan():
    cnt = Counter(s for w in W for s in w["signs"]); signs = sorted(s for s, c in cnt.items() if c >= 4)
    X = Q.ctx_matrix(A + B, signs) + 1e-9; Z = linkage(pdist(X, "cosine"), "ward")
    print("[Gegenrechnung] Kosinus-Silhouette k=2..6:", {k: round(Q.silhouette(X, fcluster(Z, k, "maxclust")), 3) for k in range(2, 7)})

def pilots():
    dA = sum(w["dorn"] for w in W if w["id"][0] == "A"); dB = sum(w["dorn"] for w in W if w["id"][0] == "B")
    print(f"[Pilot] Dorne A {dA}/31 vs B {dB}/30: Fisher p={fisher_exact([[dA, 31-dA], [dB, 30-dB]])[1]:.3f}")
    print(f"[Pilot] Wortlaenge A {np.mean([len(w) for w in A]):.2f} vs B {np.mean([len(w) for w in B]):.2f}: Mann-Whitney p={mannwhitneyu([len(w) for w in A], [len(w) for w in B])[1]:.3f}")

if __name__ == "__main__":
    ledger(); power_prefix(); silh_scan(); pilots(); power_h1()
