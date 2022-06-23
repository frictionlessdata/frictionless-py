from frictionless import Dialect


def test_dialect():
    dialect = Dialect()
    assert dialect.header_rows == [1]
    assert dialect.header_join == " "
    assert dialect.header_case == True
