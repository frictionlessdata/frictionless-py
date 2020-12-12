import os
import pytest
import sqlite3
from pytest_cov.embed import cleanup_on_sigterm
from dotenv import load_dotenv

load_dotenv(".env")


# Cleanups


cleanup_on_sigterm()


# Fixtures


@pytest.fixture
def database_url(tmpdir):
    path = str(tmpdir.join("database.db"))
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE 'table' (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO 'table' VALUES (1, 'english'), (2, '中国人')")
    conn.commit()
    yield "sqlite:///%s" % path
    conn.close()


# Settings


def pytest_addoption(parser):
    parser.addoption(
        "--ci",
        action="store_true",
        dest="ci",
        default=False,
        help="enable integrational tests",
    )


def pytest_configure(config):
    if not config.option.ci:
        expr = getattr(config.option, "markexpr")
        setattr(config.option, "markexpr", "{expr} and not ci" if expr else "not ci")


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    return os.path.join("data", "cassettes")
