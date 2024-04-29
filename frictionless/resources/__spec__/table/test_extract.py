import os
from pathlib import Path

from frictionless import Resource, resources, system
from frictionless.resources import TableResource

# General


def test_extract_resource():
    resource = TableResource.from_descriptor("data/resource.json")
    assert resource.extract() == {
        "name": [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
    }


def test_extract_resource_process():
    resource = TableResource.from_descriptor("data/resource.json")
    process = lambda row: {**row.to_dict(), "id": 3}
    assert resource.extract(process=process) == {
        "name": [
            {"id": 3, "name": "english"},
            {"id": 3, "name": "中国人"},
        ]
    }


def test_extract_resource_from_file():
    resource = TableResource(path="data/table.csv")
    assert resource.extract() == {
        "table": [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
    }


def test_extract_resource_from_file_process():
    resource = TableResource(path="data/table.csv")
    process = lambda row: {**row.to_dict(), "id": 3}
    assert resource.extract(process=process) == {
        "table": [
            {"id": 3, "name": "english"},
            {"id": 3, "name": "中国人"},
        ]
    }


def test_extract_resource_from_file_pathlib():
    resource = Resource(Path("data/table.csv"))
    assert isinstance(resource, TableResource)
    assert resource.extract() == {
        "table": [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
    }


# Bugs


def test_extract_resource_from_json_format_issue_827():
    resource = resources.TableResource(path="data/table.json")
    assert resource.extract() == {
        "table": [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
    }


def test_extract_resource_basepath_and_abspath_issue_856():
    descriptor = {"name": "name", "path": os.path.abspath("data/table.csv")}
    with system.use_context(trusted=True):
        resource = TableResource.from_descriptor(descriptor, basepath="data")
        assert resource.extract() == {
            "name": [
                {"id": 1, "name": "english"},
                {"id": 2, "name": "中国人"},
            ]
        }


def test_extract_resource_string_with_leading_zeros_issue_1232_1364():
    resource = TableResource(path="data/issue-1232.csv")
    assert resource.extract(limit_rows=1) == {
        "issue-1232": [
            {
                "comune": 30151360,
                "codice_regione": 3,
                "codice_provincia": 15,
                "codice_comune": 1360,
                "denominazione_comune": "POLPENAZZE DEL GARDA",
                "sigla_provincia": "BS",
                "data_entrata_in_carica": "13/10/2021",
            }
        ]
    }
