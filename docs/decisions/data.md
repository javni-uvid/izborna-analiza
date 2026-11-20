# The archive, RIK and the census

Decisions about the archive, fetching from RIK, the census, settlements and places, moved word for word from
AGENTS.md on 20 Nov 2026 (the maintainer's decision, so that an agent reads the rules and only the decisions of the
part it works on: AGENTS.md had grown to 97 KB). **Keep it current:** a decision made or changed is added here, at
the end of the section it belongs to, in the same commit as the change. The principles and the rules of work are in
AGENTS.md.

## Archive and data

- **Git is the archive.** `data/rounds/<id>/` holds RIK's files as downloaded and the derived stores; the history is
  a timestamped record of what RIK published. A file is committed only when its content changed.
- **The derived stores are written one entry per line** (`jsonfile.py`), so git keeps a small diff.
- **Each derived store keeps only what a page needs.** None of them holds a name:
  - `boards.json`: per decision, the station, kind, link, address, and whether each list appointed a member.
  - `documents.json`: label, link and upload time of every station document in RIK's register of minutes.
  - `commission.json`: link, RIK's kind and the day, for the municipal commissions' documents; for a document RIK
    lists under a city the results don't have (Niš, Belgrade), RIK's name of that city.
  - `observers.json`: the OCR numbers only.
  - `observer_reviews.csv`: what a person found in an observers' record.
  - `settlements.json`: per station, its census municipality and settlement and the rule that found them (each
    election's Settlements page and Explore's census measures use it).
- **Stations are keyed `municipality code/number` per round.** Municipality codes are stable across elections,
  but names differ ("Ниш-Медијана" in 2022, "Градска општина Медијана" in RIK's registers). Names map to codes
  with `boards.municipality_key`, using every archived round.
- **The 2022 census** (`data/census/2022/`) is kept as the Statistical Office (RZS) published it, by settlement
  and by municipality, with `sources.json` (address, SHA-256, size, first fetched); a table is written only when
  its content changed. Which tables: `census.TABLES`. The census is final, so the **census** workflow runs by
  hand; the development sandbox can't reach the Office's site (its proxy refuses it), GitHub's runners can. The
  tables count people and hold no names. Education, ethnicity, activity and migration exist only by municipality.
- **Each station's settlement** (`settlements.py`): the first rule that answers decides, the same for every
  station: a correction in `data/settlements.csv`, a settlement named in the decision's address (after its first
  part: "address"; in it: "building"), in the station's name, the municipality's only settlement, the same place
  in another election ("place", by `places.py`), and last the seat, assumed only for an address with a street or a
  house number that names no settlement. No rule, no entry: unknown is not zero. The census prints names, not codes:
  its units come from the first column's indentation, and RIK's municipalities match them by name (brackets say
  which city; a city municipality RIK doesn't list in a round belongs to the city's own). The **boards** workflow
  joins again after reading decisions, since they give the addresses.
- **Places across elections** (`places.py`) are matched going forward in time, by priority: manual correction
  (`data/places.csv`), then address, then name, then number. A new election never changes how the earlier ones
  were joined. An address read from a decision that names another building than the station's own name in the
  results is not used, for matching or for display (3 Nov 2026). Such addresses come from decisions filed under the
  wrong station, or from a line that is only the town's name.

## Fetching from RIK

- **Endpoints:**
  - `/get-elections/`: the rounds.
  - `/get_results/`: progress and totals.
  - `/export-results/{round}/2`: the results file.
  - `/get-election`: the register of minutes, ten stations a page.
  - `/get-additional-documents`: decisions on polling boards (type 4) and the municipal commissions' documents
    (type 1).
- **The election calendar sets how often RIK is asked** (`schedule.py`). Election days come from the archive and
  from `data/elections.csv`, which a maintainer fills in when an election is called. The cadence:
  - with no election under way, once a day;
  - on election day, every 6 hours, then every hour from two hours before the polls close;
  - every hour for two days after;
  - every 3 hours until 14 days after.

  How the schedule is kept reliable:
  - `data/looks.json` records the last look, because GitHub drops many scheduled runs (3 of about 22 hourly runs
    on 3 Nov 2026).
  - While a count is open, the watch loop starts the next run itself.
  - Sunday evenings get extra cron runs.
- **Registers are read incrementally:**
  - The register of minutes is re-read only when a cheap count per document kind changed.
  - The register of additional documents is read newest first, stopping at the first page with nothing new.
  - A full pass happens only when a store lacks something, for example the decisions' links, or the cities' names
    in the commissions' store (`commission.needs_reading`).
- **Time windows after election day:**
  - The register of minutes: daily for 14 days, then on Mondays until 60 days.
  - Board decisions: until 14 days, since they are appointed before election day.
  - Observers' records: OCR until 60 days.
  - The commissions' documents: once for every archived round, then with the register of minutes.

## Decisions log

