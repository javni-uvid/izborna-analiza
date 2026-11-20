# Local elections from the commissions' own documents

Decisions about local elections read from the municipal commissions' own documents and sites, moved word for word
from AGENTS.md on 20 Nov 2026 (the maintainer's decision, so that an agent reads the rules and only the decisions of
the part it works on: AGENTS.md had grown to 97 KB). **Keep it current:** a decision made or changed is added here,
at the end of the section it belongs to, in the same commit as the change. The principles and the rules of work are
in AGENTS.md.

## Decisions log

- **8 Nov 2026, preparing for local elections.** Marko asked how to prepare; agreed order: (1) a registry of the
  municipalities' sites and a weekly watch for the commissions' documents (done: `data/municipal_sites.csv` from
  RIK's address book — only the e-mail's domain is kept, never the address, phone or mailbox — and `watch.py`);
  later a pre-election mode of the municipality page (stations, controller coverage, deadlines before any result),
  rounds of one day grouped on the elections page and the home, the "area" column of the station acts as a
  street index for "where do I vote", feeds that announce new commission documents, and a size/time measurement
  with dozens of simultaneous rounds. Not a dry run on Belgrade 2024: Marko expects Belgrade's commission to be the
  best-run; a small municipality's local election is the better test.
  9 Nov: the first pass left 100 of 148 sites with nothing — 28 didn't answer (24 URLError, 4 HTTP 403/5xx),
  72 answered with nothing found. Marko asked for both now. The watch goes three links deep (pages about documents,
  notices and decisions too, up to 100 pages), reads WordPress's upload search and the sitemaps, sends a
  browser-like client name, and logs why a site failed, so a certificate problem can be told from a site that is
  down. Run by hand for those 100 (`only`).
  9 Nov, what to do with what the watch found (2,607 documents, 48 municipalities): Marko chose local elections
  from the commissions' own documents — board decisions for controllers by list, then the results tables — on
  Pančevo first (1,082 documents: 2023/11–12 and 2024/04 uploads), plus the new acts on polling stations for the
  stations still without a settlement. `local.py` starts with a masked probe of the layouts (workflow **local**).
  The first probe of Pančevo's 121 commission documents: minutes of the commission's sessions and proposals of
  lists, many of them of the 2026 parliamentary election (the site's upload folders don't follow the dates). The
  results of a local election weren't among them: the watch kept only documents about stations, boards or "the
  commission", and a results report names none of those. It now also keeps "results" (rezultat + izbor, odbornici,
  zapisnik, izveštaj) and "lists" (list + proglašenje, zbirna, kandidati, odbornici).
  Marko asked how to handle 145 sites that all differ. Not a project or an analyser per site: the law fixes the
  documents, the sites differ in where they put them. So three layers in this repo — discovery the same for every
  site (a site's quirks as data in municipal_sites.csv, code only where nothing else works), classification by the
  first page's words of the form (`local.classify`, data/local_docs.json), readers per kind of document, not per
  site, a new layout a new variant of the reader. Unclassified documents go to a list for a person, coverage per
  municipality is shown as a fact. Order: classification, Pančevo end to end, then Temerin and Sečanj.
  Marko: Valjevo's site is valjevo.rs, not the mail's valjevo.org.rs, "and some sites may be like that". A domain
  that doesn't answer is now tried as name.rs, name.org.rs, name.ls.gov.rs, name.gov.rs; the one that answers is
  written back to municipal_sites.csv with the old one in the note, so the file stays the record of where to look.
  The deeper pass over the 100 sites crashed after 2.5 hours on one malformed link ("Invalid IPv6 URL") and kept
  nothing, since the store was written only at the end. Now a link that doesn't parse is skipped, a site that
  throws is logged and passed, and the store is written after every site with finds.
  10 Nov, Pančevo's local results: its "ukupan izveštaj o rezultatima … za sva biračka mesta" (2 June 2024) is a
  scanned typed table that OCR reads well (79 stations, five lists). `local.result_rows` checks each row against
  itself and sets aside what doesn't add up; the reading becomes a draft round in RIK's format (`local.build`,
  data/local/L80314-20240602/), its stations named from the 2026 round (the same 79, by number), published by
  moving it to data/rounds/ after a check. The lists' names come from the proclamations (contestants, public as
  RIK's are; a precedent: Belgrade 2024's round names its lists' leaders). Station minutes (158) are not read:
  hand-filled, OCR is unreliable on them.
  First reading: 74 of 79 stations add up; registered (106,192) and valid (49,527) match the published totals to
  the vote, invalid is 26 short (1,567 of 1,593: some derived cell). Marko read the five set aside in the report
  (`data/local_corrections.csv`) and confirmed the lists' names (`data/local_lists.csv`, from the decision on the
  collective list, a scan). With them every list's total matches. The report's column order differs from
  Wikipedia's (ordered by votes): 1 Vučić, 2 SVM, 3 Pančevo protiv nasilja, 4 POKS, 5 Pančevačka grupa.
  Published the same day as round `L80314-20240602` (moved from data/local/ to data/rounds/): the first local
  election read from a commission's own documents. Invalid ballots looked 26 short of Wikipedia's 1,593, but Marko
  checked the four cells derived from a sum (stations 16, 26, 69, 74) and they are right: Wikipedia's figure is
  voters (51,120, which matches) less valid votes, while the report's invalid ballots count what was in the box
  (51,094 ballots = 49,527 valid + 1,567 invalid). The 26 are voters who signed but left no ballot in the box.
  10 Nov, Pančevo's polling boards. The commission published, per station, the standing composition
  (`N-stalni-sastav.pdf`, 79), the extended (`BM-N-Prosireni-sastav.pdf`, 79; classified as lists' documents,
  since they name the lists) and 44 changes (`N_PS.pdf`, `izmena-bm-…`). The extended one writes a slot as
  "1. član: <person>, <…>, <list>;" and its deputy on the next line, with no "na predlog", which RIK's reader
  doesn't take, so `local.board_slots` matches each role's own text to a list (`boards.match_list`) and keeps
  only the list's number and whether the role was filled; changes and the standing composition are kept as links
  (`local.read_board`, by the decision's title). `izbori local --boards ROUND` (the workflow's `results` input with
  `kind` boards) reads the documents of the 60 days before the election into the round's boards.json in RIK's
  store format, with the commission's own link, so the site shows controllers and decisions as for RIK's rounds.
  With `path_has` as well, only those documents are read and each role is logged with every word masked but
  the lists' own after its first comma (`local.role_shape`), to see why a role matched no list; nothing is kept.
  The first full reading put list 4's roles under list 3 ("Панчево-Борба против насиља" shares three words with
  list 3's name; `boards.match_list` divides by the shorter name) and matched none of list 5's, named in the
  decisions as Група грађана „ГРУПА ПАНЧЕВО", not by its ballot name. `local.role_list` now counts, in the role's
  text after the person, the words of each list's name that no other list's name has ("Панчево", "против",
  "насиља" are in three; "борба" only in list 4's), the best clearly ahead and with two of its words in the text;
  or, for a citizens' group, the round's only citizens' group list (two such lists: not guessed). OCR's garbled
  "2. чпан;" and "~ замсник 1. чпана:" at a line's start still start a role (the deputy's on one line: "сутра" at
  the end of a line once took the next member for a deputy), and a role in quotes, as a supplement (допуна)
  writes it, is read. Third reading: lists 1–5 have a member at 79, 76, 79, 70 and 65 of 79 stations; at 103
  slots a list named its member and no deputy (the decisions have no deputy's line there). Left: station 65's
  decision, whose OCR garbled lists 2 and 4 (four roles matched to no list), and a supplement at station 54
  whose one role names its list otherwise than any of the five (not guessed). The controllers' note on a local
  round names the commission's decisions on the municipality's site as the source (`ctrl_note_local`).
  10 Nov, Temerin and Sečanj: the watch found neither one's report of results. Sečanj's commission adopted its
  "Ukupni izveštaj o rezultatima" on 21 Dec 2025 (minutes of its 25th session, after the repeated vote at
  stations 7 and 8), but no upload by that name was among the documents: the media search looked only for boards,
  stations and the commission. It now also asks for results and reports, and the site's search for "rezultati
  izbora". That found both: Sečanj's `2025/12/Ukupan-izvestaj.pdf` (classified as a list's document) and
  Temerin's "УКУПАН ИЗВЕШТАЈ О РЕЗУЛТАТИМА ИЗБОРА ЗА ОДБОРНИКЕ…" (dated 6 June, its own day). So `--results` no
  longer asks for the kind or the election's day: any local report with "izveštaj" in its link, dated up to 40
  days after, is read, and the one with most stations kept (`local.report_candidates`).
  Both reports hold only the municipality's totals (Temerin: 31 stations, 24,763 registered, 11,687 valid, four
  lists; Sečanj: 17 stations, 10,226 registered, 6,787 valid, five lists). Results by station are only in the
  boards' minutes, filled in by hand: OCR reads "5 4 6'" for a number. Marko chose to have them read by eye:
  `local.crop_results` cuts out the minutes' results section (from "РЕЗУЛТАТИ" to the board, its members,
  signatures or remarks, by Tesseract's line boxes), the images go to a temporary branch `crops-tmp`
  (a run's artifacts are stored where the session can't reach), deleted once read, and Claude
  reads the numbers into `data/local_hand.csv`; each row must add up and all of them to the report's totals,
  and a row that doesn't is left for Marko.
  Read the same day. Temerin: 31 stations, every row adds up, and their sum is the report's to the vote
  (registered 24,763, voted 12,055, ballots 12,054, invalid 367, lists 7,208 / 2,002 / 2,055 / 422). Sečanj: 17
  stations, stations 7 and 8 from their repeated votes (10 and 17 Dec 2025; the first minutes summed with the
  rest miss the report by 10 valid votes, the repeats match it exactly): voted 6,966, ballots 6,965, invalid 178,
  lists 4,103 / 285 / 111 / 2,179 / 109; the registered voters add up to 10,227, one more than the report's
  10,226, with every cell read twice: left as the minutes have it, for Marko. The lists' names are printed on the
  minutes. Published as `L80446-20240602` and `L80373-20251130`. A municipality's page no longer lists another
  municipality's local election among the elections it "didn't vote in".
  10 Nov, the classifier reads the title first. The whole first page misfiled documents that name lists,
  boards and results in passing: Pančevo's extended boards (BM-N-Prosireni-sastav) as lists, Sečanj's report of
  results as lists, and the appointments to Sečanj's commission on the lists' proposals as results. Now the title
  (from the heading in capitals — РЕШЕЊЕ, ИЗВЕШТАЈ, ЗАПИСНИК, ОДЛУКА — 400 characters) is matched first
  (`local.TITLE_KINDS`, with a new kind, `commission`, for appointments to the electoral commission), the page
  only when the title matches nothing. Entries carry the classification's version (`v`); `run_classify` reads
  the new documents first, then every entry of an older version again, so one rule applies to all.
  `izbori local --overview` answers what can be published next: per municipality, its local documents
  grouped by time (a document's day is often its own date, not the election's), and for each group whether a
  report by station reads (`result_rows`, at least 3 rows), only a report of totals exists, or only minutes.
