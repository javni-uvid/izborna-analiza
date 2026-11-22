"""What Google Search showed of izbornipodaci.rs: the searches it came up for, its pages, clicks and positions.

Ported from javni-uvid/zailiprotiv's `tools/search.py` (22 Nov 2026). Asked of the Search Console API by the
**visits** workflow (search=true), with a Google service account's key in the repository secret GSC_KEY (the account
added as a user of the Search Console property; "Restricted", which only reads, is enough). Only sums; a search or a
page seen fewer than three times is left out, as the run's log is public. Search Console's numbers come two to three
days late, and a new property has none for its first days.

With --inspect N, also whether Google took the site's pages into its index: N addresses of each kind of page (the
kinds of `tools/vitals.py`: home, municipality or city, polling station, a round's pages, ...) in each script,
spread evenly over the sitemap, asked of the URL Inspection API (2,000 a day per property). What Google says of each
kind is summed; the pages are the site's own, public anyway.

    python3 tools/search.py DAYS [--inspect N]"""
import json
import os
import re
import sys
import urllib.request
from collections import Counter
from datetime import date, timedelta

from vitals import kind as path_kind

PROPERTY = "sc-domain:izbornipodaci.rs"  # the Domain property: the apex and www together
SITE = "https://izbornipodaci.rs/"
LEAST = 3


def session():
    """An authorised session for the Search Console API, or None (and why) when the key is missing or not one."""
    key = os.environ.get("GSC_KEY", "").strip()
    if not key:
        print("::notice::Search Console not read: no key (repository secret GSC_KEY); see tools/search.py.")
        return None
    try:
        info = json.loads(key)
    except ValueError:
        print("::warning::Search Console not read: GSC_KEY is not a JSON key; set it to the whole service account "
              "key file.")
        return None
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    return AuthorizedSession(creds)


def kind(address: str) -> str:
    """The kind of page an address of the site is, and its script: "municipality or city (cyr)"."""
    return path_kind(address[len(SITE):] if address.startswith(SITE) else address)


def sample(addresses: list[str], n: int) -> dict[str, list[str]]:
    """N addresses of each kind, spread evenly over its list (the same ones each time, while the sitemap is)."""
    by_kind: dict[str, list[str]] = {}
    for a in sorted(addresses):
        by_kind.setdefault(kind(a), []).append(a)
    return {k: [v[i * len(v) // n] for i in range(n)] if len(v) > n else v for k, v in sorted(by_kind.items())}


def fetch(url: str) -> str:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "izborna-analiza visits"}),
                                timeout=60) as r:
        return r.read().decode("utf-8")


def sitemap() -> list[str]:
    """Every address in the site's sitemap: the index, then each of its parts."""
    addresses = []
    for part in re.findall(r"<loc>([^<]+)</loc>", fetch(SITE + "sitemap.xml")):
        if part.startswith(SITE):
            addresses += re.findall(r"<loc>([^<]+)</loc>", fetch(part))
    return [a.replace("&amp;", "&") for a in addresses if a.startswith(SITE)]


def inspect(http, n: int) -> None:
    """Whether Google indexed a sample of each kind of page, and the canonical address it chose for it."""
    addresses = sitemap()
    picked = sample(addresses, n)
    print(f"\nIndexed? {sum(map(len, picked.values()))} of the sitemap's {len(addresses)} pages, up to {n} of each kind "
          "(URL Inspection; the state as Google last saw it)")
    url = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"

    def ask(page: str):
        """Google's answer for one address; None when it gave none twice."""
        import requests
        for _ in range(2):
            try:
                return http.post(url, json={"inspectionUrl": page, "siteUrl": PROPERTY}, timeout=60)
            except requests.RequestException as e:
                print(f"    {page}: {type(e).__name__}", flush=True)
        return None

    from concurrent.futures import ThreadPoolExecutor
    pool = ThreadPoolExecutor(4)  # each answer takes some 5 s; four at once stay far under 600 a minute
    for k, pages in picked.items():
        states, other_canonical, never = Counter(), [], 0
        for page, r in zip(pages, pool.map(ask, pages)):
            if r is None:
                states["(no answer)"] += 1
                continue
            if r.status_code != 200:
                print(f"  Search Console answered {r.status_code}: {r.text[:300]}")
                return
            s = r.json().get("inspectionResult", {}).get("indexStatusResult", {})
            states[s.get("coverageState", "?")] += 1
            never += not s.get("lastCrawlTime")
            if s.get("googleCanonical") and s.get("googleCanonical") != page:
                other_canonical.append(f"{page} → {s['googleCanonical']}")
        print(f"\n  {k}  ({len(pages)} asked; never crawled: {never})", flush=True)
        for state, c in states.most_common():
            print(f"    {c:>3}  {state}")
        for line in other_canonical[:3]:
            print(f"    Google's canonical is another page: {line}")


def main(days: int, n_inspect: int = 0) -> None:
    http = session()
    if http is None:
        return
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=days - 1)
    url = f"https://searchconsole.googleapis.com/webmasters/v3/sites/{PROPERTY.replace(':', '%3A')}/searchAnalytics/query"

    def ask(dims: list[str], limit: int = 50, kind: str = "web") -> list[dict]:
        r = http.post(url, json={"startDate": start.isoformat(), "endDate": end.isoformat(), "dimensions": dims,
                                 "rowLimit": limit, "type": kind}, timeout=60)
        if r.status_code != 200:
            print(f"  Search Console answered {r.status_code}: {r.text[:300]}")
            return []
        return r.json().get("rows", [])

    print(f"Google Search, {start} to {end} (searches and pages seen fewer than {LEAST} times left out)")
    total = ask([], 1)
    if total:
        t = total[0]
        print(f"  {t['impressions']:.0f} times shown, {t['clicks']:.0f} clicks, average position {t['position']:.1f}")
    else:
        print("  nothing yet (a new property has no data for its first days)")
    for title, dims, limit in (("Searches", ["query"], 60), ("Pages", ["page"], 40), ("Devices", ["device"], 5),
                               ("Countries", ["country"], 10), ("By day", ["date"], days + 1)):
        rows = ask(dims, limit)
        print(f"\n{title}  (shown / clicks / position)")
        for r in sorted(rows, key=lambda r: r["keys"][0]) if dims == ["date"] else rows:
            if r["impressions"] >= LEAST:
                print(f"  {r['impressions']:>6.0f} {r['clicks']:>5.0f} {r['position']:>6.1f}  {r['keys'][0]}")
    # the pages summed by kind, so that a kind whose pages are each seen seldom still shows
    by_kind: dict[str, list[float]] = {}
    for r in ask(["page"], 5000):
        s = by_kind.setdefault(kind(r["keys"][0]), [0, 0])
        s[0] += r["impressions"]
        s[1] += r["clicks"]
    print("\nPages by kind  (shown / clicks)")
    for k, (shown, clicks) in sorted(by_kind.items(), key=lambda x: -x[1][0]):
        if shown >= LEAST:
            print(f"  {shown:>6.0f} {clicks:>5.0f}  {k}")
    if n_inspect:
        inspect(http, n_inspect)


if __name__ == "__main__":
    args = sys.argv[1:]
    n = int(args[args.index("--inspect") + 1]) if "--inspect" in args else 0
    days = [a for i, a in enumerate(args) if a != "--inspect" and (i == 0 or args[i - 1] != "--inspect")]
    main(int(days[0]) if days else 28, n)
