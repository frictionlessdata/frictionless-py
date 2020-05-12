from tableschema import Field
from goodtables import Headers


# General


def test_basic():
    headers = create_headers(['field1', 'field2', 'field3'])
    assert headers.field_positions == [1, 2, 3]
    assert headers.errors == []
    assert headers == ['field1', 'field2', 'field3']


# Helpers


def create_headers(headers, *, fields=[], field_positions=[]):
    field_positions = field_positions or list(range(1, len(headers) + 1))
    if not fields:
        for field_position in field_positions:
            fields.append(Field({'name': 'field%s' % field_position, 'type': 'any'}))
    return Headers(headers, fields=fields, field_positions=field_positions)
