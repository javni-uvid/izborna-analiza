# OCR: decisions on polling boards and observers' records

Decisions about reading RIK's documents by OCR (decisions on polling boards, observers' records), moved word for
word from AGENTS.md on 20 Nov 2026 (the maintainer's decision, so that an agent reads the rules and only the
decisions of the part it works on: AGENTS.md had grown to 97 KB). **Keep it current:** a decision made or changed is
added here, at the end of the section it belongs to, in the same commit as the change. The principles and the rules
of work are in AGENTS.md.

## OCR

- **Engine:** Tesseract with `srp+srp_latn` on GitHub's runners. In the development sandbox the Serbian data can't
  be downloaded; use `rus` for local checks and confirm on a runner.
- **Decisions on polling boards** use the PDF's text layer when there is one, otherwise OCR. Each list's slot gives
  "member yes/no", and the address is cleaned before it is kept.
  - The workflow reads in four jobs at once (about 1,600 decisions an hour each): `--plan` lists what to read,
    `--read --shard I/4` reads one share, `--merge` keeps everything and commits once. The plan and the parts are
    workflow artifacts, so they hold no names either.
  - A reading's version (`boards.PARSER`) is kept with every decision read (`v`). Raise it when `parse_decision`
    reads more than before: `plan()` then lists every decision read by an older version (by its kept link, since
    the register is paged only for new decisions once read whole), and the daily run reads them again, about
    1,600 an hour per job. Don't reread by hand per municipality for a parser fix; raise the version.
  - Layouts: the numbered parser ("1. члан:", "1) члан:") goes first, so nothing that read before changes; the
    unnumbered one (`_unnumbered`) takes over only where it finds no slot. A new layout comes from the masked
    layouts the read jobs log (`--diagnose`, or `--diagnose-ids` for decisions already read), never from a
    decision's text with names.
  - Tables with a row per member and per deputy, each with its own proposal (Ub, 2026): a page OCR read column by
    column (`read_columns`) is read again line by line (psm 6), and each numbered slot's list is the one its text
    names most (`named_most`), its own number first. Only decisions in that layout take this path.
  - Kinds: RIK's label, which the commission picks when it uploads, decides; only at a station with no standing
    decision and two extended ones does the title naming the standing composition, or the president, make one of
    them standing (`standing_under_extended`). A title alone never overrules a label: on 6 Nov 2026 a title-first
    rule turned 29 of Ada's extended decisions into standing ones (both of a station's titles name the standing
    composition) and was taken back the same night. A re-index gives decisions already read the current kind.
  - Placement (`Placer`): by municipality and number, and where the register's station name disagrees with the
    results, by that name among the city municipalities of the same district, or among municipalities whose name
    in any election, or district, contains the register's; "РИК" (RIK's own boards) among the stations abroad and
    in prisons. Nothing placed under its own name moves (checked on every archived election).
- **Observers' records (RG-11)** are read by a person. OCR only orders the review list:
  - The score is the ink and words between "… су следеће:" and "(примедбе уписује …)". Each column of a landscape
    page is read on its own, and printed rules are left out by the length of their dark runs.
  - A person writes what they found in `observer_reviews.csv`, through `izbori observers --review` and `--merge`.
    Only a confirmed "yes" becomes a flag.

## Decisions log

- **5 Nov 2026, later:** Kosovo and Metohija are on the map in RIK's division, from Glaurdić et al. (2021, CC BY
  4.0), the 1999 layer, joined by name (either of the dataset's two names; Gora is the municipality seated in
  Dragaš). RGZ's register would have needed an account, and OpenStreetMap follows Kosovo's division since 2000.
  The map's classes hold equal numbers of municipalities, as the province's turnout squeezed equal steps.
  The maintainer asked why so many board decisions were missing (750 of 8,392 stations in 2026): unreadable
  layouts (371), decisions listed under a city or a name the results don't use (319: Niš, abroad, prisons), 17
  of Kostolac and Sevojno added to Požarevac and Užice by number (a bug), and 43 never published. The parser
  learnt three layouts and decisions are placed by the station's name; `--reindex` applies it to what was read.
  After the re-index, 8,345 of 2026's 8,392 stations have their controllers known (7,642 before); of the 47 left,
  43 have no decision in RIK's register (37 in Kosovo and Metohija) and 4 are unreadable. The 2023 elections were
  re-indexed and re-read too: parliamentary 8,120 of 8,273 (7,269 before), provincial 1,771 of 1,776 (1,621).
- **6 Nov 2026, Ub's decisions:** the maintainer found Ub's station 2 (2026) showing controllers of lists 1, 7 and
  15, while the decision names the student list, and its standing composition counted as the extended one. Both
  came from the register and the scans: the commission uploaded its standing compositions under the extended
  composition's label (now recognised station by station, by the title naming the president), and its extended
  compositions are scanned tables that OCR read half by columns (now read line by line, row by row). The decisions
  of Ub and eight municipalities with similar readings (Vranje, Zrenjanin, Bajina Bašta, Petrovac na Mlavi,
  Kragujevac, Senta, Srbobran, Blace) were read again: 179 stations' controllers changed, Ub's station 2 to the
  eleven lists its decision names and Vranje's 83 stations to fuller lists. The masked layouts are in boards runs
  42125804884 and 42127173840.
- **8 Nov 2026, a misread "на" dropped controllers.** Mali Iđoš, station 1: the Student list's member and deputy
  are in the decision, the station showed none. OCR had read "на предлог" as "ха предлог" in three of six slots and
  the parser kept only slots with "на предлог", so those lists vanished without a trace (not "unparsed", just
  fewer slots). A proposal is now "предлог" with any short word before it, and decisions carry the reading's
  version so a parser fix rereads what the old reading read (8,700 decisions this time, one daily run). The
  symptom to watch for: a municipality whose decisions read far fewer slots than its stations have lists.
  The reread (8,701 decisions, one run) found 470 controllers more in 281 decisions and lost none. The second
  pattern from the same municipality (station 16): OCR garbled the word "члан" in one slot's heading, the slot
  ran into the one before it, and the merged text named two lists; a slot now starts at any "N. <short word>:"
  (reading version 3, read again). Each new example Marko sends is worth a diagnosis before a guess.
  Marko then checked nine suspect decisions by hand: two kinds of suspect. Decisions that add up (a supplement
  or a mislabelled standing decision beside the real one) only looked thin per document — `coverage` unions them,
  nothing was lost. The real losses were three layouts (Žabalj, Zrenjanin, Novi Sad). So the daily merge now logs
  `odd_stations`: stations lacking a list that 90% of their municipality's stations have, computed on the union,
  the honest version of the per-document statistic.
  Reading version 3 was a regression: its looser slot pattern also passed the sanity check that picks a PDF's
  text layer over OCR, so bad text layers (whole commissions: Čoka, Trstenik, Žitorađa…) were taken for the
  decision and 4,700 slots vanished for an hour. Version 4: the strict pattern decides the text layer, the loose
  one applies only inside a decision that has proper slots. Lesson: a pattern used as a sanity check must not be
  the one you loosen. Version 4 also reads again (line by line, or OCR instead of the text layer) whenever a
  decision names more members than slots were found, takes "подносиоца" as a proposal's mark, a slot whose number
  OCR turned into letters, and a deputy's role without its colon.
