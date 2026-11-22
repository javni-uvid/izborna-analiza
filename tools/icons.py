"""Draw the site's mark into its files (22 Nov 2026, the maintainer's choice of three drafts: a ballot box with a
gold slip going in). Run by hand when the mark changes, and commit what it writes:

    uv run --with playwright==1.56.0 --with pillow==12.0.0 python tools/icons.py

src/izbori/root/ (copied to the site's root by the build): favicon.svg (navy, its own colours in a dark scheme),
favicon.ico (16, 32, 48) and favicon-96.png (Google shows no SVG), apple-touch-icon.png (180, opaque), logo.png
(512, schema.org's Organization), og-image.png (1200×630, the picture a shared link shows).
src/izbori/static/: brand-mark.svg and brand-mark-dark.svg, the header's mark (white box, the theme's gold).
"""
import base64
import io
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT, STATIC = ROOT / "src/izbori/root", ROOT / "src/izbori/static"
FONTS = ROOT / "osnova/design/fonts"
SLIP = '<rect class="b" x="10.5" y="3" width="11" height="13" rx="1"/>'
BOX = '<path class="a" d="M4 13h9v3h6v-3h9v14.5a1.5 1.5 0 0 1-1.5 1.5h-21A1.5 1.5 0 0 1 4 27.5z"/>'
NAVY, GOLD, NIGHT, NIGHT_GOLD, LIGHT_INK = "#1e3a5f", "#c9971c", "#142a47", "#e4b94a", "#e8eef6"


def svg(a: str, b: str, extra: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><style>.a{{fill:{a}}}.b{{fill:{b}}}{extra}'
            f'</style>{SLIP}{BOX}</svg>\n')


def tile(bg: str) -> str:
    """The mark on a navy square with round corners, for the files that can't follow the reader's scheme."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="{bg}" '
            f'fill="{NAVY}"/><g transform="translate(4.8 4.8) scale(.7)"><style>.a{{fill:#fff}}.b{{fill:{NIGHT_GOLD}}}'
            f'</style>{SLIP}{BOX}</g></svg>')


def main() -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / "favicon.svg").write_text(svg(NAVY, GOLD, f"@media (prefers-color-scheme:dark){{.a{{fill:{LIGHT_INK}}}.b{{fill:{NIGHT_GOLD}}}}}"), encoding="utf-8", newline="\n")
    (STATIC / "brand-mark.svg").write_text(svg("#fff", GOLD), encoding="utf-8", newline="\n")
    (STATIC / "brand-mark-dark.svg").write_text(svg("#fff", NIGHT_GOLD), encoding="utf-8", newline="\n")
    font = "".join(f"@font-face{{font-family:Literata;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode((FONTS / n).read_bytes()).decode()}) format('woff2');font-weight:200 900}}"
                   for n in ("literata-latin-wght-normal.woff2", "literata-latin-ext-wght-normal.woff2"))
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")

        def shot(html: str, w: int, h: int, transparent: bool = False) -> Image.Image:
            page = browser.new_page(viewport={"width": w, "height": h})
            page.set_content(f"<html><body style='margin:0'>{html}</body></html>")
            page.wait_for_timeout(300)
            png = page.screenshot(omit_background=transparent)
            page.close()
            return Image.open(io.BytesIO(png)).convert("RGBA")

        def icon(px: int, radius: str = "6", transparent: bool = True) -> Image.Image:
            return shot(f'<div style="width:{px}px;height:{px}px">{tile(radius).replace("<svg ", f"<svg width=\"{px}\" height=\"{px}\" ")}</div>', px, px, transparent)

        def save(img: Image.Image, name: str, opaque: bool = False) -> None:
            img = img.convert("RGB") if opaque else img
            img.save(OUT / name, optimize=True)

        save(icon(96), "favicon-96.png")
        save(icon(180, "0", False), "apple-touch-icon.png", opaque=True)
        save(icon(512, "0", False), "logo.png", opaque=True)
        icon(48).save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
        mark = svg("#fff", NIGHT_GOLD).replace("<svg ", '<svg width="150" height="150" ')
        og = (f"<style>{font}</style><div style='width:1200px;height:630px;box-sizing:border-box;background:{NAVY};"
              f"border-bottom:12px solid {GOLD};color:#fff;display:flex;flex-direction:column;justify-content:center;"
              f"padding:0 96px;font-family:system-ui,sans-serif'><div style='display:flex;align-items:center;gap:36px'>"
              f"{mark}<div style='font:700 104px/1 Literata,Georgia,serif;letter-spacing:-1px'>Izborni podaci</div></div>"
              f"<div style='margin-top:44px;font-size:36px;line-height:1.35;color:#c5d2e2;max-width:960px'>Svako biračko "
              f"mesto u Srbiji, kroz sve izbore od 2022, iz onoga što objavljuje Republička izborna komisija.</div></div>")
        save(shot(og, 1200, 630), "og-image.png", opaque=True)
        browser.close()
    for f in sorted(OUT.iterdir()):
        print(f.name, f.stat().st_size)


if __name__ == "__main__":
    main()
