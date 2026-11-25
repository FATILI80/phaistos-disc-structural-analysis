"""
PHAISTOS-DISKUS - PHASE 2: PRUEFPROTOKOLL + TESTHARNESS (ein Block)
Rollen: Fatih = Projektleitung | Gemini = Deutungstabellen aus Quellen aufbauen | Claude = Code/Statistik-Audit

FRAGE: Schlaegt eine veroeffentlichte Deutung (Zeichen->Silbe-Tabelle) den Zufall?
Leitplanke: keine Uebersetzung, keine Gleichsetzung von Zeichenaehnlichkeit mit Sprachverwandtschaft.

ABLAUF FUER GEMINI
1. Pro Deutung EINE Datei claims/<name>.json:
   {"name":..., "source":"Autor, Jahr, Seite", "lexicon_source":"Woerterbuch/Korpus der behaupteten Sprache",
    "direction":"inward"|"outward" (Leserichtung laut Autor; Datensatz ist aussen->innen, "outward" kehrt jedes Wort um),
    "table":{"01":"pa","02":"ke",...}, "lexicon":["wort1","wort2",...]}
2. Tabelle NUR aus der Originalpublikation uebernehmen, auf Godart/Olivier-Nummerierung (01-45) umgesetzt;
   Umsetzung dokumentieren. Nichts aus KI-Gedaechtnis. Nicht belegbar -> Deutung als "unverifiziert" melden, nicht laufen lassen.
3. Lexikon aus einer veroeffentlichten Quelle der Sprache, nicht generiert und nicht nachtraeglich an die Scheibe angepasst.
4. Lauf: python phaistos_test.py run claims/*.json     (Selbsttest: python phaistos_test.py selftest)
5. Bericht je Deutung: Treffer, abgedeckte Wortformen, p roh, p Bonferroni (k = Zahl der Deutungen), Varianten ALL und STRICT.

ENTSCHEIDUNGSREGEL (vor dem Lauf festgelegt)
- "nicht widerlegt" nur wenn p_Bonferroni < 0.01 in ALL und STRICT. Sonst "nicht gestuetzt". Nie "bestaetigt".
- Bei 241 Zeichen kann auch ein bestandener Test Zufall sein. Er schliesst Deutungen aus, er beweist keine.

GRENZEN
- Getestet wird exakter Lexikontreffer auf Wortformen (Typen, Dubletten zaehlen einmal). Flexion/Morphologie wird nicht modelliert.
- Nullmodell: Silbenwerte der Tabelle werden zufaellig auf die Zeichen umverteilt (Werteverteilung bleibt gleich).
- Transkription: gegen Wikipedia-Transkription (Godart/Achterberg-Nummerierung) und Godart-Haeufigkeitstabelle abgeglichen, nicht gegen die Scheibe selbst.
- Korrektur v2: B28-B30 und Dorne B20, B24, B30 nach dieser Quelle berichtigt (vorher fehlerhaft).
"""
import json, random, sys
from collections import Counter

DATA = {
 "A": {"A1": "02-12-13-01-18T", "A2": "24-40-12", "A3": "29-45-07T", "A4": "29-29-34",
  "A5": "02-12-04-40-33", "A6": "27-45-07-12", "A7": "27-44-08", "A8": "02-12-06-18[ERASED]",
  "A9": "31-26-35", "A10": "02-12-41-19-35", "A11": "01-41-40-07", "A12": "02-12-32-23-38T",
  "A13": "39-11", "A14": "02-27-25-10-23-18", "A15": "28-01T", "A16": "02-12-31-26T",
  "A17": "02-12-27-27-35-37-21", "A18": "33-23", "A19": "02-12-31-26T", "A20": "02-27-25-10-23-18",
  "A21": "28-01T", "A22": "02-12-31-26T", "A23": "02-12-27-14-32-18-27", "A24": "06-18-17-19",
  "A25": "31-26-12", "A26": "02-12-13-01", "A27": "23-19-35T", "A28": "10-03-38",
  "A29": "02-12-27-27-35-37-21", "A30": "13-01", "A31": "10-03-38"},
 "B": {"B1": "02-12-22-40-07", "B2": "27-45-07-35", "B3": "02-37-23-05T", "B4": "22-25-27",
  "B5": "33-24-20-12", "B6": "16-23-18-43T", "B7": "13-01-39-33", "B8": "15-07-13-01-18",
  "B9": "22-37-42-25", "B10": "07-24-40-35", "B11": "02-26-36-40", "B12": "27-25-38-01",
  "B13": "29-24-24-20-35", "B14": "16-14-18", "B15": "29-33-01", "B16": "06-35-32-39-33",
  "B17": "02-09-27-01", "B18": "29-36-07-08T", "B19": "29-08-13", "B20": "29-45-07T",
  "B21": "22-29-36-07-08T", "B22": "27-34-23-25", "B23": "07-18-35", "B24": "07-45-07T",
  "B25": "07-23-18-24", "B26": "22-29-36-07-08T", "B27": "09-30-39-18-07", "B28": "02-06-35-23-07",
  "B29": "29-34-23-25", "B30": "45-07T"}}
