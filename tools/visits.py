"""What Cloudflare Web Analytics counted on izbornipodaci.rs: pages, where visitors came from, devices, hours.

Asked of Cloudflare's GraphQL analytics by the **visits** workflow, with a token that only reads the account's
analytics (taken from javni-uvid/zailiprotiv's, 22 Nov 2026). Only sums are printed, and a row seen fewer than three
times is left out: the run's log is public, and a sum of one can be a person. No address, no single request, nothing
about any one visitor is asked for at all. The account may hold other sites, so every question names this one."""
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.cloudflare.com/client/v4/graphql"
HOSTS = ["izbornipodaci.rs", "www.izbornipodaci.rs"]
LEAST = 3


def ask(query: str, variables: dict) -> dict:
    req = urllib.request.Request(API, data=json.dumps({"query": query, "variables": variables}).encode(),
                                 headers={"Authorization": f"Bearer {os.environ['CLOUDFLARE_ANALYTICS_TOKEN']}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        got = json.load(r)
    if got.get("errors"):
        print("Cloudflare:", "; ".join(e.get("message", "?") for e in got["errors"])[:600])
        return {}
    accounts = (got.get("data") or {}).get("viewer", {}).get("accounts") or [{}]
    return accounts[0]


def groups(dimension: str, variables: dict, limit: int = 40, order: str = "count_DESC") -> list:
    query = """query($acc: String!, $since: Time!, $until: Time!, $hosts: [String!]) { viewer {
      accounts(filter: {accountTag: $acc}) {
        rows: rumPageloadEventsAdaptiveGroups(limit: %d, orderBy: [%s],
          filter: {datetime_geq: $since, datetime_leq: $until, bot: 0, requestHost_in: $hosts}) {
          count sum { visits } dimensions { %s } } } } }""" % (limit, order, dimension)
    return ask(query, variables).get("rows", [])


def main(hours: int) -> None:
    until = datetime.now(timezone.utc)
    since = until - timedelta(hours=hours)
    variables = {"acc": os.environ["CLOUDFLARE_ACCOUNT_ID"], "hosts": HOSTS,
                 "since": since.strftime("%Y-%m-%dT%H:%M:%SZ"), "until": until.strftime("%Y-%m-%dT%H:%M:%SZ")}
    print(f"Web Analytics, last {hours} h, to {variables['until']} (browsers only; rows under {LEAST} left out)")
    for r in groups("requestHost", variables):
        if r["count"] >= LEAST:
            print(f"  {r['dimensions']['requestHost']}: {r['count']} page views, {r['sum']['visits']} visits")
    for title, dim, limit in (("Pages", "requestPath", 60), ("Came from", "refererHost", 25),
                              ("Device", "deviceType", 5), ("Country", "countryName", 12),
                              ("Browser", "userAgentBrowser", 8)):
        print(f"\n{title}  (page views / visits)")
        for r in groups(dim, variables, limit):
            if r["count"] >= LEAST:
                print(f"  {r['count']:>6} {r['sum']['visits']:>6}  {r['dimensions'][dim] or '(none)'}")
    print("\nBy hour, UTC  (page views / visits)")
    for r in groups("datetimeHour", variables, hours + 2, "datetimeHour_ASC"):
        if r["count"] >= LEAST:
            print(f"  {r['dimensions']['datetimeHour'][5:16]}  {r['count']:>5} {r['sum']['visits']:>5}")


if __name__ == "__main__":
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    if not 1 <= hours <= 2160:
        sys.exit("hours: from 1 to 2160")
    main(hours)
