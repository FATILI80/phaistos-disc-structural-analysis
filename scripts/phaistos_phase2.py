"""Phase 2 (Module 1-2): Datenaudit des Gemini-Blocks, Affix-Test mit Nullmodell, Wurzelfamilien, Kontext-Aehnlichkeit.
Basis: phaistos_test.py v2 (abgeglichen gegen Wikipedia-Transkription + Godart-Haeufigkeitstabelle)."""
import random, sys
from collections import Counter, defaultdict
import phaistos_test as P

GEM = {  # Datenblock aus Geminis Handoff (unveraendert abgetippt)
"A1":[2,12,13,1,18],"A2":[24,40,12],"A3":[29,45,7],"A4":[29,29,34],"A5":[2,12,4,40,33],"A6":[27,45,7,12],"A7":[27,44,8],"A8":[2,12,6,18,42],"A9":[27,26,35],"A10":[2,12,41,19,35],"A11":[1,41,40,7],"A12":[2,12,32,23,38],"A13":[39,11],"A14":[2,27,25,10,23,18],"A15":[28,1],"A16":[2,12,31,26],"A17":[2,12,27,27,35,37,21],"A18":[33,23],"A19":[2,12,31,26],"A20":[2,27,25,10,23,18],"A21":[28,1],"A22":[2,12,31,26],"A23":[2,12,27,14,32,18,27],"A24":[6,18,17,19],"A25":[31,26,12],"A26":[2,12,13,1],"A27":[23,19,35,1,41],"A28":[10,3,38],"A29":[2,12,27,27,35,37,21],"A30":[13,1],"A31":[10,3,38],
"B1":[2,12,22,40,7],"B2":[27,45,7,35],"B3":[2,37,23,5],"B4":[22,25,27],"B5":[33,24,20,12],"B6":[16,23,18,43],"B7":[13,1,39,33],"B8":[15,9,27,12],"B9":[27,18,22,31,26],"B10":[22,25,27],"B11":[7,24,40,35],"B12":[2,26,36,40],"B13":[27,25,38,1],"B14":[29,24,24,20,35],"B15":[16,14,18],"B16":[29,33,1],"B17":[6,35,32,39,33],"B18":[2,9,27,1],"B19":[29,36,7,8],"B20":[29,8,13],"B21":[29,45,7],"B22":[22,29,36,7,8],"B23":[27,34,23,25],"B24":[7,18,35],"B25":[7,45,7],"B26":[7,23,18,24],"B27":[22,29,36,7,8],"B28":[9,30,39,18,7],"B29":[2,6,35,23,7],"B30":[29,34,23,25]}

def audit_gemini():
    W = {w["id"]: w["signs"] for w in P.parse(P.DATA)}
    diff = [k for k in W if GEM[k] != W[k]]
    ca, cb = Counter(), Counter()
    for k, v in GEM.items(): (ca if k[0] == "A" else cb).update(v)
    fa = [ca[i] for i in range(1, 46)] == P.FREQ_A; fb = [cb[i] for i in range(1, 46)] == P.FREQ_B
    print(f"[AUDIT] Gemini-Block: {len(diff)} von 61 Woertern weichen von v2 ab: {diff}")
    print(f"[AUDIT] Zeichen A={sum(map(len,[v for k,v in GEM.items() if k[0]=='A']))} B={sum(map(len,[v for k,v in GEM.items() if k[0]=='B']))} | Godart-Haeufigkeit A:{fa} B:{fb}")