- **6 Nov 2026, census tables:** for a study of controllers by list (outside the site, every list measured alike),
  the maintainer chose to archive the 2022 census, so that polling stations can be joined to their settlements and
  compared with like places. The Office publishes seven tables by settlement (population, age and sex, households,
  families, every census from 1948, dwellings); education, ethnicity, economic activity and migration only by
  municipality, education also by type of settlement. `izbori census` keeps those seven and eight by
  municipality, as published; joining stations to settlements comes next.
- **6 Nov 2026, stations' settlements:** the maintainer chose to keep the join in the repo: a store per round that
  records the rule behind each station's settlement, and corrections by hand in `data/settlements.csv`, as
  `data/places.csv` does for places. The seat is assumed only where a decision gives a street address naming no
  place: falling back to it for every station put all 91 of Prokuplje's stations, from 107 settlements, in the
  town. The same place in another election comes before the seat, and fills the 2022 round, whose results name
  no station. In 2026, 7,556 of the 8,210 stations where the census was held have a settlement (6,520 named or
  certain, 607 from another election, 429 assumed seats); 654 have none, mostly where decisions give no address
  (Prokuplje, Knjaževac, Negotin, Bajina Bašta). openpyxl joins the dependencies, to read the census.
- **8 Nov 2026, "(naselje nije utvrđeno)".** Marko asked which six Novi Sad stations had no settlement and why.
  Two had an address whose building OCR mangled a little ("ЂУРАДАНИЧИЋ", "ІІСВЕТИ CABAіІ"), so the building rule
  (`places.contradicts`) set the whole address aside, town included; it now tolerates a lost space or a letter or
  two. The other four had no usable address line at all (no address, no town in it, or the building and the town
  run together) and got rows in `data/settlements.csv` with the reason. The map's settlements are clickable: a
  settlement's stations list under the map, from the page's own JSON.
- **8 Nov 2026, the 700 stations without a settlement.** 442 of them had an address from the board decision that
  names only the building (Senta, Negotin, Bajina Bašta, Valjevo …), 173 none at all (Prokuplje, Knjaževac). Guessing
  "no street means the town" was rejected: the same commissions write bare names for village stations too. RIK's
  station lookup (biracka-mesta/) has no addresses either. The primary source is the local commission's decision
  on polling stations (law, art. 56–57: number, name, address, area), published on the web — a handful are in
  RIK's register of commission documents (Negotin, Ljubovija, Pirot), the rest on the municipalities' own sites.
  `data/station_lists.csv` collects the links Marko or I find, `stationlist.py` reads them (rule "list", before the
  address rule, passed on to other elections), the **stations** workflow runs it. An act of 2023 serves 2026
  through the places. Rows must look like the station (a shared word in the name) so a renumbering can't move a
  station to another's settlement.
  9 Nov: the first reads put whole villages one station off (Barajevo, Varvarin, Dimitrovgrad, Odžaci): a table
  cell of several lines puts the start of a row's address above its number in the extracted text. Now both
  alignments are read and the one agreeing with more of the board decisions' explicit addresses is kept; an act
  agreeing with under 60% of at least four is set aside whole, and an explicit address beats the act's row.
- **9 Nov 2026, Novi Sad by its quarters.** Marko wants the city of Novi Sad drawn by its quarters (Telep, Novo
  naselje…), not as one settlement. First a probe (`izbori geo --quarters-inspect`) of what OpenStreetMap has
  inside the settlement. It has 24 quarters with boundaries (Telep, Liman 1–4, Detelinara, Grbavica; Novo naselje as
  Bistrica) and 31 local communities (admin_level 10, finer). Marko left the choice to me: quarters, the names he
  used. `--quarters` keeps them in data/geo/quarters.json with public buildings' names → quarter, to place each
  station by its building's name where the city's act gives no address.
  First fetch: 25 quarters; 141 of the 153 stations in the settlement placed by building (schools, kindergartens,
  local communities' halls); the rest (a utility company, pensioners' clubs) stay "Novi Sad". Quarters are taken
  smallest first, so Sajlovo isn't swallowed by the industrial zone around it. Bistrica is shown as Novo naselje.
  Same day, Marko: keep the municipality's map as it was and open the urban city, larger, on a click on Novi Sad.
  So the quarters no longer replace the settlement: `Site.quarter_zoom` draws a second map (own hatch pattern ids,
  "zh1…", so it paints while the first steps aside; the first is hidden by visibility, not display, for the same
  reason), the page data carries `q` (station number → quarter) for its panel and its PNG.
  Same day, Marko: make similar shades easier to tell apart. Five steps instead of four (60–70% and 70%+ apart, as
  most of Novi Sad's quarters sat in one step), opacities evenly spaced, and the top step darkened
  (brightness 0.72, `mp-deep`; mun.js darkens the same in the PNG) since opacity alone can't go past full.
  Same day, Marko: two names and two places instead of the in-page zoom — "Opština Novi Sad" (the whole, Novi Sad one
  settlement) and "Grad Novi Sad" (the urban city by quarters) in the search, the labels and the references; a click
  on Novi Sad on the Opština page goes to Grad. Grad is `municipality_context(part=True)` at /novi-sad/grad/: the
  same page over the city's stations, quarters as its settlements, no similar-municipality ranks, no history strip.
  RIK's name "Град Нови Сад" is shown as "Општина Нови Сад" (`display_names`, `mname` in station/check/repeat/
  changes); the data files keep RIK's name.
  Same day, Marko asked why /beograd/ had no PNG: the export lived in mun.js, which a city's page doesn't load. It
  moved to `static/mapimg.js` (`window.mapImage(figure, data)`), used by mun.js and city.js; the city's JSON gained
  each municipality's registered, valid and votes and the lists' colours, and the image says "the city" and "the
  largest municipalities".
