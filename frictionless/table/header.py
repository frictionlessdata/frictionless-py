from __future__ import annotations

from functools import cached_property
from typing import List, Optional

from ..exception import FrictionlessException
from ..schema import Field
from .. import errors, helpers


class Header(List[str]):  # type: ignore
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
        labels: List[str],
        *,
        fields: List[Field],
        row_numbers: List[int],
        ignore_case: bool = False,
        schema_sync: bool = False,
    ):
        super().__init__(field.name for field in fields)
        self.__fields = []
        for field in fields:
            copy = field.to_copy()
            # to_copy() goes through the descriptor and drops the back-reference
            # to the schema; restore it so checks like "field belongs to schema's
            # primary_key" remain accurate.
            copy.schema = field.schema
            self.__fields.append(copy)
        self.__field_names = self.copy()
        self.__row_numbers = row_numbers
        self.__ignore_case = ignore_case
        self.__schema_sync = schema_sync
        self.__labels = labels
        self.__errors: List[errors.HeaderError] = []
        self.__expected_fields: Optional[List[Field]] = None
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

    # Schema sync / expectations

    def get_expected_fields(self) -> List[Field]:
        """Returns the fields, in the order expected in the data.

        Without `schema_sync`, this is just the schema fields unchanged.

        With `schema_sync`, fields are reordered to match the labels; labels
        without a matching field get a fresh `any`-typed field, and fields not
        present in labels are dropped. Duplicate labels are rejected.
        """
        if self.__expected_fields is not None:
            return self.__expected_fields

        if not self.__schema_sync:
            self.__expected_fields = self.__fields
            return self.__expected_fields

        if len(self.__labels) != len(set(self.__labels)):
            note = '"schema_sync" requires unique labels in the header'
            raise FrictionlessException(note)

        expected: List[Field] = []
        for label in self.__labels:
            field = self.__find_field_by_name(label)
            if field is None:
                field = Field.from_descriptor({"name": label, "type": "any"})
            expected.append(field)
        self.__expected_fields = expected
        return self.__expected_fields

    def _get_extra_labels(self) -> List[str]:
        """Returns labels in the data that don't correspond to any schema field.

        Without `schema_sync`, labels beyond the schema's field count are
        considered extras. With `schema_sync`, extras are accepted, so an
        empty list is returned.
        """
        if not self.__schema_sync:
            if len(self.__fields) < len(self.__labels):
                return self.__labels[len(self.__fields) :]
        return []

    def _get_missing_fields(self) -> List[Field]:
        """Returns schema fields that don't have a corresponding label.

        Without `schema_sync`, fields beyond the labels count are considered
        missing. With `schema_sync`, only required fields whose name is not
        among the labels are missing.
        """
        fields = self.__fields
        labels = self.__labels
        if not self.__schema_sync:
            if len(fields) > len(labels):
                return fields[len(labels) :]
            return []

        normalized_labels = [self.__normalize(label) for label in labels]

        def required_and_missing(field: Field) -> bool:
            required = field.required or (
                field.schema is not None and field.name in field.schema.primary_key
            )
            return (
                required and self.__normalize(field.name) not in normalized_labels
            )

        return [field for field in fields if required_and_missing(field)]

    def __find_field_by_name(self, name: str) -> Optional[Field]:
        target = self.__normalize(name)
        for f in self.__fields:
            if self.__normalize(f.name) == target:
                return f
        return None

    def __normalize(self, s: str) -> str:
        return s.lower() if self.__ignore_case else s

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

        # Extra labels
        extra_start = len(fields) + 1
        for offset, label in enumerate(self._get_extra_labels()):
            self.__errors.append(
                errors.ExtraLabelError(
                    note="",
                    labels=list(map(str, labels)),
                    row_numbers=self.__row_numbers,
                    label="",
                    field_name="",
                    field_number=extra_start + offset,
                )
            )

        # Missing fields
        missing_fields = self._get_missing_fields()
        if missing_fields:
            missing_ids = {id(field) for field in missing_fields}
            for field_number, field in enumerate(fields, start=1):
                if field is None or id(field) not in missing_ids:
                    continue
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
                duplicate_field_numbers: List[int] = []
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