def perm_pos(words, n=5000, seed=3):
    rng = random.Random(seed); lens = [len(w) for w in words]; flat = [s for w in words for s in w]
    def pos(ws):
        ini, fin, tot = Counter(), Counter(), Counter()
        for w in ws: tot.update(w); ini[w[0]] += 1; fin[w[-1]] += 1
        return ini, fin, tot
    oi, of, tot = pos(words); big = Counter((w[0], w[1]) for w in words)
    gi, gf, gb = Counter(), Counter(), Counter()
    for _ in range(n):
        rng.shuffle(flat); i = 0; ws = []
        for L in lens: ws.append(flat[i:i+L]); i += L
        ni, nf, _ = pos(ws)
        for s in tot: gi[s] += ni[s] >= oi[s]
        for s in tot: gf[s] += nf[s] >= of[s]
    return oi, of, tot, {s: (gi[s]+1)/(n+1) for s in tot}, {s: (gf[s]+1)/(n+1) for s in tot}

def affixes():
    res = {}
    for vn, ws in P.variants(P.parse(P.DATA)).items():
        words = [w["signs"] for w in ws]
        oi, of, tot, pi, pf = perm_pos(words)
        cand = [s for s in tot if tot[s] >= 4]; m = 2 * len(cand)   # Bonferroni ueber Zeichen x {initial, final}
        res[vn] = ({s for s in cand if pi[s]*m < 0.05}, {s for s in cand if pf[s]*m < 0.05}, oi, of, tot)
        print(f"[AFFIX {vn}] getestet {len(cand)} Zeichen (n>=4), Bonferroni m={m}")
        print("   Praefix-Kandidaten (initial):", {s: f"{oi[s]}/{tot[s]}" for s in sorted(res[vn][0])})
        print("   Suffix-Kandidaten (final):  ", {s: f"{of[s]}/{tot[s]}" for s in sorted(res[vn][1])})
    return res

def families(res):
    pre, suf = res["ALL"][0] & res["STRICT"][0], res["ALL"][1] & res["STRICT"][1]
    words = {w["id"]: w["signs"] for w in P.parse(P.DATA)}
    roots = defaultdict(list)
    for k, w in words.items():
        a, b = 0, len(w)
        while a < b - 1 and w[a] in pre: a += 1
        if b - a > 1 and w[b-1] in suf: b -= 1
        roots[tuple(w[a:b])].append(k)
    fam = {r: v for r, v in roots.items() if len(v) >= 2}
    print(f"[SEGMENT] Praefixe {sorted(pre)} Suffixe {sorted(suf)} (in ALL und STRICT signifikant); {len(roots)} Wurzelformen, {len(fam)} davon in >=2 Woertern:")
    for r, v in sorted(fam.items(), key=lambda x: -len(x[1])): print("   ", "-".join(f"{s:02d}" for s in r), v)

def contexts(words):
    L, R, C = defaultdict(set), defaultdict(set), Counter()
    for w in words:
        for i, s in enumerate(w):
            C[s] += 1; L[s].add(w[i-1] if i else "^"); R[s].add(w[i+1] if i < len(w)-1 else "$")
    return L, R, C

def ctx_sim(words, a, b):
    L, R, C = contexts(words)
    j = lambda x, y: len(x & y) / len(x | y) if x | y else 0
    return (j(L[a], L[b]) + j(R[a], R[b])) / 2, C[a], C[b]

def complementary(n=3000, seed=4):
    words = [w["signs"] for w in P.parse(P.DATA)]; rng = random.Random(seed)
    lens = [len(w) for w in words]; flat = [s for w in words for s in w]
    for a, b in [(2, 1), (29, 31), (24, 25)]:
        obs, na, nb = ctx_sim(words, a, b); lo = 0
        for _ in range(n):
            rng.shuffle(flat); i = 0; ws = []
            for Ln in lens: ws.append(flat[i:i+Ln]); i += Ln
            lo += ctx_sim(ws, a, b)[0] <= obs
        print(f"[KOMPL] {a:02d} vs {b:02d}: n={na}/{nb}, Kontext-Aehnlichkeit {obs:.3f}, p(so unaehnlich oder unaehnlicher bei Zufall)={(lo+1)/(n+1):.3f}")

if __name__ == "__main__":
    audit_gemini(); res = affixes(); families(res); complementary()