- **10 Nov 2026, classifying in parallel.** Reading the first page of all 4,838 documents again (a new
  classification's version) took one runner most of a day at four documents at once. Now the workflow's classify
  is a matrix of 8 runners, each with its share of municipalities (`local.shard_of`: largest first onto the least
  loaded share, the same split in every runner); a municipality stays on one runner, so its site gets no more
  requests at once than before. Each part's `data/local_docs.json` is an artifact, and a merge job commits every
  entry that differs from main's (`local.merge_parts`), also when some parts ran out of time, since a run resumes.
  The crops and crops-read runs have their own concurrency group: they commit nothing to main, so they don't wait.
- **10 Nov 2026, reading sheets for minutes filled in by hand.** Asked whether reading the minutes could be
  automatic, I measured on the 48 stations of Temerin 2024 and Sečanj 2025 read by eye: Tesseract read 14% of the
  handwritten cells; a small network trained on MNIST about 70% (78% once the cells were found by long ruled lines
  only); taking the most likely figures that add up (ballots less invalid are the valid votes, the lists sum to
  them) accepted 10 of Temerin's 31 stations with 2 wrong and 3 of Sečanj's 17 with all 3 wrong — a figure that
  adds up isn't a right one, and the registered voters aren't checked by any sum. So nothing is taken from a
  model. What it does instead: `izbori local --crops … --sheets` (the workflow's crops) puts only the number cells
  on reading sheets, a row per station, with the model's guess under each and red where a station doesn't add up,
  so a municipality is read from two or three images and nothing but figures leaves the minutes. 30 of Temerin's 31
  and all of Sečanj's stations were found that way. numpy, OpenCV and scikit-learn come in with `uv run --with`
  in the workflow only, as shapely does for geo; their tests skip without them.
- **10 Nov 2026, a queued classify builds on the one before.** The classify and merge jobs check out the branch as
  it is when they start, not the commit the run was dispatched on, so a run queued behind another one (the same
  concurrency group) skips what that one committed instead of reading it again and failing to push its merge.
- **10 Nov 2026, a site that doesn't answer is skipped while classifying.** The first sharded run took 1 to 32
  minutes for seven of its parts and more than an hour for the eighth: its municipality, Bač (734 documents on
  bac.rs), didn't answer, so each document waited out the download's 90-second timeout, four at a time. A share
  by municipality keeps a site's requests to one runner, so one dead site holds up only its part — but the merge
  waits for every part. Now five failures in a row from a site skip its other documents for that run (they stay
  unclassified, so the next run asks again). Classifying runs in threads instead of processes: the reading is
  pdftotext and tesseract, run as processes anyway, and the threads share the count.
- **10 Nov 2026, merging a cancelled classify.** Bač's part was stopped by hand. The merge job's steps now run
  even when the run is cancelled, and `kind` merge with a run's id in `code` merges that run's parts from its
  artifacts (`actions: read`), for a run dispatched before this change. The workflow is at GitHub's ten inputs,
  so this reuses `code` and `kind`.
- **10 Nov 2026, the merge undid shards.** The first sharded merge took every entry of a part that differed from
  the store being merged into. But each part is the whole store as its runner began plus its own reading, so a
  later part's old entries put back what an earlier part had just read: Pančevo, Temerin and Sečanj (1,862
  documents read) were left as before. Now an entry is taken only when the store lacks it or the part read it
  by a newer classifier version, which doesn't depend on the parts' order; that run's parts were merged again
  (`kind` merge).
- **10 Nov 2026, several municipalities' results in one run.** The local runs that commit wait for each other and
  GitHub keeps only one waiting, so `--results` takes the codes of one election day comma-separated (17 Dec 2023:
  Prokuplje, Rača, Golubac), each named from the sites file, one that fails not stopping the rest, and the drafts
  are committed together.
- **11 Nov 2026, the reports of 17 Dec 2023.** Prokuplje's report is a scanned table: 18 of its 90 stations were
  set aside, most because OCR read a one or an eleven as strokes and not as many as there were ("||" for 1, "|"
  for 11), so they were off by ten. A cell of strokes is now 1, 11 or 111, taken as the one combination that makes
  the lists add up to the valid votes, and noted on the row; two ways, or none, and it stays aside. Rača's and
  Golubac's reports aren't tables but a section per station with labelled lines, which read no row at all: they
  are read by `section_rows` (headings "број 1" or "бр. 1", labelled figures, a line per list ending in its
  votes), with ballots taken as valid and invalid since these reports don't give them.
- **11 Nov 2026, a report's pages to read by eye.** The stations a report's reader sets aside, and the lists'
  names where no proclamation was found, are read from the report itself: `kind` pages renders the documents
  whose link holds `path_has` (several municipalities' codes in `code`) at 150 dpi, each page cut above the first
  line of a signature block (`PAGE_END`: "Број:", the president or deputy, "М.П."), onto the crops' temporary
  branch, deleted once read. A report holds no one's name but the lists' and the signatories', so this is the
  same rule as the minutes' crops.
- **11 Nov 2026, 17 Dec 2023 read against the reports.** Every station of Prokuplje (91), Rača (27) and Golubac
  (30) was read by eye from the reports' pages and compared with what the readers made: the rows read were right
  but for three of Prokuplje's that added up wrong (station 62's first two lists read 15 and 105 for 115 and 5;
  66's strokes taken for lists 5 and 2 the wrong way round; 70's turnout 45 for 43) and one OCR lost altogether
  (33). With the stations set aside, these are in `data/local_corrections.csv`, and every total then matches the
  commission's own (Prokuplje's summary page, Rača's and Golubac's separate reports of totals). Golubac's report
  prints station 14's valid votes as 14 and 18's as 211, where its lists and its other figures give 141 and 208;
  the corrections take those and say so. A correction now brings back a station OCR lost when it gives every
  figure. The lists' names are the reports' own.
  Published (moved to `data/rounds/`): every station of the three adds up and their sums are the commissions' totals
  to the vote.
