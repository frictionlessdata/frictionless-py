from six.moves import zip_longest


def create_cells(headers, schema_fields, optional_fields, values=None, row_number=None):
    """Create list of cells from headers, fields and values.

    Args:
        headers (List[str]): The headers values.
        schema_fields (List[tableschema.field.Field]): The tableschema
            fields.
        optional_fields (List[str]): List of schema fields which are defined as
            optional. This has the effect that a field defined as optional and
            is missing from the header and values, will not create a cell for
            that field.
        values (List[Any], optional): The cells values. If not specified,
            the created cells will have the same values as their
            corresponding headers. This is useful for specifying headers
            cells.
            If the list has any `None` values, as is the case on empty
            cells, the resulting Cell will have an empty string value. If
            the `values` list has a different length than the `headers`,
            the resulting Cell will have value `None`.
        row_number (int, optional): The row number.

    Returns:
        List[dict]: List of cells.
    """
    fillvalue = '_fillvalue'
    is_header_row = (values is None)
    cells = []

    iterator = zip_longest(headers, schema_fields, values or [], fillvalue=fillvalue)
    for column_number, (header, field, value) in enumerate(iterator, start=1):
        if header == fillvalue:
            header = None
        elif is_header_row:
            value = header
        if field == fillvalue:
            field = None
        if value == fillvalue:
            value = None

        # Only allow optional fields to be ignored if there is no header or value
        # defined.
        # - If both of them are defined, then don't ignore it.
        # - If either of them are defined separately, then indicates a structural
        #   error, so leave the cell to be created and let them be checked
        if (header is None and value is None and
                field and field.name in optional_fields):
            continue

        cell = create_cell(header, value, field, column_number, row_number)
        cells.append(cell)

    return cells


def create_cell(header, value=None, field=None, column_number=None, row_number=None):
    cell = {
        'header': header,
        'field': field,
        'value': value,
        'column-number': column_number,
        'number': column_number,  # FIXME: Remove deprecated "number"
        'row-number': row_number,
    }
    return _remove_none_values(cell)


def _remove_none_values(dictionary):
    result = {}
    for key, value in dictionary.items():
        if value is not None:
            result[key] = value
    return result
