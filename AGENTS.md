# AGENTS.md

How to work on this repository, what must not change, and why things are as they are. Written for coding agents
and for people. This file holds the rules of work and the principles; the decisions of each part of the project
are in the files the map below names (20 Nov 2026: this file had grown to 97 KB, read whole by every agent).
**Keep them current:** when a decision is made or changed, add it to its part's file in the same commit; a rule
of work or a principle, here. README.md describes the project for its users; these files are for those who change
it. Dates are the maintainer's decisions unless said otherwise.

## How to work here

- **A branch and a pull request per task** (20 Nov 2026, the maintainer's decision, as several agents work at once,
  the way javni-uvid/zailiprotiv works; from 2 Nov 2026 until then everything was committed straight to `main`):
  - **Each agent in an Orca worktree** of its own (`orca worktree create --name <task> --no-parent`, from the main
    clone): Orca makes the branch, `<the maintainer's GitHub login>/<task>`, from `origin/main`, and the folder
    under `~/orca/workspaces/izborna-analiza/`. Short-lived: hours, a day at most. Orca runs `uv sync` in a new
    worktree itself (`orca.yaml`); `tzdata`, which Windows lacks, is a dependency there.
  - **Before starting, `gh pr list`:** when an open pull request touches the same files, build on it or wait.
  - **Before pushing,** `git rebase origin/main` and `uv run pytest -q`; then `gh pr create` (the template asks
    what, why, what was checked, and whether the maintainer must decide); `gh pr checks --watch` until **test**
    passes on it, then `gh pr merge --squash`: one commit on `main`, the branch deleted. `sh tools/posalji.sh <body
    file>` does all of it in this order and waits for **test** to start before it counts as passed; `--ne-spajaj`
    stops before the merge. A pull request that needs the maintainer (a principle, something seen from outside,
    DNS, email) says so and is left for them to merge.
  - **The workflows still commit data straight to `main`** (results, documents, boards, observers, state…): a
    branch will lag behind in `data/`, which is fine while a task doesn't change `data/`. A task that must change
    `data/` by hand rebases just before it merges.
  - **`main` is guarded on our side:** GitHub's rulesets can't exempt the workflows' own token (GitHub Actions
    can't be a ruleset's bypass actor), so a ruleset requiring pull requests would stop the hourly data runs. The
    repository's ruleset only forbids deleting `main` and force-pushes; `tools/hooks/pre-push` refuses a push to
    `main` from a clone set with `git config core.hooksPath tools/hooks` (its worktrees share it; a fix that can't
    wait: `IZBORI_MAIN=1 git push origin main`). For the same reason GitHub's auto-merge can't be used (it needs a
    required check), so the agent waits for **test** and merges. Squash is the only merge; merged branches are
    deleted.
  - Dependabot's monthly pull requests (the workflows' actions, the Python packages): merge them once their checks
    pass.
- **Workflows, safely** (20 Nov 2026, as in javni-uvid/zailiprotiv): every action pinned to a commit with its
  version in a comment beside it (Dependabot moves both); inputs and context reach scripts through `env`, never
  pasted into `run:` as `${{ }}`; a checkout keeps no token unless its job pushes (`persist-credentials: false`);
  `permissions: {}` at the top and each job asks for the least it needs (`contents: write` to commit, `actions:
  write` to start another workflow, `actions: read` for another run's artifacts). **security** checks all of this
  (zizmor; `.github/zizmor.yml` lists the accepted findings with the reason), the Python packages (pip-audit) and
  the code (CodeQL).
- **Run the whole test suite before every push:** `uv run pytest -q` (about 3 minutes). The **test** workflow runs
  it again on every pull request and on `main`; a red run is fixed before anything else. On Windows set
  `PYTHONUTF8=1` (the maintainer's computer has it for the user); the site's languages are then built one after
  another, and the suite took 42 minutes there on 20 Nov 2026, against some 4 on GitHub's runners. Paths kept to
  compare (`Site.produced`) are POSIX paths: with Windows' backslashes `finish()` removed every page in a folder.
- **Explain why in commit messages.** Say what changed for the site or the data, and the reason.
- **Write the decision down** in its part's file under `docs/decisions/` (the map below), at the end of the
  section it belongs to, in the same commit as the change.
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
- **Talk to the maintainer in Serbian** (Latin script), briefly and to the point. Code, comments and docs are in
  English.

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
| The site: pages and their order, Explore, the maps and the shared image, the palette, the guide, the incremental build, the size budget, hosting | `docs/decisions/site.md` |
| Local elections from the commissions' own documents: the municipal sites and the watch, classifying, the reports' readers, reading by eye | `docs/decisions/local.md` |
| The workflows, their safety, and the tests | `docs/decisions/code.md` |
| The project's course, and decisions that span parts | `docs/decisions/log.md` |

## Known issues and open decisions

- **Belgrade 2024 decisions on polling boards (round 567956):** RIK's register holds only 129 decisions for its
  1,265 stations, listed under "Београд"; the station's name places them by district since 5 Nov 2026, and its 17
  decisions on the extended composition now read. The rest were never published there.
- **Despotovac and Ub 2023 (round 341140):** their decisions on the extended composition (44 and 51) are tables,
  people in one column and lists in the other, which OCR interleaves line by line. Ub's rows give the list's
  ballot number ("члан 6"), but no rule tells an empty name cell from a filled one, and Despotovac's don't even say
  which list a member belongs to: they stay unread rather than guessed (masked layouts in boards run 42106667607).
