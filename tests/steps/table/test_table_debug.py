from frictionless import Pipeline, steps
from frictionless.resources import TableResource


class Counter:
    count = 0

    def __call__(self, row):
        self.count += 1


def test_step_table_debug():
    source = TableResource(path="data/transform.csv")
    counter = Counter()

    pipeline = Pipeline(
        steps=[steps.table_debug(function=counter)],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]

    assert counter.count == 3
