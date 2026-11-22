"""How fast izbornipodaci.rs is for those who open it: Core Web Vitals as Cloudflare Web Analytics measured them.

LCP (when the largest thing on the first screen is drawn; good up to 2.5 s), INP (how long the page takes to answer
a tap; good up to 200 ms) and CLS (how much the page jumps while loading; good up to 0.1), each as the share of
measured page loads that were good, middling and poor: by device, and by kind of page (home, municipality or city,
polling station, a round's pages, Explore, the guide, ...) in Latin and Cyrillic, since the site has some 67,000
pages and one of them is seldom opened often enough to say. Google judges a page by the 75th percentile, so "good"
for three loads in four is the line to hold; for a kind under it the elements Cloudflare names are listed: which one
jumped (CLS), was drawn late (LCP) or answered late (INP).

Ported from javni-uvid/zailiprotiv's `tools/vitals.py` (22 Nov 2026). Asked of Cloudflare's GraphQL analytics by
the **visits** workflow, with the token that only reads the account's analytics, and only of this site's hosts.
Sums only, and a row measured fewer than twenty times is left out: the log is public, and a share of so few says
nothing. `schema` as the first argument prints the fields Cloudflare offers instead (they have changed before)."""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.cloudflare.com/client/v4/graphql"
DATASET = "rumWebVitalsEventsAdaptiveGroups"
HOSTS = ["izbornipodaci.rs", "www.izbornipodaci.rs"]
LEAST = 20
LINE = 0.75
PATHS = 2000  # the most measured pages asked for, to be summed by kind
METRICS = (("LCP", "lcp"), ("INP", "inp"), ("CLS", "cls"))
ELEMENT = {"lcp": "largestContentfulPaintElement", "inp": "interactionToNextPaintElement",
           "cls": "cumulativeLayoutShiftElement"}
SUMS = " ".join(f"{m}Good {m}NeedsImprovement {m}Poor {m}Total" for _, m in METRICS)
FIELDS = [f"{m}{part}" for _, m in METRICS for part in ("Good", "NeedsImprovement", "Poor", "Total")]
PAGES = {"index.html": "home", "explore.html": "Explore", "elections.html": "lists of elections and municipalities",
         "municipalities.html": "lists of elections and municipalities", "repeat.html": "places to watch",
         "about.html": "about", "404.html": "not found"}


def kind(path: str) -> str:
    """The kind of page a path is, and its script: "municipality or city (cyr)"."""
    script = "lat"
    path = path.lstrip("/")
    if path.startswith("cyr/"):
        script, path = "cyr", path[4:]
    if path in ("", "index.html"):
        what = "home"
    elif path in PAGES:
        what = PAGES[path]
    elif path.startswith("guide."):
        what = "guide"
    elif path.startswith("r/"):
        what = "a round's pages"
    elif path.startswith("s/"):
        what = "polling place"
    elif re.fullmatch(r"[a-z0-9-]+/?", path):
        what = "municipality or city"
    elif re.fullmatch(r"[a-z0-9-]+/\d+[^/]*/?", path):
        what = "polling station across elections"
    else:
        what = "other"
    return f"{what} ({script})"


