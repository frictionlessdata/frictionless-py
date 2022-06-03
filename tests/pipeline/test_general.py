import pytest
from frictionless import Pipeline


# General


def test_pipeline_resource():
    pipeline = Pipeline(
        {
            "tasks": [
                {
                    "type": "resource",
                    "source": {"path": "data/transform.csv"},
                    "steps": [
                        {"code": "cell-set", "fieldName": "population", "value": 100},
                    ],
                }
            ]
        }
    )
    status = pipeline.run()
    assert status.task.target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert status.task.target.read_rows() == [
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]


@pytest.mark.skip
def test_pipeline_package():
    pipeline = Pipeline(
        {
            "tasks": [
                {
                    "type": "package",
                    "source": "data/package/datapackage.json",
                    "steps": [
                        {"code": "resource-remove", "name": "data2"},
                    ],
                }
            ]
        }
    )
    status = pipeline.run()
    assert status.task.target.resource_names == ["data"]


def test_transform_pipeline():
    pipeline = Pipeline(
        {
            "tasks": [
                {
                    "type": "resource",
                    "source": {"path": "data/transform.csv"},
                    "steps": [
                        {"code": "cell-set", "fieldName": "population", "value": 100},
                    ],
                }
            ]
        }
    )
    status = pipeline.run()
    assert status.valid
    assert status.task.valid
    assert status.task.target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert status.task.target.read_rows() == [
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]


# Parallel


@pytest.mark.ci
def test_transform_pipeline_parallel():
    pipeline = Pipeline(
        {
            "tasks": [
                {
                    "type": "resource",
                    "source": {"path": "data/transform.csv"},
                    "steps": [
                        {"code": "cell-set", "fieldName": "population", "value": 100},
                    ],
                },
                {
                    "type": "resource",
                    "source": {"path": "data/transform.csv"},
                    "steps": [
                        {"code": "cell-set", "fieldName": "population", "value": 10000},
                    ],
                },
            ]
        }
    )
    status = pipeline.run()
    assert status.valid
    assert status.tasks[0].valid
    assert status.tasks[0].target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert status.tasks[0].target.read_rows() == [
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]
    assert status.tasks[1].valid
    assert status.tasks[1].target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert status.tasks[1].target.read_rows() == [
        {"id": 1, "name": "germany", "population": 10000},
        {"id": 2, "name": "france", "population": 10000},
        {"id": 3, "name": "spain", "population": 10000},
    ]


# Issues


def test_pipeline_pprint_1029():
    pipeline = Pipeline(
        {
            "tasks": [
                {
                    "type": "resource",
                    "source": {"path": "../data/transform.csv"},
                    "steps": [
                        {"code": "table-normalize"},
                        {"code": "table-melt", "fieldName": "name"},
                    ],
                }
            ]
        }
    )
    expected = """{'tasks': [{'source': {'path': '../data/transform.csv'},
            'steps': [{'code': 'table-normalize'},
                      {'code': 'table-melt', 'fieldName': 'name'}],
            'type': 'resource'}]}"""
    assert repr(pipeline) == expected
