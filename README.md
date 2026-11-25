# Phaistos-Diskus: quantitative Strukturanalyse (Datenstand v2)

Reproduzierbare statistische Untersuchung der Zeichenfolge auf dem Diskos von Phaistos (Kreta, Archäologisches Museum Iraklio). 241 lesbare Zeichen in 61 Wortfeldern, 45 Zeichentypen (Nummerierung 01–45 nach Evans/Godart).

**Dieses Repository enthält keine Entzifferung.** Es gibt keine Lautwerte, keine Übersetzung und keine Behauptung zur Sprache. Mit 241 Zeichen und ohne zweisprachigen Paralleltext ist eine Entzifferung mit Statistik allein nicht möglich. Untersucht wird nur die Struktur der Zeichenfolge.

## Regeln der Auswertung

- Jede Zahl stammt aus einem Skript in `scripts/`. Die Daten werden nur aus `scripts/phaistos_test.py` (Variable `DATA`) geladen, und jedes Skript prüft vorher die Integrität des Datensatzes.
- Nullmodelle erhalten Wortlängen und, wo nötig, die Position der Zeichen im Wort. Bei Permutationstests gilt p = (k + 1) / (N + 1), also p ≥ 1/(N + 1). Exakte Tests (Fisher, Binomial) können kleinere Werte liefern.
- Mehrfachtest-Korrektur nach Holm und Benjamini-Hochberg über alle durchgeführten Tests.
- Einstufungen: Strukturtests sind „nachgewiesen“ oder „nicht nachgewiesen“. Deutungen anderer sind „vereinbar“, „nicht vereinbar“ oder „nicht prüfbar“. Ein Nullergebnis heißt nie „bestätigt“, und „nicht prüfbar“ heißt nicht „widerlegt“.

## Kennzahlen (Datenstand v2)

| Kennzahl | ALL | STRICT (ohne A20, A21, B12, B28) | NO_A8 (ohne A8) |
| :--- | :--- | :--- | :--- |
| Wortfelder | 61 (A 31, B 30) | 57 (A 29, B 28) | 60 (A 30, B 30) |
| Lesbare Zeichen | 241 (A 122, B 119) | 224 (A 114, B 110) | 237 (A 118, B 119) |
| Zeichen 02 | 19 (A 14, B 5), alle am Wortanfang | 17 (A 13, B 4) | 18 (A 13, B 5) |
| Bigramm 02-12 | 13 (A 12, B 1) | 13 (A 12, B 1) | 12 (A 11, B 1) |
| Dorne (Schrägstrich am Wortende) | 17 (A 9, B 8) | 16 (A 8, B 8) | 17 (A 9, B 8) |

Das getilgte Zeichen in A8 zählt nicht. A24 trägt laut Godart nur einen Riss und keinen Dorn. STRICT lässt Felder weg, die ergänzt oder unsicher gelesen sind.

## Nachgewiesene Strukturbefunde

- **Die Zeichenfolge ist nicht zufällig geordnet.** Bedingte Entropie H(Xₙ | Xₙ₋₁) = 1,630 Bit gegen 2,346 ± 0,061 Bit (Zeichen global gemischt) und 2,217 ± 0,068 Bit (Zeichen innerhalb der Wörter gemischt), jeweils p ≤ 1/(N + 1). In STRICT 1,576 Bit gegen 2,254 und 2,120 Bit.
- **Zeichen 02 steht immer am Wortanfang**, in 19 von 19 Fällen (Seite A 14/14, Seite B 5/5).
- **02 und 12 bilden ein festes Paar**: 13 Vorkommen, Odds Ratio 85,0, Fisher exakt p = 2,6 · 10⁻¹². Fast nur auf Seite A (12 von 13).
- **Seite A und Seite B unterscheiden sich** in der Zeichenverteilung (Jensen-Shannon-Divergenz, Wörter zwischen den Seiten vertauscht, p = 0,0004). Bei Dornen und Wortlängen gibt es keinen Unterschied.
- **Mehr wiederholte Zeichenfolgen als bei Zufall**: 27 maximale Wiederholungen gegen 17,0 ± 2,9 (ALL, p ≈ 0,002), in STRICT 23 gegen 14,7 (p < 0,01; der genaue Wert schwankt je nach Zufallsstart zwischen etwa 0,001 und 0,005).
- **Größenordnungen**: Zeichenvorrat mindestens etwa 49 bis 51 (Chao1). Wortschatz unter einem Zipf-Modell etwa 450 Wörter (90-%-Intervall etwa 180 bis 2500, abhängig von den Modellannahmen). Ein kleiner, geschlossener Wortschatz unter 100 Wörtern passt nicht zu den Daten.

Über 19 Tests bleiben nach Holm 6 Befunde, nach Benjamini-Hochberg 11. Die Korrektur in `phaistos_phase3.py` rechnet mit den dokumentierten p-Werten der Einzeltests; die Kennzahlen dieses Abschnitts erzeugt `phaistos_master_status.py`, `phaistos_audit_v3.py` (Seitenunterschied) und `phaistos_inventory.py` (Größenordnungen). Diese Befunde beschreiben Struktur, nicht Bedeutung.

