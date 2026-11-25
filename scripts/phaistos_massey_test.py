"""Massey & Massey (1998): Test des Anspruchs 'Schraegstrich-Woerter = Zahlwoerter'. Basis: phaistos_test.py v2.
VOR dem Lauf festgelegte Regeln (Vorregistrierung):
 Leserichtung 'outward' (Massey liest von innen nach aussen): jedes Wort wird umgekehrt.
 Zeichenwerte: aus Masseys eigener Tabelle der 17 Schraegstrich-Woerter (PDF S. 63) abgeleitet; Zeichen ohne Wert = '?'.
 Zahlwortmuster: Vidals Liste (PDF S. 64), Klammern = optional. Q=K, V(okalzeichen) passt zu E/O, '?' passt auf jeden Buchstaben.
 Pruefbar sind Woerter mit hoechstens einem '?'. Optional darf eine Schlussgruppe K-Y (Massey: Enklitikon) entfernt werden.
 R1: Skelett gleich Muster. R2: wie R1, aber eine Abweichung (Editierdistanz <= 1) erlaubt.
 Wichtig: Die Werte sind an den 17 Woertern selbst angepasst (zirkulaer). Aussagekraft hat nur der Vergleich mit den uebrigen Woertern."""
import random, itertools
from scipy.stats import fisher_exact
import phaistos_test as P

MASSEY = {"A1": "W V N K Y", "A3": "T R Y", "A12": "? T K K Y", "A15": "V S", "A16": "W K K Y", "A19": "W K K Y", "A21": "V S",
          "A22": "W K K Y", "A27": "? ? T", "B3": "V T ? Y", "B6": "T W T ?", "B18": "K T R Y", "B20": "T R Y", "B21": "K T R Y ?",
          "B24": "T R T", "B26": "K T R Y ?", "B30": "T R"}
VIDAL = ["E-S", "D-W", "T-R-(Y)-(S)", "Q-T-R-(S)", "P-(N)-Q", "W-(K)-S", "E-(P)-T", "O-(K)-T", "E-N-W", "D-K", "E-(N)-D-K", "D-(W)-D-K", "T-R-(Y)-(S)-K-(Y)-D-K"]

def expand(p):
    toks = p.split("-"); outs = []
    for mask in itertools.product([0, 1], repeat=len(toks)):
        s = []
        for t, m in zip(toks, mask):
            opt = t.startswith("(")
            if opt and not m: continue
            if not opt and not m: continue
            s.append(t.strip("()"))
        # nicht-optionale Tokens muessen immer drin sein
        if all((not t.startswith("(")) <= bool(m) for t, m in zip(toks, mask)): outs.append(tuple(s))
    return set(outs)
NUM = sorted({e for p in VIDAL for e in expand(p)})

def eq(c, e):
    return c == "?" or c == e or (c == "V" and e in "EO") or (c == "K" and e == "Q")

def lev1(a, b):  # Editierdistanz <= 1 mit eq
    if len(a) == len(b): return sum(not eq(x, y) for x, y in zip(a, b)) <= 1
    if abs(len(a) - len(b)) > 1: return False
    if len(a) > len(b): a, b = b, a
    for i in range(len(b)):
        if all(eq(x, y) for x, y in zip(a, b[:i] + b[i+1:])): return True
    return False

def match(sk, loose):
    variants = [sk] + ([sk[:-2]] if len(sk) > 2 and sk[-2:] == ("K", "Y") else [])
    for v in variants:
        if len(v) < 2: continue
        for n in NUM:
            if (len(v) == len(n) and all(eq(c, e) for c, e in zip(v, n))) or (loose and lev1(v, n)): return True
    return False

def build_map(words):
    m = {}
    for k, sk in MASSEY.items():
        rev = words[k]["signs"][::-1]; lt = sk.split(); assert len(rev) == len(lt), k
        for s, l in zip(rev, lt):
            if l != "?":
                assert m.setdefault(s, l) == l, f"Konflikt Zeichen {s}: {m[s]} vs {l}"
    return m

def skeleton(w, m): return tuple(m.get(s, "?") for s in w["signs"][::-1])

if __name__ == "__main__":
    words = {w["id"]: w for w in P.parse(P.DATA)}
    assert [k for k, w in words.items() if w["dorn"]] == list(MASSEY), "Dornwoerter != Masseys 17 Woerter"
    m = build_map(words); print("Abgeleitete Zeichenwerte (aus Masseys Tabelle der 17 Schraegstrich-Woerter):", dict(sorted(m.items())))
    print("Ausrichtung widerspruchsfrei, 17 von 17 Dornwoertern = Masseys 17 Woerter")
    for loose in (False, True):
        el = {k: skeleton(w, m) for k, w in words.items() if sum(c == "?" for c in skeleton(w, m)) <= 1}
        sl = [k for k in el if words[k]["dorn"]]; un = [k for k in el if not words[k]["dorn"]]
        hs = [k for k in sl if match(el[k], loose)]; hu = [k for k in un if match(el[k], loose)]
        tab = [[len(hs), len(sl) - len(hs)], [len(hu), len(un) - len(hu)]]
        print(f"[{'R2 (locker)' if loose else 'R1 (streng)'}] pruefbare Woerter: Dorn {len(sl)}, ohne Dorn {len(un)} | Treffer Dorn {len(hs)}/{len(sl)}, ohne Dorn {len(hu)}/{len(un)} | Fisher p={fisher_exact(tab)[1]:.3f}")
        print("   Treffer mit Dorn:", hs, "| ohne Dorn:", hu)
        # Nullmodell: Zeichenwerte der 17 zugeordneten Zeichen zufaellig umverteilt
        rng = random.Random(3); keys = list(m); vals = list(m.values()); ge = 0; n = 2000
        for _ in range(n):
            rng.shuffle(vals); mm = dict(zip(keys, vals))
            ge += sum(match(skeleton(words[k], mm), loose) for k in sl if sum(c == "?" for c in skeleton(words[k], mm)) <= 1) >= len(hs)
        print(f"   Zufalls-Umverteilung der Werte: p(>= {len(hs)} Treffer bei Dornwoertern)={(ge+1)/(n+1):.3f}")
