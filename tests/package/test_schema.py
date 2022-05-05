from frictionless import Package, helpers


IS_UNIX = not helpers.is_platform("windows")
BASEURL = "https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/%s"


# Schema


DESCRIPTOR_FK = {
    "resources": [
        {
            "name": "main",
            "data": [
                ["id", "name", "surname", "parent_id"],
                ["1", "Alex", "Martin", ""],
                ["2", "John", "Dockins", "1"],
                ["3", "Walter", "White", "2"],
            ],
            "schema": {
                "fields": [
                    {"name": "id"},
                    {"name": "name"},
                    {"name": "surname"},
                    {"name": "parent_id"},
                ],
                "foreignKeys": [
                    {
                        "fields": "name",
                        "reference": {"resource": "people", "fields": "firstname"},
                    },
                ],
            },
        },
        {
            "name": "people",
            "data": [
                ["firstname", "surname"],
                ["Alex", "Martin"],
                ["John", "Dockins"],
                ["Walter", "White"],
            ],
        },
    ],
}


def test_package_schema_foreign_key():
    package = Package(DESCRIPTOR_FK)
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].valid
    assert rows[0].to_dict() == {
        "id": "1",
        "name": "Alex",
        "surname": "Martin",
        "parent_id": None,
    }
    assert rows[1].to_dict() == {
        "id": "2",
        "name": "John",
        "surname": "Dockins",
        "parent_id": "1",
    }
    assert rows[2].to_dict() == {
        "id": "3",
        "name": "Walter",
        "surname": "White",
        "parent_id": "2",
    }


def test_package_schema_foreign_key_invalid():
    package = Package(DESCRIPTOR_FK)
    package.resources[1].data[3][0] = "bad"
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].errors[0].code == "foreign-key-error"
    assert rows[0].to_dict() == {
        "id": "1",
        "name": "Alex",
        "surname": "Martin",
        "parent_id": None,
    }
    assert rows[1].to_dict() == {
        "id": "2",
        "name": "John",
        "surname": "Dockins",
        "parent_id": "1",
    }
    assert rows[2].to_dict() == {
        "id": "3",
        "name": "Walter",
        "surname": "White",
        "parent_id": "2",
    }


def test_package_schema_foreign_key_self_reference():
    package = Package(DESCRIPTOR_FK)
    package.resources[0].schema.foreign_keys = [
        {"fields": "parent_id", "reference": {"resource": "", "fields": "id"}}
    ]
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].valid


def test_package_schema_foreign_key_self_reference_invalid():
    package = Package(DESCRIPTOR_FK)
    package.resources[0].data[2][0] = "0"
    package.resources[0].schema.foreign_keys = [
        {"fields": "parent_id", "reference": {"resource": "", "fields": "id"}}
    ]
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].errors[0].code == "foreign-key-error"


def test_package_schema_foreign_key_multifield():
    package = Package(DESCRIPTOR_FK)
    package.resources[0].schema.foreign_keys = [
        {
            "fields": ["name", "surname"],
            "reference": {"resource": "people", "fields": ["firstname", "surname"]},
        }
    ]
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].valid


def test_package_schema_foreign_key_multifield_invalid():
    package = Package(DESCRIPTOR_FK)
    package.resources[0].schema.foreign_keys = [
        {
            "fields": ["name", "surname"],
            "reference": {"resource": "people", "fields": ["firstname", "surname"]},
        }
    ]
    package.resources[1].data[3][0] = "bad"
    resource = package.get_resource("main")
    rows = resource.read_rows()
    assert rows[0].valid
    assert rows[1].valid
    assert rows[2].errors[0].code == "foreign-key-error"
