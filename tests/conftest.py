from pathlib import Path

import pytest

from izbori.history import Archive

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
R2026 = "680072"


def pytest_configure(config):
    """On Windows the tests that build the whole site (marked `site`) are left to **test** on the pull request
    (20 Nov 2026, AGENTS.md): there the build is several times slower and the module took 40 minutes and more.
    `IZBORI_SVI_TESTOVI=1`, or any `-m`, runs what is asked."""
    import os
    import sys
    if sys.platform == "win32" and not config.option.markexpr and not os.environ.get("IZBORI_SVI_TESTOVI"):
        config.option.markexpr = "not site"
        config.issue_config_time_warning(pytest.PytestConfigWarning(
            "Windows: the tests marked `site` run on the pull request, not here (IZBORI_SVI_TESTOVI=1 runs them)"),
            stacklevel=2)


@pytest.fixture(scope="session")
def archive() -> Archive:
    return Archive(DATA)


@pytest.fixture(scope="session")
def round2026(archive):
    return archive.load(R2026)


@pytest.fixture(scope="session")
def raw2026() -> bytes:
    return (DATA / "rounds" / R2026 / "results.csv").read_bytes()
