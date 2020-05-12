from goodtables import validate_table


# General


# TODO: fix/test properly stream.field_positions
def test_validate_table():
    report = validate_table('data/table.csv')
    assert report['valid']
