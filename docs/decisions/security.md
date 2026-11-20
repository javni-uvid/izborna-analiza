# Security

What this project guards besides the organization's rules (`osnova/security.md`), and what it accepts as it is
(20 Nov 2026, when the shared rules came from javni-uvid/osnova). **Keep it current:** a decision made or changed
is added here, at the end of the section it belongs to, in the same commit as the change.

## What it guards besides

- **No person's name, anywhere** (principle 4): not in the archive, the pages, the logs or CI's output. Public
  CI logs show OCR's layouts with every word not printed on the form masked; whatever is parsed from a document
  and could hold a name is checked before it is kept.
- **The observer target list stays private** (principle 6): never committed, never built in GitHub Actions,
  whose build outputs anyone with an account can download.
- **The archive is what RIK published:** the workflows commit RIK's files as downloaded, so `main`'s history is
  the record. A task that changes `data/` by hand says why in its pull request.

## Accepted as it is

- **No security headers from the host.** izbornipodaci.rs points straight at GitHub Pages (DNS at Loopia), with
  no Cloudflare in front, so the headers `osnova/security.md` sets at Cloudflare aren't sent; GitHub Pages
  serves HTTPS only. They come with Cloudflare, if it is put in front (*Hosting* in `site.md`).
- **`artipacked` for the workflows that push** (boards, census, documents, geo, history, local, observers,
  stations, update, watch): their checkout keeps the token to commit; `.github/zizmor.yml` lists them.
- **OCR's system packages by name, not version** (tesseract with its Serbian data, poppler, antiword, from the
  runner's Ubuntu archive): the runner's image fixes them, and a version from another archive would differ from
  what the OCR was tuned on. Python tools are named by version (`uv==…`, the `--with` packages); Dependabot
  doesn't move those, so they are raised by hand.

## Decisions log

- **20 Nov 2026, matched to osnova.** `uv` and the packages a step adds with `--with` (numpy, OpenCV,
  scikit-learn, shapely, pyshp) are named by version, the versions those steps had been resolving to. CodeQL's
  four open findings were closed in the code: the two addresses `site.js` builds from the page's own values are
  used only as plain relative paths (`relPath`), Explore draws a view only when the address names one of its own,
  and a character class in `cli.py` lost a range the next one already held (the same letters). The repository's
  settings are not yet `osnova/security.md`'s: all actions are allowed (not only GitHub's, by commit), and
  secret scanning with push protection, Dependabot's security updates and private vulnerability reporting are
  off. They are the maintainer's to switch on (an agent's attempt was refused by its permissions).
