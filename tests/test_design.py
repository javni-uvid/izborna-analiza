"""The stylesheet keeps to the design rules (docs/decisions/site.md, "Design rules")."""

import re
from pathlib import Path

import izbori

CSS = (Path(izbori.__file__).parent / "static" / "site.css").read_text(encoding="utf-8")


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
    assert steps["3"] == "1rem"  # body text is 16 px
    assert "font: 16px/1.55" in CSS


def _tokens(block: str) -> dict[str, str]:
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", block))


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
    light = _tokens(CSS[CSS.index(":root {"):CSS.index(":root[data-theme=\"dark\"]")])
    dark = _tokens(CSS[CSS.index(":root[data-theme=\"dark\"]"):CSS.index("@media (prefers-color-scheme: dark)")])
    system = _tokens(CSS[CSS.index("@media (prefers-color-scheme: dark)"):CSS.index("* { box-sizing")])
    assert dark == system  # the two ways to the dark theme give the same colours
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
    static = Path(izbori.__file__).parent / "static"
    fonts = (static / "fonts.css").read_text(encoding="utf-8")
    assert "http" not in fonts + CSS.replace("http://www.w3.org/2000/svg", "")
    for name in re.findall(r"url\(fonts/([^)]+)\)", fonts):
        assert (static / "fonts" / name).exists(), name
    assert (static / "fonts" / "OFL-Literata.txt").exists()
