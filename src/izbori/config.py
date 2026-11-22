"""Project-wide settings. Override with environment variables when running a fork."""

import os

SITE_URL = os.environ.get("IZBORI_SITE_URL", "https://izbornipodaci.rs/").rstrip("/") + "/"
REPO_URL = os.environ.get("IZBORI_REPO_URL", "https://github.com/javni-uvid/izborna-analiza")
RIK_BASE = os.environ.get("IZBORI_RIK_BASE", "https://www.rik.parlament.gov.rs")
RIK_PUBLIC = "https://www.rik.parlament.gov.rs"
USER_AGENT = f"izborni-podaci/0.1 (+{REPO_URL})"
# Cloudflare Web Analytics' site token (22 Nov 2026, the maintainer's exception to principle 5 in AGENTS.md): when set,
# every page loads Cloudflare's counting script, the one script from another server, and the footer and the about
# page say so. Public by design (every page shows it); empty, nothing is loaded. Only letters and digits are taken.
ANALYTICS_TOKEN = os.environ.get("IZBORI_ANALYTICS_TOKEN", "")
ANALYTICS_TOKEN = ANALYTICS_TOKEN if ANALYTICS_TOKEN.isalnum() else ""
