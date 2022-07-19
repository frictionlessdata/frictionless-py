import os
import pytest
import sqlalchemy as sa
from frictionless import platform
from pytest_cov.embed import cleanup_on_sigterm
from dotenv import load_dotenv

load_dotenv(".env")


# Cleanups


cleanup_on_sigterm()


# Fixtures


@pytest.fixture
def google_credentials_path():
    path = os.environ.get("GOOGLE_CREDENTIALS_PATH")
    if not path or not os.path.isfile(path):
        pytest.skip('Environment variable "GOOGLE_CREDENTIALS_PATH" is not available')
    elif platform.type != "linux" or platform.python < "3.8":
        pytest.skip('Environment variable "GOOGLE_CREDENTIALS_PATH" is Linux/Python3.8')
    return path


@pytest.fixture
def postgresql_url():
    url = os.environ.get("POSTGRESQL_URL")
    if not url:
        pytest.skip('Environment varialbe "POSTGRESQL_URL" is not available')
    yield url
    engine = sa.create_engine(url)
    conn = engine.connect()
    meta = sa.MetaData(bind=conn)
    meta.reflect(views=True)
    for table in reversed(meta.sorted_tables):
        conn.execute(table.delete())
    conn.close()


@pytest.fixture
def mysql_url():
    url = os.environ.get("MYSQL_URL")
    if not url:
        pytest.skip('Environment varialbe "MYSQL_URL" is not available')
    yield url
    engine = sa.create_engine(url)
    conn = engine.connect()
    meta = sa.MetaData(bind=conn)
    meta.reflect(views=True)
    for table in reversed(meta.sorted_tables):
        conn.execute(table.delete())
    conn.close()


@pytest.fixture
def sqlite_url(tmpdir):
    path = str(tmpdir.join("database.db"))
    return "sqlite:///%s" % path


@pytest.fixture
def database_url(sqlite_url):
    engine = sa.create_engine(sqlite_url)
    conn = engine.connect()
    conn.execute("CREATE TABLE 'table' (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO 'table' VALUES (1, 'english'), (2, '中国人')")

    conn.execute(
        "CREATE TABLE 'fruits' (uid INTEGER PRIMARY KEY, fruit_name TEXT, calories INTEGER)"
    )
    conn.execute("INSERT INTO 'fruits' VALUES (1, 'Apples', 200), (2, 'Oranges中国人', 350)")
    yield sqlite_url
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
