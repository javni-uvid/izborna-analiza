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
