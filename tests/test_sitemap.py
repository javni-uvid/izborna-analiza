"""The sitemap's parts, without building a site (runs on Windows too)."""

import xml.etree.ElementTree as ET

from izbori import site as S


def test_sitemap_splits_into_parts_and_leaves_out_what_isnt_a_page(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "SITEMAP_PART", 2)
    s = S.Site.__new__(S.Site)
    s.out, s.site_url, s.rendered = tmp_path, "https://izbornipodaci.rs/", 0
    s.produced = {"index.html", "cyr/index.html", "about.html", "zemun/index.html", "m/1.html", "404.html",
                  "static/site.css", "static/x.html", "feed.sr.xml", "search.json", "a&b.html"}
    s.redirects = {"m/1.html"}
    s.write_sitemap()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    parts = [l.text for l in ET.parse(tmp_path / "sitemap.xml").getroot().findall("s:sitemap/s:loc", ns)]
    assert parts == [f"https://izbornipodaci.rs/sitemap-{n}.xml" for n in (1, 2, 3)]
    urls = [u.text for n in (1, 2, 3) for u in ET.parse(tmp_path / f"sitemap-{n}.xml").getroot().findall("s:url/s:loc", ns)]
    assert urls == ["https://izbornipodaci.rs/a&b.html", "https://izbornipodaci.rs/about.html",
                    "https://izbornipodaci.rs/cyr/", "https://izbornipodaci.rs/", "https://izbornipodaci.rs/zemun/"]
    assert "a&amp;b.html" in (tmp_path / "sitemap-1.xml").read_text(encoding="utf-8")
    robots = (tmp_path / "robots.txt").read_text(encoding="utf-8")
    assert robots == "User-agent: *\nAllow: /\n\nSitemap: https://izbornipodaci.rs/sitemap.xml\n"
    assert "Disallow" not in robots  # every crawler is welcome, AI ones too (22 Nov 2026)