## Zurückgezogen oder nicht nachgewiesen

Diese Hypothesen sind im Lauf des Projekts entstanden und haben die Prüfung nicht bestanden:

- Strophen-Kadenz mit [28-01] nach langen Wörtern (hängt an den ergänzten Feldern A20/A21, ohne sie p = 0,14)
- Offene Silbenschrift aus Konsonant und Vokal, abgeleitet aus Doppelzeichen (p = 0,21)
- Grammatik als verstecktes Markov-Modell mit 4 Zuständen (auf ungesehenen Daten schlechter als einfache Modelle)
- Ring-Komposition auf Seite B (nur ein gleiches Wortpaar, B21 und B26)
- Fünf Vokalklassen (Zeichengruppen gibt es, eine Deutung als Vokale ist unbelegt)
- Ergänzende Verteilung der Zeichenpaare 02/01, 29/31 und 24/25 (mit Positionskontrolle p = 0,34, 0,35, 0,13)

## Deutungen anderer

- **Massey & Massey (1998)**, Schrägstrich-Wörter als Zahlwörter: unter vorab festgelegten Regeln **nicht gestützt**. Die Wörter ohne Schrägstrich passen genauso oft zur Zahlwortliste (siehe `docs/MASSEY_TEST.md`).
- **Hempl, Faucounau, Achterberg et al., Owens/Coleman**: **nicht prüfbar**, weil keine vollständige Zeichentabelle mit unabhängigem Lexikon frei vorliegt. Das ist keine Aussage darüber, ob die Deutungen richtig oder falsch sind.
- Vergleiche mit der Axt von Arkalochori und dem Altarstein von Malia: nicht prüfbar, weil Quelle und Code fehlen.

## Ausführen

```bash
pip install -r requirements.txt
python3 scripts/phaistos_test.py selftest
python3 scripts/phaistos_master_status.py
python3 scripts/phaistos_phase2.py
python3 scripts/phaistos_inventory.py
python3 scripts/phaistos_audit_v3.py
python3 scripts/phaistos_phase3.py
python3 scripts/phaistos_massey_test.py
```

`phaistos_phase3.py` läuft einige Minuten (Trennschärfe-Simulation).

| Skript | Inhalt |
| :--- | :--- |
| `phaistos_test.py` | Datensatz v2, Integritätsprüfung, Selbsttest, Prüfrahmen für Deutungen (`run claims/*.json`) |
| `phaistos_master_status.py` | Kennzahlen je Variante |
| `phaistos_phase2.py` | Präfix-/Suffix-Test, Wurzelformen, Kontext-Ähnlichkeit; prüft außerdem einen fehlerhaften KI-Datenblock |
| `phaistos_inventory.py` | Zeichenvorrat (Chao1) und Wortschatz (ABC unter Zipf) |
| `phaistos_audit_v3.py` | Gegenprüfung von Kadenz, Doppelzeichen, Seitenunterschied, Zeichengruppen, HMM, Ring-Komposition |
| `phaistos_phase3.py` | Mehrfachtest-Korrektur, Trennschärfe, Silhouette, Nebentests |
| `phaistos_massey_test.py` | Test des Zahlwort-Anspruchs von Massey & Massey |

## Daten, Quellen und Grenzen

- Transkription und Häufigkeitstabelle je Seite stammen aus dem englischen Wikipedia-Artikel „Phaistos Disc“ (Godart-Nummerierung). Die Wortformen wurden mit Duhoux (2000) abgeglichen. Gegen die Scheibe selbst wurde nicht geprüft.
- Y. Duhoux (2000): How Not to Decipher the Phaistos Disc. *American Journal of Archaeology* 104(3), 597–600.
- K. Massey & K. Massey (1998): The Phaistos Disk. Wird nur zitiert, nicht mitgeliefert.
- M. Braović, D. Krstinić, M. Štula, A. Ivanda (2024): A Systematic Review of Computational Approaches to Deciphering Bronze Age Aegean and Cypriot Scripts. *Computational Linguistics* 50(2), 725–779. doi:10.1162/coli_a_00514

Die Daten sind klein (241 Zeichen). Auch die nachgewiesenen Befunde sind Strukturbeschreibungen. Sie belegen keine Sprache, keine Lautwerte und keine Gattung.

## Entstehung

Projektleitung: Fatih Özhan. Die Auswertung entstand mit Hilfe von KI-Modellen (Claude, Gemini, ChatGPT), die sich gegenseitig geprüft haben. Dabei wurden mehrere Fehler gefunden und korrigiert, unter anderem drei falsch übernommene Wortfelder (B28–B30) und fehlende Dorne (B20, B24, B30). Alle Zahlen in diesem README wurden aus den Skripten neu erzeugt.

## Lizenz

Code: MIT (siehe `LICENSE`). Die Transkription in `DATA` stammt aus Wikipedia und steht unter CC BY-SA 4.0 (siehe `DATA_LICENSE.md`).