UNCERTAIN = {"A20", "A21", "B12", "B28"}   # ergaenzt bzw. schwache Spuren -> Variante STRICT laesst sie weg


def parse(data):
    words = []
    for side in data.values():
        for wid, s in side.items():
            erased = "[ERASED]" in s
            s = s.replace("[ERASED]", "")
            dorn = s.endswith("T")
            s = s.rstrip("T")
            words.append(dict(id=wid, signs=[int(x) for x in s.split("-")], dorn=dorn, erased=erased))
    return words


def variants(words):
    return {"ALL": words, "STRICT": [w for w in words if w["id"] not in UNCERTAIN]}


FREQ_A = [6,14,2,1,0,2,3,1,0,4,1,15,3,1,0,0,1,6,3,0,2,0,5,1,2,5,10,2,3,0,5,2,2,1,5,0,2,3,1,3,2,0,0,1,2]
FREQ_B = [5,5,0,0,1,2,15,4,2,0,0,2,3,1,1,2,0,6,0,2,0,5,6,5,5,1,5,0,8,1,0,1,4,2,6,4,2,1,3,3,0,1,1,0,4]
# Quelle: Godart 1995 laut Wikipedia "Phaistos Disc" (Sign list and counts); A ohne das eine unleserliche Zeichen (A8)


def freq_ok(words):
    ca, cb = Counter(), Counter()
    for w in words:
        (ca if w["id"][0] == "A" else cb).update(w["signs"])
    return [ca[i] for i in range(1, 46)] == FREQ_A and [cb[i] for i in range(1, 46)] == FREQ_B


def integrity(words):
    A = [w for w in words if w["id"][0] == "A"]; B = [w for w in words if w["id"][0] == "B"]
    n = lambda ws: sum(len(w["signs"]) for w in ws)
    checks = {"Woerter A=31": len(A) == 31, "Woerter B=30": len(B) == 30,
              "Zeichen A=122": n(A) == 122, "Zeichen B=119": n(B) == 119, "Gesamt=241": n(words) == 241,
              "45 Typen": {s for w in words for s in w["signs"]} == set(range(1, 46)),
              "Dorne A=9 (A24 ohne: laut Godart Riss)": sum(w["dorn"] for w in A) == 9, "Dorne B=8": sum(w["dorn"] for w in B) == 8,
              "Zeichenhaeufigkeit je Seite = Godart-Tabelle": freq_ok(words),
              "1 Tilgung": sum(w["erased"] for w in words) == 1}
    return checks


def positions(words):
    tot, ini, fin = Counter(), Counter(), Counter()
    for w in words:
        s = w["signs"]; tot.update(s); ini[s[0]] += 1; fin[s[-1]] += 1
    return tot, ini, fin


def decode_signs(signs, table):
    if any(s not in table for s in signs):
        return None
    return "".join(table[s] for s in signs)


def score(words, table, lex):
    types = {tuple(w["signs"]) for w in words}
    dec = [d for d in (decode_signs(t, table) for t in types) if d is not None]
    return sum(d in lex for d in dec), len(dec), len(types)


def perm_test(words, table, lex, n=2000, seed=1):
    rng = random.Random(seed)
    obs = score(words, table, lex)[0]
    keys, vals = list(table), list(table.values())
    ge = 0
    for _ in range(n):
        rng.shuffle(vals)
        ge += score(words, dict(zip(keys, vals)), lex)[0] >= obs
    return obs, (ge + 1) / (n + 1)


