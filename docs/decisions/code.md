# Workflows and tests

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
