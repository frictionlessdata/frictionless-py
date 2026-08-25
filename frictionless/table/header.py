from __future__ import annotations

from functools import cached_property
from typing import List, Optional, Tuple

from .. import errors, helpers, types
from ..exception import FrictionlessException
from ..schema import Field
from .label_matching import LabelMatching, deduplicate_names

# The `fieldsMatch` modes are told apart by which mismatch they tolerate: a
# label with no matching field, or a declared field with no matching label
# (the required ones aside). `exact` tolerates neither and, alone, maps the
# labels to the fields by order rather than by name.
TOLERATES_EXTRA_LABELS = ("subset", "partial")
TOLERATES_MISSING_FIELDS = ("superset", "partial")


class Header(List[str]):  # type: ignore
    """Header representation

    Compares the header row read from the data source (the "labels") with the
    fields declared in the schema, and reports the mismatches as errors.

    > Constructor of this object is not Public API

    Parameters:
        labels (any[]): the header row as read from the data source
        fields (Field[]): the fields declared in the schema, in schema order
        row_numbers (int[]): row numbers the header spans in the data source
        ignore_case (bool): ignore case
        fields_match (str): how the fields match the data source

    """

    def __init__(
        self,
        labels: List[str],
        *,
        fields: List[Field],
        row_numbers: List[int],
        ignore_case: bool = False,
        fields_match: types.IFieldsMatch = "exact",
    ):
        super().__init__(field.name for field in fields)
        self.__fields: List[Field] = []
        for field in fields:
            copy = field.to_copy()
            # to_copy() goes through the descriptor and drops the back-reference
            # to the schema; restore it so checks like "field belongs to schema's
            # primary_key" remain accurate.
            copy.schema = field.schema
            self.__fields.append(copy)
        self.__field_names = self.copy()
        self.__row_numbers = row_numbers
        self.__fields_match = fields_match
        self.__labels = labels
        self.__errors: List[errors.HeaderError] = []
        self.__expected_fields: Optional[List[Field]] = None
        self.__matching = LabelMatching(
            labels,
            self.__fields,
            ignore_case=ignore_case,
            by_name=self.__matches_by_name,
        )
        self.__process()

    @cached_property
    def labels(self):
        """
        Returns:
            str[]: the header row as read from the data source
        """
        return self.__labels

    @cached_property
    def fields(self):
        """
        Returns:
            Field[]: copies of the schema fields, in schema order
        """
        return self.__fields

    @cached_property
    def field_names(self):
        """
        Returns:
            str[]: the names of the schema fields, in schema order
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

    # Fields match / expectations

    @property
    def __matches_by_name(self) -> bool:
        """Whether labels and fields are mapped by name rather than by order.

        Only `exact` maps them by order; every other `fieldsMatch` value maps
        them by name and differs from the others solely in which mismatches
        are tolerated.
        """
        return self.__fields_match != "exact"

    def get_expected_fields(self) -> List[Field]:
        """Returns the fields, in the order expected in the data.

        Each label gets the field it pairs with (by position when
        `fieldsMatch` is `"exact"`, by name otherwise), a label
        with no field gets an artificial `any`-typed
        field named after it (so that it is reported once rather than once per
        row), and fields no label pairs with are dropped.

        Under the name-matched modes, duplicate labels are rejected, as they make
        the pairing ambiguous. Under `exact`, fabricated `any`-typed field
        names are deduplicated.
        """
        if self.__expected_fields is not None:
            return self.__expected_fields

        if self.missing:
            self.__expected_fields = self.__fields
            return self.__expected_fields

        if self.__matches_by_name:
            # ignore_case can make fields ambiguous as their keys are identical,
            # e.g. "A" and "a"
            for group in self.__matching.ambiguous_fields:
                names = ", ".join(f'"{field.name}"' for field in group)
                note = (
                    f'matching fields by name ("fieldsMatch": "{self.__fields_match}") '
                    f"is ambiguous: fields {names} differ only by case, which "
                    '"header_case" is set to ignore'
                )
                raise FrictionlessException(errors.MetadataError(note=note))

            if self.__matching.has_duplicate_labels:
                note = (
                    f'matching fields by name ("fieldsMatch": "{self.__fields_match}") '
                    "requires unique labels in the header"
                )
                raise FrictionlessException(note)

        matched = [
            self.__matching.matching_field(position, label)
            for position, label in enumerate(self.__labels)
        ]

        # A fabricated field is named after its label, deduplicated if needed.
        # Matched fields are already unique and come first, so deduplication will only rename
        # fabricated fields.
        names = deduplicate_names(
            [
                field.name if field is not None else label
                for field, label in zip(matched, self.__labels)
            ]
        )
        self.__expected_fields = [
            (
                field
                if field is not None
                else Field.from_descriptor({"name": name, "type": "any"})
            )
            for field, name in zip(matched, names)
        ]
        return self.__expected_fields

    def _get_extra_labels(self) -> List[Tuple[int, str]]:
        """Returns (field_number, label) pairs for labels in the data that
        pair with no schema field: the labels beyond the schema's field count
        under `exact`, the labels whose name matches no field under name
        matching.

        `subset` and `partial` accept extra labels, so they report none.
        """
        if self.__fields_match in TOLERATES_EXTRA_LABELS:
            return []

        return [
            (number, label)
            for number, label in enumerate(self.__labels, start=1)
            if self.__matching.matching_field(number - 1, label) is None
        ]

    def _get_missing_fields(self) -> List[Tuple[int, Field]]:
        """Returns (field_number, field) pairs for schema fields that pair
        with no label: the fields beyond the labels count when `fieldsMatch`
        is `"exact"`, the fields whose name is not among the labels under name matching —
        restricted to the required ones for `superset` and `partial`, which
        otherwise accept a data source with fewer fields.

        The field_number is `len(labels) + offset + 1` in every mode: under
        `exact` the missing fields are precisely the tail of the schema, so
        this matches their position; under name matching the missing fields
        have no natural position in the data, so we place them after the
        labels by convention.
        """

        def is_required(field: Field) -> bool:
            return field.required or (
                field.schema is not None and field.name in field.schema.primary_key
            )

        missing = self.__matching.unmatched_fields
        if self.__fields_match in TOLERATES_MISSING_FIELDS:
            missing = [field for field in missing if is_required(field)]

        start = len(self.__labels) + 1
        return [(start + offset, field) for offset, field in enumerate(missing)]

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
        for field_number, label in self._get_extra_labels():
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

        # Unmatched header
        if self.__fields_match == "partial" and fields and not self.__matching.has_match:
            self.__errors.append(
                errors.UnmatchedHeaderError(
                    note="",
                    labels=list(map(str, labels)),
                    row_numbers=self.__row_numbers,
                )
            )

        # Missing fields
        for field_number, field in self._get_missing_fields():
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
        # When fields are matched by name (not by position), the positional
        # comparisons below (blank label vs field at the same index, incorrect
        # label vs field name at the same index) don't apply. Duplicate labels
        # are still invalid, but they are rejected earlier by
        # get_expected_fields(), which raises a FrictionlessException — so
        # detecting them here would be redundant.
        if self.__matches_by_name:
            return

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
                if not self.__matching.matches(label, field):
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
