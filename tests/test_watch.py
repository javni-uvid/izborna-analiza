"""The weekly look at the municipalities' sites: which links are kept, which pages followed; nothing of a
document's text or title is kept."""
from izbori import watch


def family_list(monkeypatch, tmp_path, text, encoding="utf-8"):
    """The family's list of municipalities (osnova/data/municipalities.csv) for a test."""
    path = tmp_path / "municipalities.csv"
    path.write_text(text, encoding=encoding)
    monkeypatch.setattr(watch, "SITES", path)



def test_kind_of_links():
    assert watch.kind_of("Одлука о одређивању бирачких места за изборе 25.10.2026 odluka.pdf") == "stations"
    assert watch.kind_of("Rešenje o utvrđivanju biračkih mesta") == "stations"
    assert watch.kind_of("Решење о именовању чланова бирачких одбора у сталном саставу БМ 3") == "boards"
    assert watch.kind_of("Пословник Општинске изборне комисије") == "commission"
    assert watch.kind_of("Јавни позив за легализацију објеката") is None
    assert watch.kind_of("Бирачка места – обавештење") is None  # about stations but no act
    assert watch.kind_of("Извештај о укупним резултатима избора за одборнике Скупштине града") == "results"
    assert watch.kind_of("Збирна изборна листа кандидата за одборнике") == "lists"
    assert watch.kind_of("Резултати такмичења") is None


def test_crawl_follows_election_pages_and_keeps_documents(tmp_path, monkeypatch):
    pages = {
        "https://primer.rs/": '<a href="/izbori-2026/">Избори 2026</a> <a href="/vesti/">Вести</a> '
                              '<a href="https://drugi.rs/odluka-biracka-mesta.pdf">Одлука о одређивању бирачких места</a>',
        "https://primer.rs/izbori-2026/": '<a href="/files/Odluka%20o%20odredjivanju%20birackih%20mesta.pdf">Одлука</a> '
                                          '<a href="/files/resenje-bo-bm-12.pdf">Решење о именовању бирачког одбора БМ 12</a> '
                                          '<a href="/files/budzet.pdf">Буџет</a>',
        "https://primer.rs/vesti/": '<a href="/files/resenje-bo-bm-13.pdf">Решење о именовању бирачког одбора БМ 13</a>',
    }
    asked = []

    def fetcher(url):
        asked.append(url)
        if url.startswith("https://primer.rs/?s="):
            return '<a href="/files/odluka-bm-2023.docx">Одлука о бирачким местима 2023</a>'
        return pages.get(url, "")

    found = watch.crawl("primer.rs", fetcher=fetcher, sleep=lambda s: None)
    assert found == {"https://primer.rs/files/Odluka%20o%20odredjivanju%20birackih%20mesta.pdf": "stations",
                     "https://primer.rs/files/resenje-bo-bm-12.pdf": "boards",
                     "https://primer.rs/files/odluka-bm-2023.docx": "stations"}  # another site's file and the news page are not followed
    assert "https://primer.rs/vesti/" not in asked and "https://primer.rs/izbori-2026/" in asked
    family_list(monkeypatch, tmp_path, "municipality_code,name,domain,note\n70017,Пример,primer.rs,\n70025,Други,,webmail\n",
                                                 encoding="utf-8")
    logged = []
    assert watch.run(tmp_path, "2026-11-08", logged.append, fetcher, lambda s: None) == 3
    store = watch.load_store(tmp_path)
    assert all(set(v) == {"m", "k", "seen"} for v in store["docs"].values())  # no titles, no text
    assert any("candidate for station_lists.csv" in m for m in logged)
    assert watch.run(tmp_path, "2026-11-09", logged.append, fetcher, lambda s: None) == 0  # nothing new the next time


def test_crawl_reads_wordpress_uploads_and_sitemaps():
    pages = {
        "https://primer.rs/": "<p>почетна</p>",
        "https://primer.rs/sitemap.xml": "<sitemapindex><sitemap><loc>https://primer.rs/page-sitemap.xml</loc></sitemap></sitemapindex>",
        "https://primer.rs/page-sitemap.xml": "<urlset><url><loc>https://primer.rs/izborna-komisija/</loc></url>"
                                              "<url><loc>https://primer.rs/files/odluka-o-odredjivanju-birackih-mesta.pdf</loc></url>"
                                              "<url><loc>https://primer.rs/turizam/</loc></url></urlset>",
        "https://primer.rs/izborna-komisija/": '<a href="/files/resenje-bo-bm-4.pdf">Решење о именовању бирачког одбора</a>',
    }
    asked = []

    def fetcher(url):
        asked.append(url)
        if "wp-json/wp/v2/media" in url and "search=%D0%B1%D0%B8%D1%80%D0%B0%D1%87%D0%BA" in url:
            return ('[{"source_url": "https://primer.rs/wp-content/uploads/2026/09/BM.pdf",'
                    ' "title": {"rendered": "Решење о утврђивању бирачких места"}},'
                    ' {"source_url": "https://drugi.rs/x.pdf", "title": {"rendered": "Решење о утврђивању бирачких места"}}]')
        if "wp-json" in url:
            return "[]"
        if url in pages:
            return pages[url]
        raise OSError("404")

    found = watch.crawl("primer.rs", fetcher=fetcher, sleep=lambda s: None)
    assert found == {"https://primer.rs/wp-content/uploads/2026/09/BM.pdf": "stations",
                     "https://primer.rs/files/odluka-o-odredjivanju-birackih-mesta.pdf": "stations",
                     "https://primer.rs/files/resenje-bo-bm-4.pdf": "boards"}
    assert "https://primer.rs/turizam/" not in asked


