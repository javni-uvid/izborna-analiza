# Decisions log

Decisions about the project's course, moved word for word from AGENTS.md on 20 Nov 2026 (the maintainer's decision,
so that an agent reads the rules and only the decisions of the part it works on: AGENTS.md had grown to 97 KB).
**Keep it current:** a decision made or changed is added here, at the end of the section it belongs to, in the same
commit as the change. The principles and the rules of work are in AGENTS.md.

## The project's course

- **2 Nov 2026:** work goes straight to `main`; the place pages follow each station across elections, matched by
  address, then name, then number.
- **3 Nov 2026:**
  - Observers' records are reviewed by a person; OCR only orders the list.
  - RIK's registers are read incrementally, and results by the election calendar.
  - Decisions on polling boards are linked on the place's page.
  - The commissions' documents are listed on the municipality page without their titles.
  - Member lines are never kept as addresses, and an address that contradicts the results is not used.
  - Personally identifying data is never recorded; links to RIK's documents are. The 401 member lines that
    leaked into `boards.json` as addresses before this date stay in git history: the names are public at RIK,
    the fragments are shown nowhere, and rewriting history would break every clone. It is not rewritten.
  - Repeated markup was cut from 713 MB to 657 MB, and the languages are built in parallel.
  - Decisions on polling boards are read in four jobs at once, and the stores are written one entry per line.
  - "In short" on the pages across elections is short labelled rows (flags, turnout, most votes, the place,
    records), the main fact first and context below, figures for the latest election unless a line names
    another, instead of paragraphs of sentences. The maintainer chose this layout.
  - The custom domain waits until it is clear how useful the site is.
- **12 Nov 2026, the organization is javni-uvid.** The GitHub organization izborni-podaci was renamed javni-uvid.
  The repository's link (config's `REPO_URL`, shown on every page and in the user agent RIK and the geocoder see),
  the remote and the notes now name javni-uvid/izborna-analiza; GitHub redirects the old links meanwhile. The
  domain's `www` CNAME has to point to javni-uvid.github.io.
- **20 Nov 2026, a branch and a pull request per task** (the maintainer's decision, replacing the rule of 2 Nov):
  several agents work at once, each in its own Orca worktree, as in javni-uvid/zailiprotiv. `orca.yaml`,
  `tools/posalji.sh`, `tools/hooks/pre-push`, the pull request's template and Dependabot came from there; the
  repository allows only squash merges and deletes merged branches, and its ruleset `main` forbids deleting `main`
  and force-pushes. The **test** workflow keeps no token in its checkout and a newer run on the same branch cancels
  an older one. See *How to work here*.
- **20 Nov 2026, AGENTS.md split** (the maintainer's decision, as zailiprotiv did the same day): AGENTS.md keeps
  the rules of work, the principles, the map of the decisions and the known issues (9 KB); the architecture
  decisions and the decisions log moved word for word to `docs/decisions/` by part (data, boards, site, local,
  code, log), each section to its part's file and each dated entry to the part it is mostly about, in the order
  it had. An entry that spans parts stays whole in the part of its main subject.
