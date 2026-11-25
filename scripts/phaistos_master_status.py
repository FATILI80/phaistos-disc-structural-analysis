"""Erzeugt die Master-Kennzahlen aus phaistos_test.py v2. Nichts wird abgetippt: alle Zahlen kommen aus der Datei."""
import phaistos_test as P
from scipy.stats import fisher_exact, binom
W = P.parse(P.DATA); assert all(P.integrity(W).values()), "Datensatz nicht v2-konform"
V = P.variants(W); no8 = [w for w in W if w["id"] != "A8"]
side = lambda ws, s: [w for w in ws if w["id"][0] == s]
def facts(ws):
    sg = lambda s: [w for w in side(ws, s)]
    n = lambda l: sum(len(w["signs"]) for w in l)
    z02 = {s: sum(x == 2 for w in sg(s) for x in w["signs"]) for s in "AB"}
    ini = {s: sum(w["signs"][0] == 2 for w in sg(s)) for s in "AB"}
    big = {s: sum(w["signs"][i:i+2] == [2, 12] for w in sg(s) for i in range(len(w["signs"]) - 1)) for s in "AB"}
    d = {s: sum(w["dorn"] for w in sg(s)) for s in "AB"}
    return dict(felder=(len(ws), len(sg("A")), len(sg("B"))), zeichen=n(ws), z02=z02, z02_initial=ini, bigramm_02_12=big, dorne=d)
if __name__ == "__main__":
    for name, ws in (("ALL", W), ("STRICT", V["STRICT"]), ("NO_A8", no8)): print(name, facts(ws))
    f = facts(W); dA, dB = f["dorne"]["A"], f["dorne"]["B"]
    print("Dorne A/B Fisher exakt p =", round(fisher_exact([[dA, 31 - dA], [dB, 30 - dB]])[1], 4))
    print("02 initial: A %d/%d, B %d/%d" % (f["z02_initial"]["A"], f["z02"]["A"], f["z02_initial"]["B"], f["z02"]["B"]))
    print("Binomial 02 initial A (q=31/122):", "%.2e" % binom.sf(13, 14, 31 / 122), "| B (q=30/119):", "%.2e" % binom.sf(4, 5, 30 / 119))


# --- Sequenz-Ordnung und Wiederholungen (Werte im README stammen aus diesem Teil) ---
import math, random
from collections import Counter, defaultdict

def h1(words):
    big = [(a, b) for w in words for a, b in zip(w, w[1:])]
    H = lambda c: -sum(v / sum(c.values()) * math.log2(v / sum(c.values())) for v in c.values())
    return H(Counter(big)) - H(Counter(a for a, _ in big))

def null_global(words, rng):
    flat = [s for w in words for s in w]; rng.shuffle(flat); out, i = [], 0
    for w in words: out.append(flat[i:i + len(w)]); i += len(w)
    return out

def null_positional(words, rng):
    ini = [w[0] for w in words]; fin = [w[-1] for w in words]; med = [s for w in words for s in w[1:-1]]
    rng.shuffle(ini); rng.shuffle(fin); rng.shuffle(med); out, k = [], 0
    for i, w in enumerate(words):
        m = med[k:k + len(w) - 2]; k += len(w) - 2; out.append([ini[i]] + m + [fin[i]])
    return out

def maximal_repeats(words):
    occ = defaultdict(set)
    for i, w in enumerate(words):
        for a in range(len(w)):
            for b in range(a + 2, len(w) + 1): occ[tuple(w[a:b])].add(i)
    rep = {s: f for s, f in occ.items() if len(f) >= 2}
    sup = lambda s, f: any(len(t) > len(s) and g == f and any(t[i:i + len(s)] == s for i in range(len(t) - len(s) + 1)) for t, g in rep.items())
    return sum(not sup(s, f) for s, f in rep.items())

def mc(stat, words, nullf, n, seed, lower):
    rng = random.Random(seed); obs = stat(words); vals = [stat(nullf(words, rng)) for _ in range(n)]
    hit = sum((v <= obs) if lower else (v >= obs) for v in vals)
    m = sum(vals) / n; sd = (sum((v - m) ** 2 for v in vals) / n) ** 0.5
    return obs, m, sd, (hit + 1) / (n + 1)

if __name__ == "__main__":
    for name, ws in (("ALL", W), ("STRICT", V["STRICT"])):
        words = [w["signs"] for w in ws]
        o, m, sd, p = mc(h1, words, null_global, 5000, 1, True)
        print(f"{name} H(Xn|Xn-1) = {o:.3f} Bit | Null global {m:.3f} +- {sd:.3f}, p <= {p:.4f}")
        o, m, sd, p = mc(h1, words, lambda w, r: [r.sample(x, len(x)) for x in w], 5000, 1, True)
        print(f"{name} H(Xn|Xn-1) = {o:.3f} Bit | Null innerhalb der Woerter {m:.3f} +- {sd:.3f}, p <= {p:.4f}")
        o, m, sd, p = mc(maximal_repeats, words, null_positional, 1500, 9, False)
        print(f"{name} maximale Wiederholungen = {o} | Null positionserhaltend {m:.1f} +- {sd:.1f}, p = {p:.4f}")
