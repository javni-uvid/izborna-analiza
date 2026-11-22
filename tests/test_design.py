"""The stylesheet keeps to the design rules (docs/decisions/site.md, "Design rules")."""

import re
from pathlib import Path

import izbori

CSS = (Path(izbori.__file__).parent / "static" / "site.css").read_text(encoding="utf-8")
# the family's stylesheet, loaded before site.css, which takes its base colours, fonts and sizes (22 Nov 2026)
OSNOVA = (Path(izbori.__file__).parents[2] / "osnova" / "design" / "osnova.css").read_text(encoding="utf-8")


def test_letter_sizes_are_the_scale():
    """Every letter size is a step of the one scale (the --t- variables, as in zailiprotiv), so the site does not
    grow 36 sizes again. The exceptions: an SVG's labels in px, sizes relative to the parent, and 0 for the
    menu's short names (their text comes from ::after)."""
    sizes = {v.strip() for v in re.findall(r"font-size:\s*([^;}]+)", CSS)}
    allowed = {"inherit", "0", "0.8em", "0.85em", "9px", "10px", "11px", "12px"}
    assert {v for v in sizes if not re.fullmatch(r"var\(--t-(\d|h1|d1)\)", v)} <= allowed
    # nor can the shorthand slip a size past it: the body's 16 px and the map's SVG labels only
    assert set(re.findall(r"font:\s*([\d.]+(?:rem|px))", CSS)) <= {"16px", "11px"}
    steps = dict(re.findall(r"--t-(\w+):\s*([^;]+);", CSS))
    family = dict(re.findall(r"--ju-t-(\w+):\s*([^;]+);", OSNOVA))
    assert all(steps[k] == f"var(--ju-t-{k})" for k in family)  # the family's scale, every step of it
    assert family["3"] == "1rem"  # body text is 16 px
    assert "font: 16px/1.55" in CSS


def _tokens(block: str, family: dict[str, str] | None = None) -> dict[str, str]:
    """A block's colours; a value taken from the family's (var(--ju-…)) is read from osnova.css's `family`."""
    found = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6}|var\(--ju-[\w-]+\))", block))
    return {k: (family or {})[v[6:-1]] if v.startswith("var(") else v for k, v in found.items()
            if not v.startswith("var(") or v[6:-1] in (family or {})}  # sizes and fonts aren't colours


def _family(block: str) -> dict[str, str]:
    return dict(re.findall(r"--(ju-[\w-]+):\s*(#[0-9a-fA-F]{6})", block))


def _contrast(a: str, b: str) -> float:
    def lum(h: str) -> float:
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_text_and_controls_have_contrast_in_both_themes():
    """WCAG 2.2 AA, from the tokens themselves: text 4.5:1 on the page and on the grey cards, a form control's
    edge 3:1, in the light theme and in both ways the dark one is chosen (the menu's toggle and the system's)."""
    fam_light = _family(OSNOVA[OSNOVA.index(":root {"):OSNOVA.index("@media (prefers-color-scheme: dark)")])
    fam_dark = _family(OSNOVA[OSNOVA.index(":root[data-theme=\"dark\"]"):])
    assert fam_dark == _family(OSNOVA[OSNOVA.index("@media (prefers-color-scheme: dark)"):OSNOVA.index(":root[data-theme=\"dark\"]")])
    root = CSS[CSS.index(":root {"):CSS.index(":root[data-theme=\"dark\"]")]
    light = _tokens(root, fam_light)
    dark = _tokens(root, fam_dark) | _tokens(CSS[CSS.index(":root[data-theme=\"dark\"]"):CSS.index("@media (prefers-color-scheme: dark)")])
    system = _tokens(root, fam_dark) | _tokens(CSS[CSS.index("@media (prefers-color-scheme: dark)"):CSS.index("* { box-sizing")])
    assert dark == system  # the two ways to the dark theme give the same colours
    # this site's own colours, not the family's (22 Nov 2026, the maintainer's decision): the navy of 8 Nov 2026
    assert (light["page"], light["ink"], light["brand"], dark["page"]) == ("#ffffff", "#0f1f33", "#1e3a5f", "#0b1526")
    text = [("ink", "page"), ("ink", "surface"), ("ink-2", "page"), ("ink-2", "surface"), ("link", "page"),
            ("critical", "page"), ("critical", "surface"), ("ink", "warn-track"), ("on-button", "button"),
            ("on-brand", "brand"), ("brick-accent", "brick"), ("sun", "ink-card"), ("accent", "page")]
    for name, t in (("light", light), ("dark", dark)):
        for fg, bg in text:
            assert _contrast(t[fg], t[bg]) >= 4.5, (name, fg, bg, round(_contrast(t[fg], t[bg]), 2))
        for g in ("serious", "warning", "records"):  # a check's colour beside its name, read as text
            assert _contrast(t[g], t["page"]) >= 3, (name, g)
        assert _contrast(t["ink-2"], t["page"]) >= 3  # a form control's edge


