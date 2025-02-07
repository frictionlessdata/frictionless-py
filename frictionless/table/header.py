from __future__ import annotations

from functools import cached_property
from typing import Iterable, List, Optional

from .. import errors, helpers
from ..exception import FrictionlessException
from ..schema import Field

Label = str


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
        schema_sync: bool,
    ):
        super().__init__(field.name for field in fields)
        self.__fields = fields.copy()
        self.__expected_fields: Optional[List[Field]] = None
        self.__schema_sync = schema_sync
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

        labels = self.labels

        # Extra label
        start = len(self.fields) + 1
        for field_number, label in enumerate(self._get_extra_labels(), start=start):
            self.__errors.append(
                errors.ExtraLabelError(
                    note="",
                    labels=list(map(str, labels)),
                    row_numbers=self.__row_numbers,
                    label=label,
                    field_name="",
                    field_number=field_number,
                )
            )

        # Missing label
        start = len(labels) + 1
        for field_number, field in enumerate(self._get_missing_fields(), start=start):
            if field is not None:  # type: ignore
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
        for index, (field, label) in enumerate(zip(self.get_expected_fields(), labels)):
            # field_number is 1-indexed
            field_number = index + 1

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

    def _get_extra_labels(self) -> List[str]:
        """Returns unexpected extra labels.

        If `schema_sync=False`, the labels are expected to be in same order
        and of same number than the schema fields. If the number of labels
        is longer than the number of fields, the last labels are returned as
        extra labels.

        If `schema_sync=True`, extra labels are ignored and this method
        returns an empty list
        """
        if not self.__schema_sync:
            if len(self.fields) < len(self.labels):
                return self.labels[len(self.fields) :]
        return []

    def _get_missing_fields(self) -> List[Field]:
        """Returns unexpected missing fields.

        If `schema_sync=False`, the labels are expected to be in same order
        and of same number than the schema fields. If the number of fields is
        longer than the number of labels, the last fields are returned as
        missing fields.

        If `schema_sync=True`, missing fields are ignored, except if they are
        marked as `required`.
        """

        fields = self.fields
        labels = self.labels
        if not self.__schema_sync:
            if len(fields) > len(labels):
                return fields[len(labels) :]
        else:

            def required_and_missing(field: Field) -> bool:
                required: bool = field.required or (
                    field.schema is not None and field.name in field.schema.primary_key
                )
                missing = self._normalize(field.name) not in [
                    self._normalize(label) for label in labels
                ]
                return required and missing

            return [field for field in fields if required_and_missing(field)]

        return []

    def get_expected_fields(self) -> List[Field]:
        """Returns a list of fields, in the order they are expected to be
        found in the data.

        The label with same position, and its associated
        data are expected to comply with the field's expectations.

        If `schema_sync=False`, the schema fields are precisely the expected
        fields, so they are returned unchanged.

        If `schema_sync=True`, fields are reordered so as the field names to
        match the labels. If no such field exists, an extra field with `type: any` is
        created on the fly.

        The result is cached as a property.
        """
        if not self.__expected_fields:
            if not self.__schema_sync:
                self.__expected_fields = self.fields
            else:
                expected_fields: List[Field] = []

                if len(self.labels) != len(set(self.labels)):
                    note = '"schema_sync" requires unique labels in the header'
                    raise FrictionlessException(note)

                for label in self.labels:
                    field = self._find_field_by_name(label)

                    if not field:
                        # Default value
                        field = Field.from_descriptor({"name": label, "type": "any"})

                    expected_fields.append(field)
                self.__expected_fields = expected_fields

        return self.__expected_fields

    def _find_field_by_name(self, name: str) -> Optional[Field]:
        try:
            return next(
                f for f in self.fields if self._normalize(f.name) == self._normalize(name)
            )
        except StopIteration:
            return None

    def _normalize(self, s: str) -> str:
        return s.lower() if self.__ignore_case else s
