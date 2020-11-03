import os
import io
from setuptools import setup, find_packages


# Helpers


def read(*paths):
    """Read a text file."""
    basedir = os.path.dirname(__file__)
    fullpath = os.path.join(basedir, *paths)
    contents = io.open(fullpath, encoding="utf-8").read().strip()
    return contents


# Prepare


PACKAGE = "frictionless"
NAME = PACKAGE.replace("_", "-")
TESTS_REQUIRE = [
    "mypy",
    "black",
    "pylama",
    "pytest",
    "pymysql",
    "psycopg2",
    "pytest-cov",
    "pydoc-markdown",
    "docstring-parser",
    "python-dotenv",
    "oauth2client",
    "responses",
    "coveralls",
    "nbconvert",
    "ipython",
    "jinja2",
    "gdown",
    "moto",
]
EXTRAS_REQUIRE = {
    "aws": ["boto3>=1.9"],
    "bigquery": ["google-api-python-client>=1.12.1"],
    "ckan": ["ckanapi>=4.3"],
    "dataflows": ["dataflows>=0.1"],
    "elastic": ["elasticsearch>=7.0,<8.0"],
    "gsheet": ["google-api-python-client>=1.5"],
    "html": ["pyquery>=1.4"],
    "ods": ["ezodf>=0.3"],
    "pandas": ["pandas>=1.0"],
    "server": ["gunicorn>=20.0", "flask>=1.1"],
    "spss": ["savReaderWriter>=3.0"],
    "sql": ["sqlalchemy>=1.3"],
    "tsv": ["linear-tsv>=1.0"],
    "dev": TESTS_REQUIRE,
}
INSTALL_REQUIRES = [
    "click>=6.6",
    "pyyaml>=5.3",
    "chardet>=3.0",
    "requests>=2.10",
    "jsonschema>=2.5",
    "simpleeval>=0.9",
    "stringcase>=1.2",
    "python-dateutil>=2.8",
    "python-slugify>=1.2",
    "unicodecsv>=0.14",
    "jsonlines>=1.2",
    "simplejson>=3.10",
    "openpyxl>=3.0",
    "isodate>=0.6",
    "rfc3986>=1.4",
    "ijson>=3.0",
    "xlrd>=1.2",
    "xlwt>=1.2",
    "petl>=1.6",
]
README = read("README.md")
VERSION = read(PACKAGE, "assets", "VERSION")
PACKAGES = find_packages(exclude=["tests"])
ENTRY_POINTS = {"console_scripts": ["frictionless = frictionless.__main__:program"]}


# Run


setup(
    name=NAME,
    version=VERSION,
    packages=PACKAGES,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require=EXTRAS_REQUIRE,
    entry_points=ENTRY_POINTS,
    zip_safe=False,
    long_description=README,
    long_description_content_type="text/markdown",
    description="Frictionless is a framework to describe, extract, validate, and transform tabular data",
    author="Open Knowledge Foundation",
    author_email="info@okfn.org",
    url="https://github.com/frictionlessdata/frictionless-py",
    license="MIT",
    keywords=[
        "data validation",
        "frictionless data",
        "open data",
        "json schema",
        "json table schema",
        "data package",
        "tabular data package",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