def test_keyboard_and_motion():
    """The keyboard's place shows on every page, the first Tab skips to the page itself, and nothing moves for a
    reader who asked for less motion."""
    assert re.search(r":focus-visible\s*\{\s*outline:\s*3px solid var\(--ink\)", CSS)
    assert "@media (prefers-reduced-motion: reduce)" in CSS
    base = (Path(izbori.__file__).parent / "templates" / "base.html").read_text(encoding="utf-8")
    assert '<a class="skip" href="#main">' in base and '<main class="wrap" id="main"' in base


def test_fonts_are_served_from_the_site():
    """Principle 5: the stylesheets name no other host, and every font file they name is in static/fonts with
    its licence."""
    fonts = Path(izbori.__file__).parents[2] / "osnova" / "design" / "fonts"  # copied into static/fonts
    assert "http" not in OSNOVA + CSS.replace("http://www.w3.org/2000/svg", "")
    for name in re.findall(r"url\(fonts/([^)]+)\)", OSNOVA):
        assert (fonts / name).exists(), name
    assert (fonts / "OFL-Literata.txt").exists()


BEACON = "https://static.cloudflareinsights.com/beacon.min.js"


def test_analytics_script(monkeypatch, tmp_path):
    """Cloudflare Web Analytics (22 Nov 2026, the maintainer's exception to principle 5): with a token every page
    loads its script, the only one from another server, and the footer, the home page and the about page say that
    visits are counted; without one there is no trace of it."""
    from izbori import config
    from izbori.history import Archive
    from izbori.site import Site

    def render(token: str) -> dict[str, str]:
        monkeypatch.setattr(config, "ANALYTICS_TOKEN", token)
        site = Site(Archive(tmp_path / "data"), tmp_path / token, None, "https://example.org/x/")
        pages = {}
        for loc in ("lat", "cyr"):
            site.write(loc, "about.html", "about.html")
            prefix = "" if loc == "lat" else "cyr/"
            pages[loc] = (tmp_path / token / prefix / "about.html").read_text(encoding="utf-8")
        return pages

    for loc, page in render("").items():
        assert "cloudflareinsights" not in page and "Cloudflare" not in page, loc
        assert not re.search(r'<(script|link|img)[^>]+(src|href)="https?://', page), loc
    for loc, page in render("abc123").items():
        outside = re.findall(r'<(?:script|link|img)[^>]+(?:src|href)="(https?://[^"]+)"', page)
        assert outside == [BEACON], loc
        assert """data-cf-beacon='{"token": "abc123"}'""" in page, loc
        assert page.count("Cloudflare Web Analytics") == 2, loc  # the footer and the principle