- **10 Nov 2026, Novi Sad's stations without a quarter.** 13 of the city's 153 were left out of the quarters
  (round 680072). Why: a name with no quotes holding a building's whole name and more (ГРАДСКА УПРАВА ЗА
  ИНСПЕКЦИЈСКЕ ПОСЛОВЕ ГРАДА НОВОГ САДА; the rule took only names inside quotes); local communities named for a
  neighbourhood OpenStreetMap draws inside a quarter but leaves out of the map (МЗ САЈЛОВО ×2, МЗ ШАНГАЈ); and
  buildings outside the fetched kinds (ЈКП Водовод и канализација, ЈКП Градско зеленило, Железнице Србије, ДЕС,
  two pensioners' clubs) or missing from OpenStreetMap (ПУ Радосно детињство – вртић Чаробни шешир ×2, Дом
  здравља Лиман). Same rules for every station: an unquoted name is also matched by a building of three or more
  words it holds whole; a named place at least 80% inside one other quarter is a name for that quarter (Liman,
  over Liman 1–4, is not); and the fetch also takes offices, companies' buildings and social centres. No
  per-station table: what OpenStreetMap doesn't have stays out of the quarters.
  First refetch: 142 of 153 placed (the water utility in Rotkvarija, the inspection office in Stari grad).
  Sajlovo and Šangaj are only points in OpenStreetMap, so a neighbourhood's (or locality's) point inside a quarter
  is a name for it too; a suburb's label, over several quarters, is not.
- **10 Nov 2026, Novi Sad's stations placed by an address.** Of the 11 stations OSM has no building for, Marko
  gave four addresses (Čarobni šešir: Desanke Maksimović 80, from predskolska.rs; Dom zdravlja Liman: Bulevar
  cara Lazara 77; Železnice Srbije: Vase Stajića 2; JKP Gradsko zelenilo: Mladena Leskovca 1), kept in
  `data/geo/quarter_addresses.csv` with their source. The geo run asks OSM for those house numbers and places
  each building in the quarter its address point is in; an address OSM lacks places nothing. Sajlovo and Šangaj
  are not quarters (Marko), so their local communities' stations stay apart; DES and the two pensioners' clubs too.
- **10 Nov 2026, the watch's acts on polling stations.** From the watch's candidates (735 links, most of them
  boards, lists, voting outside the station, forms), 22 acts that decide a municipality's polling stations for an
  archived election were added to `data/station_lists.csv`: for 2022 Blace, Kraljevo, Rača, Bač, Bačka Palanka,
  Opovo, Pančevo (a second act), Šid, Prokuplje; for 2023 Bogatić, Golubac, Rača, Bačka Palanka, Kanjiža, Temerin,
  Lapovo; for 2026 Golubac, Kraljevo, Rača, Bačka Palanka, Leskovac, Mali Zvornik. Amendments alone were left out,
  and acts for the local elections of 2024 (no archived round of those municipalities). Three rows came off: a
  2022 decision that a station's results can't be established (Majdanpek: not a list), and two of Pančevo's 2023 acts —
  one for the 2024 local election, one a four-row amendment that had replaced the whole 2023 decision, since a
  municipality's stations were those of the last act read. Now each act keeps its own reading (`"st"` in the
  round's station_lists.json) and a municipality's stations are merged from all its acts in the file's order
  (`stationlist.merge`); an act taken off the file takes what it gave with it. The stations workflow then reads
  every act again once (`reread`).
  What they read: kept the acts whose rows matched the stations — 2022 Kraljevo (97 stations), Rača (25), Opovo
  (12); 2023 Golubac (26), Rača (20), Bačka Palanka (10), Temerin (16); 2026 Golubac (23), Bačka Palanka (25): 254
  stations with a settlement from their act, and Pančevo 2023 back to its decision's 50. Taken off again: acts
  that read no row as a station (2022 Blace, Bačka Palanka, Pančevo's second act, Šid, Prokuplje's .docx; 2023
  Bogatić, Kanjiža, Lapovo — tables or scans the reader doesn't cut), 2022 Bač (its site didn't answer), and 2026
  Kraljevo, Rača, Leskovac (one or two rows matched, Rača's against the addresses) and Mali Zvornik (it disagreed
  with the board decisions' addresses and was set aside).