def test_why_says_what_failed():
    import urllib.error
    assert watch.why(urllib.error.URLError("timed out")) == "URLError timed out"
    assert watch.why(urllib.error.HTTPError("u", 403, "Forbidden", {}, None)).startswith("HTTPError Forbidden")


def test_a_broken_link_or_a_crash_does_not_stop_the_run(tmp_path, monkeypatch):
    assert watch.links_of('<a href="http://[broken/x.pdf">x</a><a href="/a.pdf">a</a>', "https://p.rs/") == [("https://p.rs/a.pdf", "a")]
    family_list(monkeypatch, tmp_path, 
        "municipality_code,name,domain,note\n70017,Први,prvi.rs,\n70025,Други,drugi.rs,\n", encoding="utf-8")

    def fetcher(url):
        if "prvi" in url:
            return '<a href="/izbori/">Избори</a>' if url.endswith("prvi.rs/") else 1 / 0
        return '<a href="/o.pdf">Одлука о одређивању бирачких места</a>'
    logged = []
    assert watch.run(tmp_path, "2026-11-09", logged.append, fetcher, lambda s: None) == 1


def test_crawl_starts_from_the_commission_s_own_page_and_its_subdomain():
    pages = {
        "https://primer.rs/": '<a href="/vesti/">Вести</a>',
        "https://skupstina.primer.rs/oik/akta/": '<a href="https://skupstina.primer.rs/f/resenje-bo-bm-3.pdf">'
                                                 'Решење о именовању бирачког одбора БМ 3</a>'
                                                 '<a href="https://primer.com/resenje-bo-bm-4.pdf">Решење о именовању бирачког одбора</a>',
    }
    found = watch.crawl("primer.rs", fetcher=lambda u: pages.get(u, ""), sleep=lambda s: None,
                        pages_of=("https://skupstina.primer.rs/oik/akta/",))
    assert found == {"https://skupstina.primer.rs/f/resenje-bo-bm-3.pdf": "boards"}  # not another site's
    assert watch.same_site("www.primer.rs", "primer.rs") and not watch.same_site("neprimer.rs", "primer.rs")


def test_a_document_on_the_site_s_file_host():
    pages = {"https://ub.rs/": '<a href="https://media.readycms.io/x/Odluka%20o%20birackim%20mestima.pdf">Одлука о '
                               'бирачким местима</a><a href="https://media.readycms.io/x/strana/">Страна</a>'}
    found = watch.crawl("ub.rs", fetcher=lambda u: pages.get(u, ""), sleep=lambda s: None)
    assert found == {"https://media.readycms.io/x/Odluka%20o%20birackim%20mestima.pdf": "stations"}  # its pages not followed


def test_the_family_list_and_the_commission_pages(tmp_path, monkeypatch):
    family_list(monkeypatch, tmp_path, "municipality_code,name,domain,note\n89010,Град Нови Сад,novisad.rs,\n"
                                       "70017,Пример,primer.rs,\n")
    (tmp_path / watch.PAGES_FILE).write_text("municipality_code,pages\n89010,https://skupstina.novisad.rs/gik-strana/\n",
                                             encoding="utf-8")
    sites = watch.load_sites(tmp_path)
    assert sites[0]["pages"] == "https://skupstina.novisad.rs/gik-strana/" and sites[1]["pages"] == ""
    assert watch.names() == {"89010": "Град Нови Сад", "70017": "Пример"}


def test_the_commission_pages_name_municipalities_of_the_family_list():
    from pathlib import Path
    data = Path(__file__).resolve().parents[1] / "data"
    codes = set(watch.names())
    assert len(codes) > 160  # osnova/data/municipalities.csv, the copy of javni-uvid/osnova's list
    assert {s["municipality_code"] for s in watch._rows(data / watch.PAGES_FILE)} <= codes