def test_family_bar_and_footer(tmp_path):
    """Javni uvid's bar (22 Nov 2026, as zailiprotiv's): right after the skip link on every page, the family's name
    leading to its page and every site of the family, this one marked as the current one and leading home; the
    footer ends with the family's block. A Cyrillic page names them in Cyrillic and links the Cyrillic editions."""
    import json

    from izbori.history import Archive
    from izbori.site import Site

    fam = json.loads((Path(izbori.__file__).parents[2] / "osnova" / "design" / "sites.json").read_text(encoding="utf-8"))
    site = Site(Archive(tmp_path / "data"), tmp_path / "out", None, "https://example.org/x/")
    for loc, prefix, home in (("lat", "", "index.html"), ("cyr", "cyr/", "../cyr/index.html")):
        site.write(loc, "about.html", "about.html")
        page = (tmp_path / "out" / prefix / "about.html").read_text(encoding="utf-8")
        body = page[page.index("<body>"):]
        assert body.index('<a class="skip"') < body.index('<nav class="ju-bar"') < body.index('<header class="top">'), loc
        bar = body[body.index('<nav class="ju-bar"'):body.index("</nav>")]
        assert f'aria-label="{fam["family"]["name"][loc]}"' in bar, loc
        assert f'<a class="ju-name" href="{fam["family"]["url"][loc]}">' in bar, loc
        for s in fam["sites"]:
            if s["id"] == "izborni-podaci":
                assert f'<a aria-current="page" href="{home}">{s["name"][loc]}</a>' in bar, loc
            else:
                assert f'<a href="{s["url"][loc]}">{s["name"][loc]}</a>' in bar, loc
        foot = page[page.index('<section class="ju-foot"'):]
        assert foot.index("</section>") < foot.index("</footer>"), loc
        assert fam["family"]["promise"][loc] in foot and f'{fam["family"]["url"][loc]}#nacela' in foot, loc
        assert "<svg" not in bar and "<svg" not in foot[:foot.index("</section>")], loc  # the mark is drawn by CSS
        assert '<link rel="stylesheet" href="' in page and "static/osnova.css" in page, loc


def test_the_mark_and_the_icons(tmp_path):
    """The site's mark (22 Nov 2026, the maintainer's choice of three drafts): left of the name in the header,
    decorative (the link's name stays the site's), drawn by the stylesheet; every page links the favicon set and the
    picture a shared link shows, whose files the build puts at the root."""
    from izbori.history import Archive
    from izbori.site import HERE, Site

    site = Site(Archive(tmp_path / "data"), tmp_path / "out", None, "https://example.org/x/")
    for loc, prefix, name in (("lat", "", "Izborni podaci"), ("cyr", "cyr/", "Изборни подаци")):
        site.write(loc, "about.html", "about.html")
        page = (tmp_path / "out" / prefix / "about.html").read_text(encoding="utf-8")
        brand = re.search(r'<a class="brand" href="[^"]+">(.*?)</a>', page).group(1)
        assert brand == f'<span class="brand-mark" aria-hidden="true"></span>{name}', loc
        up = "../" if prefix else ""
        for tag in (f'<link rel="icon" type="image/svg+xml" href="{up}favicon.svg">',
                    f'<link rel="icon" type="image/png" sizes="96x96" href="{up}favicon-96.png">',
                    f'<link rel="apple-touch-icon" href="{up}apple-touch-icon.png">',
                    '<meta property="og:image" content="https://example.org/x/og-image.png">'):
            assert tag in page, (loc, tag)
    for f in ("favicon.svg", "favicon.ico", "favicon-96.png", "apple-touch-icon.png", "logo.png", "og-image.png"):
        assert (HERE / "root" / f).stat().st_size < 50_000, f  # small: a favicon is asked for on every visit
    assert re.search(r"\.brand-mark \{[^}]*url\(brand-mark\.svg\)", CSS) and "url(brand-mark-dark.svg)" in CSS
    assert (HERE / "static" / "brand-mark.svg").exists() and (HERE / "static" / "brand-mark-dark.svg").exists()
