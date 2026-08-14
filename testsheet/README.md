# Sudoku-testark

Ni oppgaver med stigende vanskegrad, én per teknikk-trinn. Skriv ut
`sudoku-testark.pdf` (side 1) og sett kryss i 1–5 under hver oppgave.
Side 2 er kjennetegnene, side 3 er fasit.

| Nr | SE | Nivå | Tall | Nøkkelteknikk | Steg | Krux | Plass | Valg |
| --: | --: | :-- | --: | :-- | --: | --: | --: | --: |
| 1 | 2,3 | VANSKELIG | 24 | Nakent enkelttall | 57 | 1 | 12 % | 3,3 |
| 2 | 2,6 | VANSKELIG | 24 | Pekende par | 58 | 1 | 43 % | 2,0 |
| 3 | 2,8 | VANSKELIG | 24 | Blokkrav | 60 | 1 | 48 % | 2,2 |
| 4 | 3,0 | VANSKELIG | 24 | Nakent par | 68 | 1 | 21 % | 2,6 |
| 5 | 3,2 | VANSKELIG | 26 | X-Wing | 60 | 1 | 33 % | 3,0 |
| 6 | 3,4 | VANSKELIG | 28 | Skjult par | 54 | 1 | 52 % | 2,4 |
| 7 | 3,6 | VANSKELIG | 30 | Nakent trippel | 58 | 1 | 40 % | 4,7 |
| 8 | 4,2 | EKSPERT | 23 | XY-Wing | 62 | 1 | 44 % | 2,2 |
| 9 | 4,5 | EKSPERT | 24 | Unikt rektangel | 60 | 1 | 58 % | 2,4 |

- **SE** — vanskegraden til det vanskeligste steget oppgaven krever.
- **Nøkkelteknikk** — hvilket steg det er. Hver oppgave på arket har sitt eget.
- **Krux** — hvor mange ganger den teknikken må brukes.
- **Plass** — hvor langt ut i løsningen kruxet dukker opp første gang.
- **Valg** — hvor mange steg som i snitt er mulige samtidig; lavt tall = smalere sti.

Rekkefølgen følger teknikken, ikke følelsen: en oppgave lenger ned på
arket kan ha flere oppgitte tall og dermed kjennes lettere enn den over.
Det er nettopp det ratingen skal fange opp.

## Oppgavene

### 1. Nakent enkelttall (SE 2,3)

En rute der åtte tall er utelukket, så bare ett blir igjen.

- Nivå: VANSKELIG · 24 oppgitte tall
- Teknikker i løsningen: skjult enkelttall (boks), skjult enkelttall (linje), nakent enkelttall
- Løsningssti: 57 steg, kruxet 1 gang fra 12 % ut i stien
- Valgt blant 12 kandidater med denne nøkkelteknikken
- Oppgave: `.6...7......2.89...24.....5......58.37.....96.92......7.....62...39.4......5...3.`
- Fasit: `968157342537248961124396875641729583375481296892635417759813624213964758486572139`

### 2. Pekende par (SE 2,6)

Et tall som i en boks bare kan stå i én rad/kolonne, og strykes videre ut.

- Nivå: VANSKELIG · 24 oppgitte tall
- Teknikker i løsningen: skjult enkelttall (boks), skjult enkelttall (linje), nakent enkelttall, pekende par
- Løsningssti: 58 steg, kruxet 1 gang fra 43 % ut i stien
- Valgt blant 125 kandidater med denne nøkkelteknikken
- Oppgave: `35...9.....9.....1..8.7....13....5..2..7.6..4..4....79....6.9..8.....2.....1...37`
- Fasit: `356819742729643851418275693137984526295736184684521379573462918841397265962158437`

### 3. Blokkrav (SE 2,8)

Et tall som i en rad/kolonne bare kan stå i én boks, og strykes ut av resten av boksen.

- Nivå: VANSKELIG · 24 oppgitte tall
- Teknikker i løsningen: blokkrav, skjult enkelttall (boks), skjult enkelttall (linje), nakent enkelttall, pekende par
- Løsningssti: 60 steg, kruxet 1 gang fra 48 % ut i stien
- Valgt blant 27 kandidater med denne nøkkelteknikken
- Oppgave: `.....5.......7.3844....8.6..8...9.3....7.4....9.2...4..5.6....2263.5.......9.....`
- Fasit: `638495127925176384471328965784569231312784596596231748159643872263857419847912653`

### 4. Nakent par (SE 3,0)

To ruter i samme enhet med samme to tall — begge tallene strykes hos naboene.

