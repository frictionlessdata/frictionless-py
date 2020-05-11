from . import helpers
from ..check import Check


class BaselineCheck(Check):
    def validate_table_headers(self, headers):
        errors = []

        # Iterate headers
        missing = helpers.combine.missing
        iterator = helpers.combine(self.schema.field_names, headers)
        for field_number, [field_name, header] in enumerate(iterator, start=1):

            # blank-header
            if header in (None, ''):
                errors.append(
                    self.spec.create_error(
                        'blank-header',
                        context={'headers': headers, 'fieldNumber': field_number},
                    )
                )

            # duplicated-header
            prev_headers = headers[0 : field_number - 1]
            duplicate_field_numbers = helpers.find_positions(prev_headers, header)
            if duplicate_field_numbers:
                errors.append(
                    self.spec.create_error(
                        'duplicate-header',
                        context={
                            'header': header,
                            'headers': headers,
                            'fieldNumber': field_number,
                            'details': ', '.join(duplicate_field_numbers),
                        },
                    )
                )

            # extra-header
            if field_name == missing:
                errors.append(
                    self.spec.create_error(
                        'extra-header',
                        context={
                            'header': header,
                            'headers': headers,
                            'fieldNumber': field_number,
                        },
                    )
                )

            # missing-header
            if header == missing:
                errors.append(
                    self.spec.create_error(
                        'missing-header',
                        context={
                            'headers': headers,
                            'fieldName': field_name,
                            'fieldNumber': field_number,
                        },
                    )
                )

            # non-matching-header
            if missing not in [field_name, header] and field_name != header:
                errors.append(
                    self.spec.create_error(
                        'non-matching-header',
                        context={
                            'header': header,
                            'headers': headers,
                            'fieldName': field_name,
                            'fieldNumber': field_number,
                        },
                    )
                )

        return errors

    def validate_table_row(self, row):
        errors = []

        # blank-row
        if row.is_blank:
            errors.append(
                self.spec.create_error(
                    'blank-row',
                    context={
                        'rowNumber': row.row_number,
                        'rowPosition': row.row_position,
                    },
                )
            )

        # extra-cell
        if row.extra_cells:
            for extra_field_number, extra_cell in enumerate(row.extra_cells, start=1):
                fieldPosition = max(row.field_positions) + extra_field_number
                errors.append(
                    self.spec.create_error(
                        'extra-cell',
                        context={
                            'cell': extra_cell,
                            'row': row,
                            'rowNumber': row.row_number,
                            'rowPosition': row.row_position,
                            'fieldPosition': field_position,
                        },
                    )
                )

        # Iterate cells
        iterator = enumerate(row.items_with_position(), start=1)
        for field_number, [field_position, field_name, cell] in iterator:

            # missing-cell
            if field_name in row.missing_cells:
                errors.append(
                    self.spec.create_error(
                        'missing-cell',
                        context={
                            'row': row,
                            'rowNumber': row.row_number,
                            'rowPosition': row.row_position,
                            'fieldName': field_name,
                            'fieldNumber': field_number,
                            'fieldPosition': field_position,
                        },
                    )
                )

        return errors

