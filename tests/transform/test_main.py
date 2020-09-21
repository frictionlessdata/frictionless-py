import os
from frictionless import transform, Package


# General


def test_ensure_dir(tmpdir):

    # Write
    transform(
        {
            "type": "package",
            "steps": [
                {"type": "load", "spec": {"loadSource": "data/table.csv"}},
                {"type": "set_type", "spec": {"name": "id", "type": "string"}},
                {"type": "dump_to_path", "spec": {"outPath": tmpdir}},
            ],
        }
    )

    # Read
    package = Package(os.path.join(tmpdir, "datapackage.json"))
    assert package.get_resource("table").read_rows() == [
        {"id": "1", "name": "english"},
        {"id": "2", "name": "中国人"},
    ]