def post(query: str, variables: dict | None = None) -> dict:
    req = urllib.request.Request(API, data=json.dumps({"query": query, "variables": variables or {}}).encode(),
                                 headers={"Authorization": f"Bearer {os.environ['CLOUDFLARE_ANALYTICS_TOKEN']}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def share(part: int, whole: int) -> str:
    return f"{round(100 * part / whole):>3}%" if whole else "   –"


def line(sums: dict, only: str = "") -> str:
    """Good / middling / poor for each metric (or `only` one), and how many loads it was measured on."""
    out = []
    for name, m in METRICS:
        if only and m != only:
            continue
        whole = sums.get(f"{m}Total") or 0
        out.append(f"{name} {share(sums.get(f'{m}Good') or 0, whole)} {share(sums.get(f'{m}NeedsImprovement') or 0, whole)}"
                   f" {share(sums.get(f'{m}Poor') or 0, whole)} ({whole})")
    return "   ".join(out)


def groups(dimensions: str, variables: dict, limit: int, paths: list | None = None) -> list:
    """Sums by the dimensions named, of this site's hosts; with `paths`, of those pages alone."""
    query = """query($acc: String!, $since: Time!, $until: Time!, $hosts: [String!]%s) { viewer {
      accounts(filter: {accountTag: $acc}) {
        rows: %s(limit: %d, orderBy: [count_DESC],
          filter: {datetime_geq: $since, datetime_leq: $until, bot: 0, requestHost_in: $hosts%s}) {
          count sum { %s } dimensions { %s } } } } }""" % (
        ", $paths: [String!]" if paths else "", DATASET, limit,
        ", requestPath_in: $paths" if paths else "", SUMS, dimensions)
    if paths:
        variables = dict(variables, paths=paths)
    got = post(query, variables)
    if got.get("errors"):
        print("Cloudflare:", "; ".join(e.get("message", "?") for e in got["errors"])[:600])
        return []
    return got["data"]["viewer"]["accounts"][0]["rows"]


def short(sums: dict) -> list:
    """The metrics a row holds under the line, of those measured often enough to say."""
    return [(name, m) for name, m in METRICS
            if (sums.get(f"{m}Total") or 0) >= LEAST and (sums.get(f"{m}Good") or 0) < LINE * sums[f"{m}Total"]]


def schema():
    """The dataset's fields as Cloudflare names them now: found from the query's root, by name, a step at a time."""
    def fields(type_name: str) -> dict:
        got = post('{ __type(name: "%s") { fields { name type { name kind ofType { name kind ofType { name kind ofType { name } } } } } } }' % type_name)
        out = {}
        for f in ((got.get("data") or {}).get("__type") or {}).get("fields") or []:
            t = f["type"]
            while t and not t.get("name"):
                t = t.get("ofType")
            out[f["name"]] = (t or {}).get("name")
        return out
    root = ((post("{ __schema { queryType { name } } }").get("data") or {}).get("__schema") or {}).get("queryType", {}).get("name")
    at = root
    for step in ("viewer", "accounts"):
        at = fields(at).get(step)
    account = fields(at)
    print("Datasets with 'rum' in the name:", ", ".join(sorted(n for n in account if "rum" in n.lower())))
    row = fields(account.get(DATASET) or "")
    for part in sorted(row):
        inner = fields(row[part]) if row[part] else {}
        print(f"\n{DATASET}.{part}: {', '.join(sorted(inner)) or row[part]}")


def main(hours: int):
    until = datetime.now(timezone.utc)
    since = until - timedelta(hours=hours)
    variables = {"acc": os.environ["CLOUDFLARE_ACCOUNT_ID"], "hosts": HOSTS,
                 "since": since.strftime("%Y-%m-%dT%H:%M:%SZ"), "until": until.strftime("%Y-%m-%dT%H:%M:%SZ")}
    print(f"Core Web Vitals, last {hours} h, to {variables['until']}: share of loads good / middling / poor, "
          f"(loads measured); rows under {LEAST} left out")
    print("Good: LCP to 2.5 s, INP to 200 ms, CLS to 0.1. The line to hold: good for 75% or more.")
    print("\nBy device")
    for r in groups("deviceType", variables, 6):
        if r["count"] >= LEAST:
            print(f"  {line(r['sum'])}   {r['dimensions']['deviceType'] or '(none)'}")
    kinds: dict[str, dict] = {}
    for r in groups("requestPath", variables, PATHS):
        k = kinds.setdefault(kind(r["dimensions"]["requestPath"]), {"count": 0, "paths": [], "sum": dict.fromkeys(FIELDS, 0)})
        k["count"] += r["count"]
        k["paths"].append(r["dimensions"]["requestPath"])
        for f in FIELDS:
            k["sum"][f] += r["sum"].get(f) or 0
    print("\nBy kind of page")
    ordered = sorted(kinds.items(), key=lambda kv: -kv[1]["count"])
    for name, k in ordered:
        if k["count"] >= LEAST:
            print(f"  {line(k['sum'])}   {name}")
    for name, k in ordered:
        for metric, m in short(k["sum"]):
            print(f"\n{metric} under the line on {name}: by element")
            for e in groups(ELEMENT[m], variables, 8, k["paths"][:200]):
                if (e["sum"].get(f"{m}Total") or 0) >= LEAST // 4:
                    print(f"  {line(e['sum'], m)}   {e['dimensions'][ELEMENT[m]] or '(none named)'}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["schema"]:
        schema()
    else:
        hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
        if not 1 <= hours <= 2160:
            sys.exit("hours: from 1 to 2160")
        main(hours)
