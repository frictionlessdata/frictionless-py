from cached_property import cached_property
from . import errors


class Headers(list):
    def __init__(self, cells, *, fields, field_positions):
        assert len(field_positions) in (len(cells), len(fields))

        # Set params
        self.__field_positions = field_positions
        self.__errors = []

        # Extra headers
        if len(fields) < len(cells):
            iterator = cells[len(fields) :]
            start = max(field_positions[: len(fields)]) + 1
            del cells[len(fields) :]
            for field_position, cell in enumerate(iterator, start=start):
                self.__errors.append(
                    errors.ExtraHeaderError(
                        details='',
                        cells=cells,
                        cell='',
                        field_name='',
                        field_number=len(fields) + field_position - start,
                        field_position=field_position,
                    )
                )

        # Missing headers
        if len(fields) > len(cells):
            start = len(cells) + 1
            iterator = zip(field_positions[len(cells) :], fields[len(cells) :])
            for field_number, (field_position, field) in enumerate(iterator, start=start):
                self.__errors.append(
                    errors.MissingHeaderError(
                        details='',
                        cells=list(map(str, cells)),
                        cell='',
                        field_name=field.name,
                        field_number=field_number,
                        field_position=field_position,
                    )
                )

        # Iterate items
        field_number = 0
        for field_position, field, cell in zip(field_positions, fields, cells):
            field_number += 1

            # Blank Header
            if not cell:
                self.__errors.append(
                    errors.BlankHeaderError(
                        details='',
                        cells=list(map(str, cells)),
                        cell='',
                        field_name=field.name,
                        field_number=field_number,
                        field_position=field_position,
                    )
                )

            # Duplicated Header
            if cell:
                duplicate_field_positions = []
                seen_cells = cells[0 : field_number - 1]
                seen_field_positions = field_positions[0 : field_number - 1]
                for seen_position, seen_cell in zip(seen_field_positions, seen_cells):
                    if cell == seen_cell:
                        duplicate_field_positions.append(seen_position)
                if duplicate_field_positions:
                    cell = None
                    self.__errors.append(
                        errors.DuplicateHeaderError(
                            details=', '.join(map(str, duplicate_field_positions)),
                            cells=list(map(str, cells)),
                            cell=str(cells[field_number - 1]),
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position,
                        )
                    )

            # Non-matching Header
            if cell:
                if field.name != cell:
                    self.__errors.append(
                        errors.NonMatchingHeaderError(
                            details='',
                            cells=list(map(str, cells)),
                            cell=str(cell),
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position,
                        )
                    )

        # Save headers
        super().__init__(cells)

    @cached_property
    def field_positions(self):
        return self.__field_positions

    @cached_property
    def errors(self):
        return self.__errors