- **11 Nov 2026, Zemun 2024: a report on its side.** Of the four documents classified as results that the overview
  didn't count as reports, Aleksandrovac 2020 and Brus 2023 hold the municipality's totals only, and Kraljevo's
  "Skup1" is the commission's rules of procedure. Zemun's "Rezultati 02. juna 2024." is a report with a table of
  its 115 stations, scanned sideways. Reports are now also links with "rezultati", and their scans are read at
  300 dpi, each page turned upright first by Tesseract's orientation detection (`boards.upright`, with
  ImageMagick) when it is sure enough.  The first try read one page: OCR stops at a decision's end ("Образложење"), which Zemun's first page has before
  its table; a report is now read to its last page (`to_end`).  Turned upright, Zemun's table still read badly: Tesseract took its ruled lines for ones and ran cells together.
  Taking the lines out first (`boards.unruled`, OpenCV, in the results step with `uv run --with` as for the
  sheets) read a test page nearly whole.
- **11 Nov 2026, Zemun 2024 read by eye.** With the scan turned, its lines taken out and read as one block
  (`--psm 6` when the first reading gives no row), OCR gave 61 rows of 115, but numbered by their order, and with
  rows lost on the way every one after was a station off: 114 of 115 differed from the report. So the stations'
  numbers OCR gives are not to be trusted where it drops rows, and every station was read by eye from the turned
  pages into `data/local_corrections.csv`: each row adds up, and the sums are the commission's totals to the vote
  (169,069 registered, 77,463 out, 77,415 voted, 1,770 invalid, 75,645 valid, all nine lists). The lists' names
  are the report's; the stations' names come from the Belgrade round of the same day (567956).  Published: 115 stations, named from that round, its totals the commission's.  Zemun's publishing commit went out with two tests failing (the place pages of its gymnasium now show five
  elections, the local one among them): the run's result was piped through `tail`, which hid its exit code. Fixed in
  the next commit; test runs before a push are now checked by their exit code, not their last line.
