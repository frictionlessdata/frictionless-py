from itertools import zip_longest
from importlib import import_module
from .helpers import cached_property
from . import helpers
from . import errors


class Header(list):
    """Header representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Header`

    > Constructor of this object is not Public API

    Parameters:
        labels (any[]): header row labels
        fields (Field[]): table fields
        field_positions (int[]): field positions
        row_positions (int[]): row positions
        ignore_case (bool): ignore case

    """

    def __init__(
        self,
        labels,
        *,
        fields,
        field_positions,
        row_positions,
        ignore_case=False,
    ):
        super().__init__(labels)
        self.__fields = [field.to_copy() for field in fields]
        self.__field_names = [field.name for field in fields]
        self.__field_positions = field_positions
        self.__row_positions = row_positions
        self.__ignore_case = ignore_case
        self.__errors = []
        self.__process()

    @cached_property
    def fields(self):
        """
        Returns:
            Schema: table fields
        """
        return self.__fields

    @cached_property
    def field_names(self):
        """
        Returns:
            str[]: table field names
        """
        return self.__field_names

    @cached_property
    def field_positions(self):
        """
        Returns:
            int[]: table field positions
        """
        return self.__field_positions

    @cached_property
    def row_positions(self):
        """
        Returns:
            int[]: table row positions
        """
        return self.__row_positions

    @cached_property
    def missing(self):
        """
        Returns:
            bool: if there is not header
        """
        return not self.__row_positions

    @cached_property
    def errors(self):
        """
        Returns:
            Error[]: header errors
        """
        return self.__errors

    @cached_property
    def valid(self):
        """
        Returns:
            bool: if header valid
        """
        return not self.__errors

    # Import/Export

    def to_str(self):
        """
        Returns:
            str: a row as a CSV string
        """

        plugin = import_module("frictionless.plugins.csv")
        cells = self.to_list(types=plugin.CsvParser.supported_types)
        return helpers.stringify_csv_string(cells)

    def to_list(self):
        """Convert to a list"""
        return self.copy()

    # Process

    def __process(self):

        # Skip missing
        if self.missing:
            return

        # Prepare context
        fields = self.__fields
        field_positions = self.__field_positions

        # Extra label
        if len(fields) < len(self):
            iterator = self[len(fields) :]
            start = max(field_positions[: len(fields)]) + 1
            for field_position, cell in enumerate(iterator, start=start):
                self.__errors.append(
                    errors.ExtraLabelError(
                        note="",
                        labels=list(map(str, self)),
                        row_positions=self.__row_positions,
                        label="",
                        field_name="",
                        field_number=len(fields) + field_position - start,
                        field_position=field_position,
                    )
                )

        # Missing label
        if len(fields) > len(self):
            start = len(self) + 1
            iterator = zip_longest(field_positions[len(self) :], fields[len(self) :])
            for field_number, (field_position, field) in enumerate(iterator, start=start):
                if field is not None:
                    self.__errors.append(
                        errors.MissingLabelError(
                            note="",
                            labels=list(map(str, self)),
                            row_positions=self.__row_positions,
                            label="",
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position
                            or max(field_positions, default=0) + field_number - start + 1,
                        )
                    )

        # Iterate items
        field_number = 0
        for field_position, field, cell in zip(field_positions, fields, self):
            field_number += 1

            # Blank label
            if not cell:
                self.__errors.append(
                    errors.BlankLabelError(
                        note="",
                        labels=list(map(str, self)),
                        row_positions=self.__row_positions,
                        label="",
                        field_name=field.name,
                        field_number=field_number,
                        field_position=field_position,
                    )
                )

            # Duplicated label
            if cell:
                duplicate_field_positions = []
                seen_cells = self[0 : field_number - 1]
                seen_field_positions = field_positions[0 : field_number - 1]
                for seen_position, seen_cell in zip(seen_field_positions, seen_cells):
                    if cell == seen_cell:
                        duplicate_field_positions.append(seen_position)
                if duplicate_field_positions:
                    cell = None
                    note = 'at position "%s"'
                    note = note % ", ".join(map(str, duplicate_field_positions))
                    self.__errors.append(
                        errors.DuplicateLabelError(
                            note=note,
                            labels=list(map(str, self)),
                            row_positions=self.__row_positions,
                            label=str(self[field_number - 1]),
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position,
                        )
                    )

            # Incorrect Label
            if cell:
                name = field.name
                if name.lower() != cell.lower() if self.__ignore_case else name != cell:
                    self.__errors.append(
                        errors.IncorrectLabelError(
                            note="",
                            labels=list(map(str, self)),
                            row_positions=self.__row_positions,
                            label=str(cell),
                            field_name=field.name,
                            field_number=field_number,
                            field_position=field_position,
                        )
                    )

        # Blank header
        if not self:
            self.__errors = [
                errors.BlankHeaderError(
                    note="",
                    labels=list(map(str, self)),
                    row_positions=self.__row_positions,
                )
            ]
