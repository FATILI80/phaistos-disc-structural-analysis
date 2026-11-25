"""Was legen 241 Zeichen / 61 Woerter ueberhaupt fest?  Schaetzung von Zeichen-Inventar und Wortschatz mit Unsicherheit.
Basis: phaistos_test.py v2.  Keine Lautwerte, keine Deutung - nur Groessenordnungen, die jede Deutung erfuellen muss."""
import numpy as np
from collections import Counter
import phaistos_test as P

def species(counts):
    c = Counter(counts); S = len(counts); N = sum(counts); f1, f2 = c[1], c[2]
    return dict(S=S, N=N, f1=f1, f2=f2, chao1=S + f1 * (f1 - 1) / (2 * (f2 + 1)), new_next=f1 / N)

def boot_chao(counts, n=4000, seed=2):
    rng = np.random.default_rng(seed); counts = np.array(counts); N = counts.sum(); out = []
    for _ in range(n):
        s = rng.multinomial(N, counts / N); s = s[s > 0]; out.append(species(list(s))["chao1"])
    return np.percentile(out, [5, 50, 95])

def abc_lexicon(S_obs, f2_obs, N, sims=60000, seed=5):
    rng = np.random.default_rng(seed); acc = []
    for _ in range(sims):
        V = int(np.exp(rng.uniform(np.log(40), np.log(4000)))); s = rng.uniform(0.3, 2.0)
        p = np.arange(1, V + 1) ** -s; p /= p.sum()
        c = np.bincount(rng.choice(V, size=N, p=p)); c = c[c > 0]
        if abs(len(c) - S_obs) <= 1 and abs((c == 2).sum() - f2_obs) <= 1: acc.append((V, s))
    return np.array(acc)

if __name__ == "__main__":
    for vn, ws in P.variants(P.parse(P.DATA)).items():
        signs = Counter(s for w in ws for s in w["signs"]); words = Counter(tuple(w["signs"]) for w in ws)
        a = species(list(signs.values())); b = species(list(words.values()))
        print(f"=== {vn} ===")
        print(f"ZEICHEN: {a['S']} Typen in {a['N']} Tokens; einmal belegt f1={a['f1']}, zweimal f2={a['f2']}; "
              f"Chao1={a['chao1']:.1f} (90%-Bootstrap {boot_chao(list(signs.values()))[0]:.0f}-{boot_chao(list(signs.values()))[2]:.0f}); P(naechstes Zeichen neu)={a['new_next']:.3f}")
        print(f"WOERTER: {b['S']} Typen in {b['N']} Tokens; f1={b['f1']}, f2={b['f2']}; Chao1={b['chao1']:.0f}; P(naechstes Wort neu)={b['new_next']:.2f}")
        acc = abc_lexicon(b["S"], b["f2"], b["N"])
        V = acc[:, 0]; s = acc[:, 1]
        print(f"ABC Zipf-Wortschatz (Prior V 40-4000 log-gleichverteilt, s 0.3-2): akzeptiert {len(acc)} Simulationen")
        print(f"   Wortschatzgroesse V: Median {np.median(V):.0f}, 90%-Intervall {np.percentile(V,5):.0f}-{np.percentile(V,95):.0f}; P(V<100)={np.mean(V<100):.3f}; P(V>1000)={np.mean(V>1000):.3f}")
        print(f"   Zipf-Exponent s: Median {np.median(s):.2f}, 90%-Intervall {np.percentile(s,5):.2f}-{np.percentile(s,95):.2f}")
