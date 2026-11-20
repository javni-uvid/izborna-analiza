# AGENTS.md

How to work on this repository, what must not change, and why things are as they are. Written for coding agents
and for people. This file holds the rules of work and the principles; the decisions of each part of the project
are in the files the map below names (20 Nov 2026: this file had grown to 97 KB, read whole by every agent).
**Keep them current:** when a decision is made or changed, add it to its part's file in the same commit; a rule
of work or a principle, here. README.md describes the project for its users; these files are for those who change
it. Dates are the maintainer's decisions unless said otherwise.

## How to work here

- **The rules every javni-uvid project shares are in `osnova/`: read `osnova/work.md` before anything else**
  (20 Nov 2026, the maintainer's decision; until then each project kept a hand-made copy of them here). A branch
  and a pull request per task in an Orca worktree, `gh pr list` before starting, `sh tools/posalji.sh <body file>`
  to ship, the decision written down in the same commit, why in the commit message, Serbian with the maintainer.
  `osnova/security.md` holds the guards and `osnova/principles.md` the promises every project makes. The folder is
  a copy the **osnova** workflow brings from `javni-uvid/osnova`: a rule that should hold for every project is
  changed there, never in `osnova/` here. What follows is only this project's.
- **A worktree** is under `~/orca/workspaces/izborna-analiza/`; Orca runs `uv sync` in a new one itself
  (`orca.yaml`); `tzdata`, which Windows lacks, is a dependency there. The workflows that commit data straight to
  `main` are results, documents, boards, observers, state and the like. A pull request that needs the maintainer
  here: a principle, something seen from outside, DNS, email.
- **A decision goes at the end of the section it belongs to** in its part's file under `docs/decisions/` (the map
  below). A rule of work or a principle of this project, here.
- **Workflows, safely:** the rules are in `osnova/security.md`. Here a job asks for `contents: write` to commit,
  `actions: write` to start another workflow, `actions: read` for another run's artifacts; `.github/zizmor.yml`
  lists the accepted findings with the reason.
- **The tests are `uv run pytest -q`** (about 3 minutes), the whole suite before every push. The **test** workflow runs
  it again on every pull request and on `main`; a red run is fixed before anything else. On Windows set
  `PYTHONUTF8=1` (the maintainer's computer has it for the user); the site's languages are then built one after
  another, and the suite took 42 minutes there on 20 Nov 2026, against some 4 on GitHub's runners. Paths kept to
  compare (`Site.produced`) are POSIX paths: with Windows' backslashes `finish()` removed every page in a folder.
- **Measured, then changed** (from zailiprotiv, 20 Nov 2026). Work on speed or size starts from a measurement
  (a profile, `--durations`, the site's size) and says the before and after. A change meant to keep the output
  (a refactor, a faster count, a module moved) is checked by building the site before and after on the same data
  and comparing every file; the pull request says how many differed and why.
- **Secrets live in GitHub Secrets only** (the mail's SMTP settings). Never ask the maintainer to paste one in a
  chat, and never print one in a log.
- **Update README.md with every feature:** the section that describes it, the archive layout, the commands, the
  module layout and the schedule, as they apply.
- **Ask RIK little.** A one-off full pass through a register is fine when a feature needs it. Recurring reads must
  be incremental, or gated by the election calendar (see *Fetching from RIK* in `docs/decisions/data.md`).
- **The development sandbox may not reach RIK; GitHub's runners can.** Run anything that needs RIK through
  `workflow_dispatch`. To tune OCR on real documents, use the masked diagnostics: `izbori observers --station
  CODE/NUMBER --diagnose N --layout` and `izbori boards --diagnose N` print the layout with every word that isn't
  printed on the form masked.
- **Only one pending run per workflow.** Each workflow has a concurrency group; a second dispatch while one is
  pending cancels the pending one. Queue at most one run of a workflow at a time.

## Principles

These are the project's promises to its readers. Never change them without the maintainer.

1. **The same rules for every contestant.** No party is hardcoded. A test swaps contestants' votes and checks that
   the flags don't change.
2. **A flag is a question, not a verdict.** The site says "unusual, check the minutes", never "fraud".
3. **Flags come from primary sources only:** laws, RIK's documents, ODIHR reports. A news report is a note, marked
   unconfirmed; it never makes a flag or changes a ranking. An OCR score is never a flag either.
4. **No personally identifying data; link to RIK instead** (the maintainer's decision, 3 Nov 2026).
   - The archive, the site, logs and CI output never record a person's name or other identifying detail, even
     though RIK publishes them in its documents (board members, observers, commission members). Linking to RIK's
     own document is always fine: whoever needs the names reads them there.
   - Never store, log, print or transcribe a name from a document.
   - Don't copy titles that commissions write: they may name a person. Keep RIK's own kind of document instead.
   - Diagnostics in public CI logs mask every word that isn't printed on the form.
   - Summaries of observers' remarks never name anyone.
   - Anything parsed from a document that could hold a name is checked before it is kept. For example,
     `boards.clean_address` drops a member's line read where an address should be, and stores are scrubbed when
     they are read and written.
5. **Nothing from third parties on the pages:** no analytics scripts, cookies, external fonts or scripts. Visitor
   counts, if any, come from the host or the edge (for example Cloudflare's proxy analytics), not from a script on
   the page.
6. **The observer target list stays private.** It is never committed or built in GitHub Actions, because anyone
   with a GitHub account can download a public repository's build outputs.

## Where the decisions are

Read the file of the part you work on before you start; each keeps the sections' and entries' words as they were
here. A decision goes at the end of the section it belongs to in its part's file, rather than inside another's
paragraph; a rule of work or a principle, here.

| Part | File |
|---|---|
| The archive and its stores, fetching from RIK (endpoints, the calendar, incremental reads), the census, stations' settlements, places across elections, the acts on polling stations, Novi Sad's quarters | `docs/decisions/data.md` |
| OCR: decisions on polling boards (controllers by list, layouts, kinds, placement, the reading's version), observers' records | `docs/decisions/boards.md` |
| The site: design rules, pages and their order, Explore, the maps and the shared image, the palette, the guide, the incremental build, the size budget, hosting | `docs/decisions/site.md` |
| Local elections from the commissions' own documents: the municipal sites and the watch, classifying, the reports' readers, reading by eye | `docs/decisions/local.md` |
| How the code is written, the workflows and their safety, the tests | `docs/decisions/code.md` |
| The project's course, and decisions that span parts | `docs/decisions/log.md` |

## Known issues and open decisions

- **Belgrade 2024 decisions on polling boards (round 567956):** RIK's register holds only 129 decisions for its
  1,265 stations, listed under "Београд"; the station's name places them by district since 5 Nov 2026, and its 17
  decisions on the extended composition now read. The rest were never published there.
- **Despotovac and Ub 2023 (round 341140):** their decisions on the extended composition (44 and 51) are tables,
  people in one column and lists in the other, which OCR interleaves line by line. Ub's rows give the list's
  ballot number ("члан 6"), but no rule tells an empty name cell from a filled one, and Despotovac's don't even say
  which list a member belongs to: they stay unread rather than guessed (masked layouts in boards run 42106667607).
