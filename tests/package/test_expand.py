from frictionless import Package, helpers


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Expand


def test_package_expand():
    package = Package("data/package.json")
    package.expand()
    print(package)
    assert package == {
        "name": "name",
        "resources": [
            {
                "name": "name",
                "path": "table.csv",
                "profile": "tabular-data-resource",
                "scheme": "file",
                "format": "csv",
                "hashing": "md5",
                "encoding": "utf-8",
                "innerpath": "",
                "compression": "",
                "control": {},
                "dialect": {
                    "delimiter": ",",
                    "lineTerminator": "\r\n",
                    "quoteChar": '"',
                    "doubleQuote": True,
                    "skipInitialSpace": False,
                },
                "layout": {
                    "header": True,
                    "headerRows": [1],
                    "headerJoin": " ",
                    "headerCase": True,
                },
                "schema": {"fields": [], "missingValues": [""]},
            }
        ],
        "profile": "data-package",
    }


def test_package_expand_empty():
    package = Package()
    package.expand()
    assert package == {
        "profile": "data-package",
        "resources": [],
    }


def test_package_expand_resource_schema():
    schema = {
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "string"}]
    }
    package = Package({"resources": [{"path": "data/table.csv", "schema": schema}]})
    package.expand()
    assert package == {
        "resources": [
            {
                "path": "data/table.csv",
                "schema": {
                    "fields": [
                        {
                            "name": "id",
                            "type": "integer",
                            "format": "default",
                            "bareNumber": True,
                        },
                        {"name": "name", "type": "string", "format": "default"},
                    ],
                    "missingValues": [""],
                },
                "profile": "tabular-data-resource",
                "scheme": "file",
                "format": "csv",
                "hashing": "md5",
                "encoding": "utf-8",
                "innerpath": "",
                "compression": "",
                "control": {},
                "dialect": {
                    "delimiter": ",",
                    "lineTerminator": "\r\n",
                    "quoteChar": '"',
                    "doubleQuote": True,
                    "skipInitialSpace": False,
                },
                "layout": {
                    "header": True,
                    "headerRows": [1],
                    "headerJoin": " ",
                    "headerCase": True,
                },
            }
        ],
        "profile": "data-package",
    }


def test_package_expand_resource_dialect():
    dialect = {"delimiter": ";"}
    package = Package({"resources": [{"path": "data/table.csv", "dialect": dialect}]})
    package.expand()
    assert package == {
        "resources": [
            {
                "path": "data/table.csv",
                "dialect": {
                    "delimiter": ";",
                    "lineTerminator": "\r\n",
                    "quoteChar": '"',
                    "doubleQuote": True,
                    "skipInitialSpace": False,
                },
                "profile": "tabular-data-resource",
                "scheme": "file",
                "format": "csv",
                "hashing": "md5",
                "encoding": "utf-8",
                "innerpath": "",
                "compression": "",
                "control": {},
                "layout": {
                    "header": True,
                    "headerRows": [1],
                    "headerJoin": " ",
                    "headerCase": True,
                },
                "schema": {"fields": [], "missingValues": [""]},
            }
        ],
        "profile": "data-package",
    }
