from goodtables import validate


# General


def test_validate():
    report = validate('data/schema.json')
    assert report.valid


def test_validate_invalid():
    report = validate({'fields': {}})
    assert report.flatten(['code', 'details']) == [
        [
            'schema-error',
            'Descriptor validation error: {} is not of type \'array\' at "fields" in descriptor and at "properties/fields/type" in profile',
        ],
    ]
