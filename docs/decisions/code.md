# The code, workflows and tests

Decisions about the workflows and the tests, moved word for word from AGENTS.md on 20 Nov 2026 (the maintainer's
decision, so that an agent reads the rules and only the decisions of the part it works on: AGENTS.md had grown to 97
KB). **Keep it current:** a decision made or changed is added here, at the end of the section it belongs to, in the
same commit as the change. The principles and the rules of work are in AGENTS.md.

## Workflows

| Workflow | When | What |
|---|---|---|
| update | hourly, plus Sunday evenings; asks RIK by the calendar | results, flags, feeds, email |
| documents | daily | register of minutes, commission documents |
| boards | daily, until 14 days after election day | decisions on polling boards: plan, four OCR jobs, merge (one commit); then the stations' census settlements |
| observers | daily, until 60 days after election day | OCR score of observers' records |
| pages | on push | incremental site build and deploy |
| geo | by hand | municipal boundaries from OpenStreetMap (Overpass); with kim, Kosovo and Metohija in RIK's division |
| census | by hand | the 2022 census tables from the Statistical Office (RZS), into `data/census/2022/` |
| test | on every pull request and push to `main` | the whole test suite |
| security | Mondays, on changes to the code or workflows (main and pull requests), by hand | actionlint, zizmor, pip-audit, CodeQL; reads only |

A run started with `GITHUB_TOKEN` can dispatch another workflow (`gh workflow run`). That is how data runs start
**pages**, and how a watch run starts the next **update** run.

## Tests

- The tests use the real archive in `data/`, plus small made-up files. The full site is built once per module and
  shared; a test that needs changed data builds from a copy of only the rounds it needs.
- When new real data breaks a test on the real archive, find the cause in the code first. The test broken by the
  2023 addresses led to the rule on addresses that contradict the results. Change the expectation only when the new
  data is right and the old expectation was wrong.

## The code

How the code is written, taken from javni-uvid/zailiprotiv on 20 Nov 2026 at the maintainer's request (that
project's `docs/decisions/code.md`), as it fits here. They are rules for new code and for code being changed;
nothing was rewritten to meet them at once.

- **A module per kind of page or source.** `site.py` (1,640 lines) loads the archive, works out what pages share and
  writes them; a new kind of page goes in a module of its own called from the build with what it needs, as
  `bysettlement`, `cities`, `maps` and `highlights` are. A move is checked by building before and after and
  comparing every file.
- **Read once, then work out, then write.** The build reads each file of `data/` once, works out what pages share
  (`Site.round_shared`, cached per election and language), and only then writes pages. Nothing is put into a page
  after it is written, and no module hands data back through an attribute of its function or a global it sets:
  it returns what it computed.
- **Shared helpers, not copies.** A store is written with `jsonfile` (one entry per line); a helper two modules
  need goes in one place rather than in both.
- **The commands may become a package.** `cli.py` is 1,340 lines; zailiprotiv split its own (1,672) into `cli/`
  by kind of command, checked by every command's `--help` giving the same text. Here it waits for a task that
  needs it.
- **A guard on the built site** is not here yet: zailiprotiv's build fails when a page is over 1 MB or loads
  anything from another site (`publish.check`), so principle 5 is checked on every build rather than by review.
  Worth porting when the build is next changed.
- **Faster without changing the output.** A cheaper count (a quick test before an expensive comparison, counting
  once instead of per page) is checked to give the same files byte for byte, and the time is measured before and
  after (AGENTS.md, "Measured, then changed").

## Decisions log

- **9 Nov 2026, today's failed runs.** Three **pages** deploys timed out at GitHub's default 10 minutes in
  "syncing files" (the builds were fine, the next deploys took under 3 minutes): the deploy now waits 30. Two
  **geo** runs failed on Overpass's 504: a third server joins the rotation. The morning's **test** and **stations**
  failures were the station-list bugs fixed the same hour.
- **20 Nov 2026, workflows hardened** (as zailiprotiv did on 17 Nov): actions pinned to commits at the versions
  Dependabot's first pull request proposed (#4), `${{ }}` out of `run:`, no token kept by checkouts that don't push
  (boards' plan and read, local's classify, pages' build, probe, test), and permissions per job. The stations
  workflow lost `actions: write`: nothing in it starts another workflow. A **security** workflow runs actionlint,
  zizmor (the workflows that push accept `artipacked`), pip-audit and CodeQL.
- **20 Nov 2026, the tests on Windows.** On the maintainer's computer 13 tests of `test_outputs.py` failed: the
  site had no page in any folder. `Site.produced` recorded the static files by `str()` of their path and
  `finish()` compared every file the same way, so on Windows `r\680072\index.html` was never among the pages
  written (`r/680072/index.html`) and was removed. Both now use `as_posix()`, as does `code_version`; on Linux
  nothing changes.
- **20 Nov 2026, the site's tests left to the pull request on Windows.** Locally the suite took 40 minutes and more
  on the maintainer's computer, twice stopped for want of memory; all but `tests/test_outputs.py` take a minute.
  That module is marked `site`, and on Windows `tests/conftest.py` deselects it unless `-m` or
  `IZBORI_SVI_TESTOVI=1` asks otherwise, so `posalji.sh` (osnova's, which runs `uv run pytest -q`) needs no option.
  Measured that day: one build of the whole archive takes some 6 minutes there under a profiler (67,000 files,
  1.9 GB at its peak), most of it Jinja rendering the places', the rounds' and the municipalities' pages, with the
  two scripts built one after another (no `fork` on Windows); the module builds the whole archive once, the 2026
  round again and two small rounds twelve times. Making the build faster on Windows is open.