def load_claim(path):
    c = json.load(open(path, encoding="utf-8"))
    if c.get("direction") not in ("inward", "outward"):
        raise ValueError(f"{path}: Feld 'direction' (inward/outward) fehlt - Deutung wird nicht getestet")
    for k in ("name", "source", "lexicon_source", "table", "lexicon"):
        if not c.get(k):
            raise ValueError(f"{path}: Feld '{k}' fehlt - Deutung wird nicht getestet")
    c["table"] = {int(k): v for k, v in c["table"].items()}
    c["lexicon"] = {w.lower() for w in c["lexicon"]}
    return c


SYL = [c + v for c in "ptkmnsrdlw" for v in "aeiou"][:45]


def rand_word(rng):
    return "".join(rng.choice(SYL) for _ in range(rng.randint(2, 4)))


def selftest(W, reps=200, n=200):
    types = sorted({tuple(w["signs"]) for w in W})
    rng = random.Random(7)
    T = dict(zip(range(1, 46), rng.sample(SYL, 45)))
    dec = [decode_signs(t, T) for t in types]
    lex = set(rng.sample(dec, len(dec) // 2)) | {rand_word(rng) for _ in range(300)}
    obs, p = perm_test(W, T, lex, n=1000)
    print(f"SENSITIVITAET (eingepflanzter Effekt, kuenstlich/zirkulaer): Treffer={obs}, p={p:.4f} -> {'OK' if p < 0.01 else 'FEHLER'}")
    pool, low = SYL[:10], 0
    for r in range(reps):
        r2 = random.Random(100 + r)
        T1 = {s: r2.choice(pool) for s in range(1, 46)}; T2 = {s: r2.choice(pool) for s in range(1, 46)}
        lex = {decode_signs(t, T2) for t in r2.sample(types, int(len(types) * 0.6))}
        low += perm_test(W, T1, lex, n=n, seed=r)[1] < 0.05
    rate = low / reps
    print(f"KALIBRIERUNG (Zufallstabelle, Zufallslexikon): p<0.05 in {rate:.1%} von {reps} Laeufen (Soll <= ca. 5%) -> {'OK' if rate <= 0.09 else 'FEHLER'}")
    return p < 0.01 and rate <= 0.09


def main(argv):
    words = parse(DATA)
    print("== INTEGRITAET ==")
    ch = integrity(words)
    for k, v in ch.items():
        print(f"  {'OK ' if v else 'FEHLER'} {k}")
    if not all(ch.values()):
        sys.exit("Datensatz inkonsistent - Abbruch")
    print("== POSITIONEN (nur beschreibend) ==")
    for vn, ws in variants(words).items():
        tot, ini, fin = positions(ws)
        only_i = sorted(s for s in tot if ini[s] == tot[s] and tot[s] >= 5)
        only_f = sorted(s for s in tot if fin[s] == tot[s] and tot[s] >= 5)
        print(f"  {vn}: nur wortinitial (n>=5): {only_i} | nur wortfinal (n>=5): {only_f}")
    cmd = argv[1] if len(argv) > 1 else "selftest"
    if cmd == "selftest":
        print("== SELBSTTEST ==")
        sys.exit(0 if selftest(words) else 1)
    if cmd == "run":
        claims = [load_claim(p) for p in argv[2:]]
        k = len(claims)
        print(f"== DEUTUNGEN (k={k}, Bonferroni) ==")
        for c in claims:
            for vn, ws in variants(words).items():
                if c["direction"] == "outward":
                    ws = [dict(w, signs=w["signs"][::-1]) for w in ws]
                obs, p = perm_test(ws, c["table"], c["lexicon"])
                _, cov, ntypes = score(ws, c["table"], c["lexicon"])
                pb = min(1.0, p * k)
                verdict = "nicht widerlegt" if pb < 0.01 else "nicht gestuetzt"
                print(f"  {c['name']} [{vn}] Treffer={obs} abgedeckt={cov}/{ntypes} p={p:.4f} p_bonf={pb:.4f} -> {verdict}")
            print(f"    Quelle: {c['source']} | Lexikon: {c['lexicon_source']}")


if __name__ == "__main__":
    main(sys.argv)
