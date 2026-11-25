"""Gegenpruefung der 'Durchbruch'-Behauptungen (Gemini-Handoff). Basis: phaistos_test.py v2.
Grundsatz: Nullmodelle auf WORTEBENE (Woerter bleiben ganz), jede Behauptung einzeln, ohne Interpretation."""
import math, random
import numpy as np
from collections import Counter
from math import comb
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import phaistos_test as P

W = P.parse(P.DATA); STRICT = P.variants(W)["STRICT"]
sg = lambda ws: [w["signs"] for w in ws]
A = [w["signs"] for w in W if w["id"][0] == "A"]; B = [w["signs"] for w in W if w["id"][0] == "B"]
rng = random.Random(11)

def kadenz(ws_a):
    long_ = [i for i, s in enumerate(ws_a[:-1]) if len(s) >= 6]
    kad = [i for i in range(1, len(ws_a)) if ws_a[i] == [28, 1]]
    hits = sum((i-1) in long_ for i in kad); N = len(ws_a) - 1
    p = sum(comb(len(long_), x) * comb(N - len(long_), len(kad) - x) for x in range(hits, min(len(long_), len(kad)) + 1)) / comb(N, len(kad))
    return hits, len(kad), len(long_), N, p

def gemination(words, n=5000):
    obs = sum(a == b for w in words for a, b in zip(w, w[1:]))
    flat = [s for w in words for s in w]; lens = [len(w) for w in words]; lo = 0
    for _ in range(n):
        rng.shuffle(flat); i = 0; c = 0
        for L in lens:
            seg = flat[i:i+L]; i += L; c += sum(a == b for a, b in zip(seg, seg[1:]))
        lo += c <= obs
    return obs, (lo + 1) / (n + 1)

def jsd(x, y):
    px = np.array([x[i] for i in range(1, 46)], float) + 0.0; py = np.array([y[i] for i in range(1, 46)], float)
    px /= px.sum(); py /= py.sum(); m = (px + py) / 2
    kl = lambda p, q: sum(a * math.log2(a / b) for a, b in zip(p, q) if a > 0)
    return (kl(px, m) + kl(py, m)) / 2

def side_test(n=5000):
    obs = jsd(Counter(s for w in A for s in w), Counter(s for w in B for s in w))
    ws = A + B; hi = 0; tok = []; 
    for _ in range(n):
        rng.shuffle(ws); a, b = ws[:31], ws[31:]
        hi += jsd(Counter(s for w in a for s in w), Counter(s for w in b for s in w)) >= obs
    return obs, (hi + 1) / (n + 1)

def silhouette(X, lab):
    D = squareform(pdist(X, metric="cosine")); s = []
    for i in range(len(X)):
        same = [j for j in range(len(X)) if lab[j] == lab[i] and j != i]
        if not same: continue
        a = np.mean(D[i, same]); b = min(np.mean(D[i, [j for j in range(len(X)) if lab[j] == c]]) for c in set(lab) if c != lab[i])
        s.append((b - a) / max(a, b))
    return float(np.mean(s))

def ctx_matrix(words, signs):
    X = []
    for s in signs:
        v = np.zeros(2 * 47)
        for w in words:
            for i, x in enumerate(w):
                if x == s:
                    v[w[i-1] if i else 46] += 1; v[47 + (w[i+1] if i < len(w)-1 else 46)] += 1
        X.append(v)
    return np.array(X)

def cluster_test(n=300, k=5):
    cnt = Counter(s for w in W for s in w["signs"]); signs = sorted(s for s, c in cnt.items() if c >= 4)
    def sil(words):
        X = ctx_matrix(words, signs); X = X + 1e-9
        return silhouette(X, fcluster(linkage(pdist(X, "cosine"), "ward"), k, "maxclust"))
    obs = sil(A + B); lens = [len(w) for w in A + B]; flat = [s for w in A + B for s in w]; ge = 0; vals = []
    for _ in range(n):
        rng.shuffle(flat); i = 0; ws = []
        for L in lens: ws.append(flat[i:i+L]); i += L
        v = sil(ws); vals.append(v); ge += v >= obs
    return obs, float(np.mean(vals)), (ge + 1) / (n + 1)