- Nivå: VANSKELIG · 24 oppgitte tall
- Teknikker i løsningen: blokkrav, skjult enkelttall (boks), skjult enkelttall (linje), nakent par, nakent enkelttall, pekende par
- Løsningssti: 68 steg, kruxet 1 gang fra 21 % ut i stien
- Valgt blant 44 kandidater med denne nøkkelteknikken
- Oppgave: `.37.4.....2.1..7......7.8.6.....8..9.1.....2.9..6.....5.4.3......9..7.3.....8.29.`
- Fasit: `637845912428169753195273846742358169816794325953621487584932671269417538371586294`

### 5. X-Wing (SE 3,2)

Et tall låst i to rader på de samme to kolonnene (eller omvendt).

- Nivå: VANSKELIG · 26 oppgitte tall
- Teknikker i løsningen: skjult enkelttall (boks), skjult enkelttall (linje), nakent enkelttall, pekende par, X-Wing
- Løsningssti: 60 steg, kruxet 1 gang fra 33 % ut i stien
- Valgt blant 3 kandidater med denne nøkkelteknikken
- Oppgave: `...7.9.412.....7..7.....95..5..4...8...6.7...1...8..6..72.....3..9.....481.3.6...`
- Fasit: `685729341291534786743861952956143278428657139137982465572418693369275814814396527`

### 6. Skjult par (SE 3,4)

To tall som bare får plass i de samme to rutene — alt annet i de rutene ryker.

- Nivå: VANSKELIG · 28 oppgitte tall
- Teknikker i løsningen: skjult par, skjult enkelttall (boks), skjult enkelttall (linje)
- Løsningssti: 54 steg, kruxet 1 gang fra 52 % ut i stien
- Valgt blant 3 kandidater med denne nøkkelteknikken
- Oppgave: `3..9...5..48.7......1..52.8..4.87...6.......4...64.3..1.28..6......1.82..8...6..3`
- Fasit: `327968451548172936961435278294387165613259784875641392152893647736514829489726513`

### 7. Nakent trippel (SE 3,6)

Tre ruter som til sammen bare rommer tre tall.

- Nivå: VANSKELIG · 30 oppgitte tall
- Teknikker i løsningen: blokkrav, skjult enkelttall (boks), skjult enkelttall (linje), nakent trippel, pekende par
- Løsningssti: 58 steg, kruxet 1 gang fra 40 % ut i stien
- Valgt blant 1 kandidat med denne nøkkelteknikken
- Oppgave: `...28.5..4.8..9..15......9..26..38.41.......38.39..62..8......26..1..3.9..9.68...`
- Fasit: `791284536468539271532617498926753814174826953853941627387495162645172389219368745`

### 8. XY-Wing (SE 4,2)

Tre toerruter i kjede: XY–XZ–YZ, som stryker Z der de to endene ser samme rute.

- Nivå: EKSPERT · 23 oppgitte tall
- Teknikker i løsningen: skjult enkelttall (boks), skjult enkelttall (linje), nakent par, nakent enkelttall, pekende par, XY-Wing
- Løsningssti: 62 steg, kruxet 1 gang fra 44 % ut i stien
- Valgt blant 84 kandidater med denne nøkkelteknikken
- Oppgave: `.....1....6..87..5...2....71......985...7...427......63....2...9..54..2....9.....`
- Fasit: `753691842462387915819254367136425798598176234274839156341762589987543621625918473`

### 9. Unikt rektangel (SE 4,5)

Et mønster som måtte gitt to løsninger — og derfor ikke kan stå.

- Nivå: EKSPERT · 24 oppgitte tall
- Teknikker i løsningen: blokkrav, skjult enkelttall (boks), skjult enkelttall (linje), pekende par, unikt rektangel
- Løsningssti: 60 steg, kruxet 1 gang fra 58 % ut i stien
- Valgt blant 17 kandidater med denne nøkkelteknikken
- Oppgave: `........8....3.52..2.4.6.7.....4...735.....869...8.....8.2.1.3..74.9....5........`
- Fasit: `713529648496837521825416973268145397351972486947683152689251734174398265532764819`

## Slik ble settet plukket

Generatoren laget 316 puslespill (seed 20260814). Fordelt på vanskeligste teknikk: pekende par 125, XY-Wing 84, nakent par 44, blokkrav 27, unikt rektangel 17, nakent enkelttall 12, X-Wing 3, skjult par 3, nakent trippel 1.
For hvert trinn er kandidaten med færrest oppgitte tall valgt.

Swordfish (SE 3,8) står ikke på arket. Løseren tar alltid det billigste steget først, og et rutenett som er åpent nok til å by på en swordfish har nesten alltid et nakent trippel eller en enklere teknikk å ta i stedet — den var vanskeligste steg i 0 av 316 genererte puslespill.

Regenerer med `sudokugen testsheet -o testsheet`.
