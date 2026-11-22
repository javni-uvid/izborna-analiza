"""The family's look and links (Javni uvid): what this site takes from `osnova/design/`, the copy of
javni-uvid/osnova's `shared/design/` (22 Nov 2026, as zailiprotiv's).

`osnova.css` (the font, the base colours, the scale of sizes, the bar and the footer block) and the fonts are
copied into `static/` by the build, and every page loads it before `site.css`, which takes its base colours, fonts
and sizes from the `--ju-*` values. The bar and the footer block are written here from `sites.json`, the same
markup on every site of the family (`osnova/design/family.html`), in the page's own script: the pages are rendered
once per script, so a Cyrillic page links the other sites' Cyrillic editions."""

from __future__ import annotations

import html
import json
from functools import cache
from pathlib import Path

DESIGN = Path(__file__).resolve().parents[2] / "osnova" / "design"
ME = "izborni-podaci"  # this site's id in sites.json
# The family's mark (family.html draws it as an inline SVG): here a span that site.css draws the same, a square's
# outline and a dot in the text's colour, since an SVG twice on each of some 20,000 pages would cost 9 MB.
MARK = '<span class="ju-mark" aria-hidden="true"></span>'


def files() -> list[Path]:
    """What the build takes from osnova/design (and what the code's version counts)."""
    return [DESIGN / "osnova.css", DESIGN / "sites.json", *sorted((DESIGN / "fonts").iterdir())]


@cache
def sites() -> dict:
    return json.loads((DESIGN / "sites.json").read_text(encoding="utf-8"))


def _script(loc: str) -> str:
    return "cyr" if loc == "cyr" else "lat"


def _a(target: dict, script: str, home: str, text: str, attrs: str = "") -> str:
    href = home if target.get("id") == ME else target["url"][script]
    return f'<a{attrs} href="{html.escape(href)}">{text}</a>'


def bar(loc: str, home: str) -> str:
    """The family's bar, first in the page after the skip link: the family's name, then its sites, this one
    marked. `home` is this site's first page as seen from the page the bar is on."""
    script = _script(loc)
    data = sites()
    fam = data["family"]
    name = html.escape(fam["name"][script])
    links = "".join(
        "\n    " + _a(s, script, home, html.escape(s["name"][script]), ' aria-current="page"' if s["id"] == ME else "")
        for s in data["sites"]
    )
    return (
        f'<nav class="ju-bar" aria-label="{name}">\n  <div class="ju-bar-in">\n'
        f'    {_a(fam, script, home, MARK + name, " class=\"ju-name\"")}{links}\n  </div>\n</nav>'
    )


def foot(loc: str, home: str) -> str:
    """The family's block, last in the footer: what the family promises, and its sites with a line on each."""
    script = _script(loc)
    data = sites()
    fam = data["family"]
    name = html.escape(fam["name"][script])
    items = "".join(
        f'\n    <li>{_a(s, script, home, html.escape(s["name"][script]))}<span>{html.escape(s["about"][script])}</span></li>'
        for s in data["sites"]
    )
    principles = {"url": {k: v + "#nacela" for k, v in fam["url"].items()}}
    return (
        f'<section class="ju-foot" aria-label="{name}">\n  <h2>{_a(fam, script, home, MARK + name)}</h2>\n'
        f'  <p>{html.escape(fam["promise"][script])} {_a(principles, script, home, html.escape(fam["principles"][script]))}</p>\n'
        f"  <ul>{items}\n  </ul>\n</section>"
    )