# ---- HMM (Baum-Welch, skaliert), Held-out A->B und B->A ----
def hmm_fit(seqs, K=4, V=46, it=60, seed=0):
    r = np.random.default_rng(seed); pi = r.dirichlet(np.ones(K)); T = r.dirichlet(np.ones(K), K); E = r.dirichlet(np.ones(V), K)
    for _ in range(it):
        pi_n = np.zeros(K); T_n = np.zeros((K, K)); E_n = np.zeros((K, V))
        for o in seqs:
            n = len(o); al = np.zeros((n, K)); c = np.zeros(n)
            al[0] = pi * E[:, o[0]]; c[0] = al[0].sum(); al[0] /= c[0]
            for t in range(1, n): al[t] = (al[t-1] @ T) * E[:, o[t]]; c[t] = al[t].sum(); al[t] /= c[t]
            be = np.ones((n, K))
            for t in range(n-2, -1, -1): be[t] = (T @ (E[:, o[t+1]] * be[t+1])) / c[t+1]
            g = al * be; g /= g.sum(1, keepdims=True); pi_n += g[0]
            for t in range(n-1):
                x = al[t][:, None] * T * (E[:, o[t+1]] * be[t+1])[None, :]; T_n += x / x.sum()
            for t in range(n): E_n[:, o[t]] += g[t]
        pi = pi_n / pi_n.sum(); T = (T_n + 1e-3) / (T_n + 1e-3).sum(1, keepdims=True); E = (E_n + 0.05) / (E_n + 0.05).sum(1, keepdims=True)
    return pi, T, E

def hmm_ll(seqs, m):
    pi, T, E = m; tot = 0.0
    for o in seqs:
        a = pi * E[:, o[0]]; c = a.sum(); tot += math.log(c); a /= c
        for t in range(1, len(o)): a = (a @ T) * E[:, o[t]]; c = a.sum(); tot += math.log(c); a /= c
    return tot

def uni_ll(train, test, k=0.5):
    c = Counter(s for w in train for s in w); N = sum(c.values())
    return sum(math.log((c[s] + k) / (N + k * 45)) for w in test for s in w)

def big_ll(train, test, k=0.05):
    c = Counter(); cc = Counter()
    for w in train:
        p = 0
        for s in w: c[(p, s)] += 1; cc[p] += 1; p = s
    tot = 0.0
    for w in test:
        p = 0
        for s in w: tot += math.log((c[(p, s)] + k) / (cc[p] + k * 45)); p = s
    return tot

def hmm_heldout():
    for name, tr, te in (("A->B", A, B), ("B->A", B, A)):
        nt = sum(map(len, te)); best = max((hmm_ll(te, hmm_fit(tr, seed=s)) for s in range(3)), default=0)
        # fairer: waehle Seed nach TRAININGS-LL
        fits = [hmm_fit(tr, seed=s) for s in range(3)]; m = max(fits, key=lambda f: hmm_ll(tr, f))
        print(f"   HMM {name}: held-out {hmm_ll(te, m)/nt:.3f} nats/Zeichen | Unigramm {uni_ll(tr, te)/nt:.3f} | Bigramm {big_ll(tr, te)/nt:.3f}")

def ring():
    b = [w for w in W if w["id"][0] == "B"]; ids = [w["id"] for w in b]
    eq = [(x["id"], y["id"]) for i, x in enumerate(b) for y in b[i+1:] if x["signs"] == y["signs"]]
    print(f"   exakt gleiche Woerter auf Seite B: {eq}")
    for c in (23, 24, 25):
        pairs = [(c-d, c+d) for d in range(1, 7) if c-d >= 1 and c+d <= 30]
        sim = [(f"B{i}", f"B{j}", len(set(b[i-1]['signs']) & set(b[j-1]['signs']))) for i, j in pairs]
        print(f"   Spiegelpaare um B{c} (gemeinsame Zeichen): {sim}")

if __name__ == "__main__":
    print("[1] Kadenz [28-01] nach Langvers (>=6), hypergeom")
    print("   ALL   : hits=%d/%d, Langverse=%d/%d, p=%.5f" % kadenz(A)[:4] + ("" ,)[0] if False else "", end="")
    h = kadenz(A); print("   ALL   : %d/%d Treffer, Langverse %d von %d, p=%.5f" % h)
    As = [w["signs"] for w in STRICT if w["id"][0] == "A"]; h = kadenz(As); print("   STRICT: %d/%d Treffer, Langverse %d von %d, p=%.5f (A20/A21 sind Kopien von A14/A15)" % h)
    print("[2] Gemination (gleiche Folgezeichen):"); o, p = gemination(sg(W)); print(f"   beobachtet {o} von 180 Uebergaengen; p(<=beob., Wort-Permutation)={p:.3f}")
    print("[3] Seiten-Unterschied JSD, Nullmodell = Woerter zwischen A und B vertauscht:"); o, p = side_test(); print(f"   JSD={o:.4f}, p={p:.4f}")
    print("[4] Ward-Cluster (k=5): Silhouette real vs. Zufall (Zeichen gemischt)"); o, m, p = cluster_test(); print(f"   real {o:.3f} | Zufall {m:.3f} | p={p:.3f}")
    print("[5] HMM (4 Zustaende) held-out:"); hmm_heldout()
    print("[6] Ring-Komposition B21-B30:"); ring()
