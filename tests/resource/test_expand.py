from frictionless import Resource, helpers


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Expand


def test_resource_expand():
    resource = Resource({"name": "name", "path": "data/table.csv"})
    resource.expand()
    print(resource)
    assert resource == {
        "name": "name",
        "path": "data/table.csv",
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


def test_resource_expand_with_dialect():
    dialect = {"delimiter": "custom"}
    resource = Resource({"name": "name", "path": "data/table.csv", "dialect": dialect})
    resource.expand()
    assert resource == {
        "name": "name",
        "path": "data/table.csv",
        "dialect": {
            "delimiter": "custom",
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


def test_resource_expand_with_schema():
    schema = {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }
    resource = Resource({"name": "name", "path": "data/table.csv", "schema": schema})
    resource.expand()
    assert resource == {
        "name": "name",
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
