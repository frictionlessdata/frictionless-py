from __future__ import annotations
from typing import List
from functools import cached_property
from .. import helpers
from .. import errors


# TODO: add types
class Header(list):
    """Header representation

    > Constructor of this object is not Public API

    Parameters:
        labels (any[]): header row labels
        fields (Field[]): table fields
        row_numbers (int[]): row numbers
        ignore_case (bool): ignore case

    """

    def __init__(
        self,
        labels,
        *,
        fields,
        row_numbers,
        ignore_case=False,
    ):
        super().__init__(field.name for field in fields)
        self.__fields = [field.to_copy() for field in fields]
        self.__field_names = self.copy()
        self.__row_numbers = row_numbers
        self.__ignore_case = ignore_case
        self.__labels = labels
        self.__errors: List[errors.HeaderError] = []
        self.__process()

    @cached_property
    def labels(self):
        """
        Returns:
            Schema: table labels
        """
        return self.__labels

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
    def field_numbers(self):
        """
        Returns:
            str[]: list of field numbers
        """
        return list(range(1, len(self.__field_names) + 1))

    @cached_property
    def row_numbers(self):
        """
        Returns:
            int[]: table row positions
        """
        return self.__row_numbers

    @cached_property
    def missing(self):
        """
        Returns:
            bool: if there is not header
        """
        return not self.__labels

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

    # Convert

    def to_str(self):
        """
        Returns:
            str: a row as a CSV string
        """

        cells = self.to_list()
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
        labels = self.__labels
        fields = self.__fields

        # Extra label
        if len(fields) < len(labels):
            start = len(fields) + 1
            iterator = labels[len(fields) :]
            for field_number, label in enumerate(iterator, start=start):
                self.__errors.append(
                    errors.ExtraLabelError(
                        note="",
                        labels=list(map(str, labels)),
                        row_numbers=self.__row_numbers,
                        label="",
                        field_name="",
                        field_number=field_number,
                    )
                )

        # Missing label
        if len(fields) > len(labels):
            start = len(labels) + 1
            iterator = fields[len(labels) :]
            for field_number, field in enumerate(iterator, start=start):
                if field is not None:
                    self.__errors.append(
                        errors.MissingLabelError(
                            note="",
                            labels=list(map(str, labels)),
                            row_numbers=self.__row_numbers,
                            label="",
                            field_name=field.name,
                            field_number=field_number,
                        )
                    )

        # Iterate items
        field_number = 0
        for field, label in zip(fields, labels):
            field_number += 1

            # Blank label
            if not label:
                self.__errors.append(
                    errors.BlankLabelError(
                        note="",
                        labels=list(map(str, labels)),
                        row_numbers=self.__row_numbers,
                        label="",
                        field_name=field.name,
                        field_number=field_number,
                    )
                )

            # Duplicated label
            if label:
                duplicate_field_numbers = []
                seen_cells = labels[0 : field_number - 1]
                for seen_number, seen_cell in enumerate(seen_cells, start=1):
                    if label == seen_cell:
                        duplicate_field_numbers.append(seen_number)
                if duplicate_field_numbers:
                    label = None
                    note = 'at position "%s"'
                    note = note % ", ".join(map(str, duplicate_field_numbers))
                    self.__errors.append(
                        errors.DuplicateLabelError(
                            note=note,
                            labels=list(map(str, labels)),
                            row_numbers=self.__row_numbers,
                            label=str(labels[field_number - 1]),
                            field_name=field.name,
                            field_number=field_number,
                        )
                    )

            # Incorrect Label
            if label:
                name = field.name
                # NOTE: review where we normalize the label/name
                lname = label.replace("\n", " ").strip()
                if name.lower() != lname.lower() if self.__ignore_case else name != lname:
                    self.__errors.append(
                        errors.IncorrectLabelError(
                            note="",
                            labels=list(map(str, labels)),
                            row_numbers=self.__row_numbers,
                            label=str(label),
                            field_name=field.name,
                            field_number=field_number,
                        )
                    )

        # Blank header
        if not labels:
            self.__errors = [
                errors.BlankHeaderError(
                    note="",
                    labels=list(map(str, labels)),
                    row_numbers=self.__row_numbers,
                )
            ]
