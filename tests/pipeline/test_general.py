from frictionless import Pipeline, steps


# General


def test_pipeline():
    pipeline = Pipeline(steps=[steps.table_normalize()])
    assert pipeline.step_codes == ["table-normalize"]
    assert pipeline.limit_memory == 1000


def test_pipeline_from_descriptor():
    pipeline = Pipeline.from_descriptor(
        {
            "steps": [{"code": "table-normalize"}],
            "limitMemory": 100,
        }
    )
    assert pipeline.step_codes == ["table-normalize"]
    assert pipeline.limit_memory == 100
    assert isinstance(pipeline.steps[0], steps.table_normalize)


def test_pipeline_pprint():
    pipeline = Pipeline.from_descriptor(
        {
            "steps": [
                {"code": "table-normalize"},
                {"code": "table-melt", "fieldName": "name"},
            ],
        }
    )
    expected = """{'steps': [{'code': 'table-normalize'},
           {'code': 'table-melt', 'fieldName': 'name'}]}"""
    assert repr(pipeline) == expected
