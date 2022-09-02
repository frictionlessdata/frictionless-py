import textwrap
from frictionless import Pipeline, steps


# General


def test_pipeline():
    pipeline = Pipeline(steps=[steps.table_normalize()])
    assert pipeline.step_types == ["table-normalize"]


def test_pipeline_from_descriptor():
    pipeline = Pipeline.from_descriptor({"steps": [{"type": "table-normalize"}]})
    assert pipeline.step_types == ["table-normalize"]
    assert isinstance(pipeline.steps[0], steps.table_normalize)


def test_pipeline_pprint():
    pipeline = Pipeline.from_descriptor(
        {
            "steps": [
                {"type": "table-normalize"},
                {"type": "table-melt", "fieldName": "name"},
            ],
        }
    )
    expected = """
    {'steps': [{'type': 'table-normalize'},
               {'type': 'table-melt', 'fieldName': 'name'}]}
    """
    assert repr(pipeline) == textwrap.dedent(expected).strip()