- **11 Nov 2026, links that failed.** A fork searched for the official sites of the municipalities whose documents
  didn't download: none moved and none is dead (Bač's bac.rs answers again; it didn't during the night's run).
  The 148 other documents fail by their links: 42 of Kanjiža's have backslashes in their path, 45 of Golubac's end
  in "?lang=lat" (the site answers with a page), 21 are old Word .doc files. `local.download` now turns
  backslashes into slashes and asks again without "?lang=" when a page comes back, and `.doc` is read by antiword
  (installed in the local workflow).
- **11 Nov 2026, faster local rounds (Marko's go-ahead on the proposals).** (1) A draft is checked against the
  commission's own totals, read from the reports (`totals_of`, `check_totals` into `meta.local.check`; "ready to
  publish" when nothing is set aside and the sums match to the vote), so the totals no longer need reading by
  eye; the swap Prokuplje's station 62 had (two lists off by a hundred each way, the row adding up) is what this
  catches. (2) One run per municipality instead of three: a draft that isn't ready leaves its report's pages on
  the temporary branch, and `results=day` takes every municipality with a report of that date not yet published.
  (4) The overview counts as reports the documents classified as results and links with "rezultati", which it
  missed for Zemun, Rača and Golubac. (3) — classifying again from masked first pages kept in the store — waits:
  whether the masked text classifies as the full one does has to be measured on a real run first.  The first `results=day` (2 June 2024) found four municipalities with a report of that day not yet published —
  Alibunar, Bačka Palanka, Kanjiža, Novi Kneževac — and none is by station: decisions on preliminary results or the
  totals. A day with no report by station is an answer, so such a run no longer fails. The classify run after the
  link fixes read 618 more documents (Bač's among them); 122 are left, 45 of them Golubac's "?lang=" links.  With Bač classified, the overview counts 69 local elections in 41 municipalities: 5 with a report by station
  (all published), 21 with the commission's totals only, 7 with some boards' minutes. Bač 2024 has its totals
  and preliminary results only, each found twice (bac.rs and www.bac.rs): a report's link is now read once
  whatever its "www.".
- **11 Nov 2026, local runs that "failed".** Seven of the night's local runs were red, none by an error: each was a
  results run whose reports held no table of stations (Zemun's while its reading was being made, Bač's totals,
  the first `results=day` before it was allowed to find none), which exited 1. A results run now fails only on an
  error, and writes what each municipality gave to the run's summary page (stations and "ready to publish", or
  what's left: stations set aside, sums that aren't the commission's totals, or no report by station).
- **11 Nov 2026, a dry run of the reader.** `kind` check with `results` runs the reader as it would on a report
  never read before: no corrections, nothing committed, the report's pages kept if the draft isn't ready. It is
  how the totals check and the pages in the same run were tried on Prokuplje 2023, whose station 62 the reader
  reads wrong while the row adds up.  The dry run read 84 of Prokuplje's stations (2 set aside, 5 lost) where the first reading had 87 (3 aside): turning
  and taking the lines out, which Zemun needed, costs Prokuplje's cleaner scan. So a report is now read both as it
  is and turned (and as one block when neither gives a row), keeping the reading with most stations.  Read so again, Prokuplje's 87 stations already give list 2 1,840 votes of its 1,819 with three stations to come:
  the check now names such lists (`over`), a misread row that adds up, before anything set aside is read.
- **11 Nov 2026, Golubac's links.** Its 45 unread documents ("…/SOG 1.docx?lang=lat", "Rešenje o proglašenju … .pdf")
  give an HTTP error as they are, without "?lang=" and with their spaces as hyphens (`link_variants`, tried in
  turn on 403 or 404). The probe now logs the error's code.
- **11 Nov 2026, Golubac's links are gone; controllers for the new rounds; where the watch starts.** All of
  Golubac's unread links give 404 in every spelling: the files are no longer on its site. Of the four local
  rounds published from reports, only Golubac has a board decision in the weeks before (one, extending one
  station's board); Prokuplje, Rača and Zemun have none on their sites. 79 of the 168 municipal sites gave the
  watch no document at all, so `municipal_sites.csv` gets a `pages` column — the commission's own pages, found by
  hand or search, read first — and the watch takes documents from a municipality's subdomains too.
- **11 Nov 2026, the empty sites by web search.** Of the 79 municipal sites that gave the watch nothing, a fork
  searched each for its official site and its commission's page (only the municipality's own domain counts).
  Nine webmail rows got their site (Arilje, Veliko Gradište, Vlasotince, Kosjerić, Koceljeva, Merošina, Niška Banja,
  Bečej, Ruma), four wrong domains were corrected (Bela Palanka's "belapalanak.ls.gov.rs", Zvezdara, Kuršumlija,
  Čačak), and Novi Sad got its commission's page on skupstina.novisad.rs. Searches rarely surface a commission's
  page, only its files; the rest are unchanged. Two things for later: several municipalities keep their files on
  media.readycms.io (their CMS's host, which `same_site` rejects), and RIK's own site carries some local
  commissions' reports ("extfile/sr/files/additionalDocuments/…", Ruma's totals among them).
- **11 Nov 2026, a CMS's file host.** Some municipalities' sites keep their files on their CMS's host
  (media.readycms.io: Ub's gazette, probably Lajkovac's lists). A document there now counts when it is linked from
  the municipality's own pages (`watch.FILE_HOSTS`); the host's own pages aren't followed, since it serves other
  sites too. RIK's results app has one local round (Belgrade 2024); the local commissions' documents it hosts under
  additionalDocuments (Ruma's totals, a decision of Novi Sad's) aren't reached by any of our readers yet.
- **11 Nov 2026, Vlasotince 2023 from its report.** The watch's new start pages found Vlasotince's „Укупни
  извештај о резултатима гласања … на бирачким местима“ (form ЛИ-ВЛ-22/23): a scanned table of its 58 stations and
  11 lists, which the reader made 12 rows of. Every station was read by eye from it into the corrections; each adds
  up, and the sums are the commission's totals to the vote (22,901 registered, 16,457 out, 16,454 voted, 429
  invalid, 16,025 valid, all eleven lists). The report says it is to be published on RIK's site: since the law of
  2022 (art. 59), each local commission's report by station should be among RIK's documents — a source for every
  municipality's local elections, not yet read.  Published, 58 stations named from the parliamentary round of the same day (341140). The totals check couldn't
  confirm it by itself: the report writes thousands with a space ("22 901"), now read, and gives the lists' votes
  without shares, which `totals_of` doesn't take; the sums were checked against the report by eye.
- **12 Nov 2026, RIK's register holds the local commissions' reports.** `izbori register` (probe `register`) read
  RIK's register of commissions' documents for its local rounds: Lokalni 2022, 2023 and 2024, the city
  municipalities of 2024 and 2026, Belgrade's rounds, and the 2025 and 2026 local elections. Each holds thousands of
  commission documents (5,374 for 2024, 5,184 for 2023) and a total report („Укупан/Укупни/Збирни извештај о
  резултатима…“) for nearly every municipality listed: 13 of 14 for 2022, 64 of 66 for 2023, 65 of 66 for 2024, 23
  of 23 city municipalities in 2024, all 9 in 2026 and all 5 in 2025 — about 180 local elections, against the 6
  reports by station the municipal sites gave. Whether each is by station (as the law asks since 2022) or totals
  only is not known from the title, so `register --reports` (probe `reports`) fetches each and logs its shape only:
  pages, text layer or scan, and lines with five or more figures. No title or text is stored.
  The first run: 208 total reports, 172 of them scans, so their shape said nothing — a scan of 2–4 pages is a table
  by station (Vlasotince's, 3 pages) as often as totals (Temerin's, 3 pages). Of the 36 with a text layer, 19 have
  15 or more rows of figures (Prokuplje 2023: 103). A scan's first two pages are now read by OCR as a report's are
  (upright, ruled lines out, psm 6) and their rows of figures counted, four reports at a time.
  With OCR: of 184 local elections with a total report, 30 have 15 or more rows of figures on their first pages
  (their text layer or OCR) — a table by station: Kraljevo 2023, Jagodina, Subotica, Ruma, Šid, Bečej 2024,
  Lazarevac, Čukarica, Stari grad, Palilula 2024 and others — and 40 more have 5 to 14. The count misses known
  tables: Vlasotince's and Zemun's (1 and 2 rows: their scans are hard to read), Rača's (a section per station), so
  it is a floor, not a sorting; which of the rest are by station needs each first page seen.
