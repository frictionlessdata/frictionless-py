import os
from frictionless import Package
from frictionless.plugins.dataflows import DataflowsPipeline


# General


def test_pipeline(tmpdir):

    # Write
    pipeline = DataflowsPipeline(
        {
            "type": "dataflows",
            "steps": [
                {"type": "load", "spec": {"loadSource": "data/table.csv"}},
                {"type": "setType", "spec": {"name": "id", "type": "string"}},
                {"type": "dumpToPath", "spec": {"outPath": tmpdir}},
            ],
        }
    )
    pipeline.run()

    # Read
    package = Package(os.path.join(tmpdir, "datapackage.json"))
    assert package.get_resource("table").read_rows() == [
        {"id": "1", "name": "english"},
        {"id": "2", "name": "中国人"},
    ]
