# Massey-Test: Sind die Schrägstrich-Wörter Zahlwörter?

Skript: `scripts/phaistos_massey_test.py`, Datenstand v2.

## Frage

K. & K. Massey (1998) deuten die Wörter mit einem Schrägstrich (Dorn) am Wortende als Zahlwörter einer indoeuropäischen Sprache. Der Test fragt nur: Passen die Schrägstrich-Wörter mit Masseys eigenen Zeichenwerten besser zu einer Zahlwortliste als die übrigen Wörter?

## Vorab festgelegte Regeln

- Leserichtung nach Massey (von innen nach außen), also jedes Wort umgekehrt.
- Zeichenwerte aus Masseys Tabelle der 17 Schrägstrich-Wörter (S. 63 seines Textes). Daraus ergeben sich 17 widerspruchsfreie Zeichenwerte. Alle anderen Zeichen gelten als unbekannt.
- Zahlwortliste: die bei Massey abgedruckte Liste von Vidal (S. 64, 13 Muster). Optionale Buchstaben dürfen fehlen, eine Endung K-Y darf abgezogen werden.
- Geprüft werden nur Wörter mit höchstens einem unbekannten Zeichen.
- R1 (streng): Das Konsonantengerüst entspricht genau einem Muster. R2 (locker): eine Abweichung ist erlaubt.

## Ergebnis

| Regel | Treffer mit Schrägstrich | Treffer ohne Schrägstrich | Fisher exakt |
| :--- | :--- | :--- | :--- |
| R1 (streng) | 5 von 16 | 3 von 14 | p = 0,69 |
| R2 (locker) | 11 von 16 | 9 von 14 | p = 1,00 |

Masseys 17 Schrägstrich-Wörter sind genau die 17 Wörter mit Dorn im Datensatz v2.

## Einordnung

- Die Wörter ohne Schrägstrich passen genauso oft zu einem Zahlwort. Der Schrägstrich trennt Zahlwörter nicht von anderen Wörtern. Der Anspruch ist in dieser Form nicht gestützt.
- Bei lockeren Regeln passt fast jedes kurze Wort zu irgendeinem Zahlwort (R2: 64 % der Wörter ohne Dorn). Treffer bedeuten dann wenig.
- Vertauscht man die 17 Zeichenwerte zufällig, gibt es weniger Treffer bei den Schrägstrich-Wörtern (p = 0,001 bei R1, p = 0,005 bei R2). Das hat kaum Gewicht, weil die Werte an genau diesen Wörtern abgeleitet wurden. Aussagekräftig ist der Vergleich mit den übrigen Wörtern.

## Grenzen

- Nur 30 von 61 Wörtern sind prüfbar, weil Massey nur für wenige Zeichen Werte nennt.
- Die Zeichenwerte sind aus seiner Tabelle abgeleitet, keine von ihm veröffentlichte Gesamttabelle.
- Getestet wird eine Umsetzung des Anspruchs in Regeln. Eine andere Umsetzung könnte anders ausfallen.
- Das ist keine Widerlegung von Masseys Gesamtdeutung, sondern ein Befund: unter diesen Regeln nicht gestützt.
