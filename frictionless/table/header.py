from __future__ import annotations

import warnings
from functools import cached_property
from typing import Any, Iterator, List, Optional, Tuple

from .. import errors, helpers, types
from ..exception import FrictionlessException
from ..schema import Field

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

    > Deprecated: using a `Header` directly as a list is deprecated, as the list
    > ambiguously holds the names of the *schema* fieldss. Use its properties instead:
    > `labels` for the header row as read from the data source, `fields`/`field_names`
    > for the schema fields.

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
        field_names = [field.name for field in fields]
        super().__init__(field_names)
        self.__fields: List[Field] = []
        for field in fields:
            copy = field.to_copy()
            # to_copy() goes through the descriptor and drops the back-reference
            # to the schema; restore it so checks like "field belongs to schema's
            # primary_key" remain accurate.
            copy.schema = field.schema
            self.__fields.append(copy)
        self.__field_names = field_names
        self.__row_numbers = row_numbers
        self.__ignore_case = ignore_case
        self.__fields_match = fields_match
        self.__labels = labels
        self.__errors: List[errors.HeaderError] = []
        self.__expected_fields: Optional[List[Field]] = None
        self.__process()

    # Deprecated

    def __warn_list_usage(self, usage: str) -> None:
        warnings.warn(
            f"Using a Header as a list ({usage}) is deprecated, as the list "
            "ambiguously holds the names of the schema fields. Use "
            "`header.field_names` instead, or `header.labels` for the header "
            "row as read from the data source.",
            DeprecationWarning,
            stacklevel=3,
        )

    def __eq__(self, other: Any) -> bool:
        self.__warn_list_usage("==")
        return super().__eq__(other)

    def __getitem__(self, index: Any) -> Any:
        self.__warn_list_usage("[]")
        return super().__getitem__(index)

    def __iter__(self) -> Iterator[str]:
        self.__warn_list_usage("iteration")
        return super().__iter__()

    def __len__(self) -> int:
        self.__warn_list_usage("len()")
        return super().__len__()

    def __contains__(self, item: Any) -> bool:
        self.__warn_list_usage("in")
        return super().__contains__(item)

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

        Under `exact`, this is just the schema fields unchanged.

        Under the name-matched modes, fields are reordered to match the labels;
        labels without a matching field get a fresh `any`-typed field (even
        where such a label is an error, so that it is reported once rather than
        once per row), and fields not present in labels are dropped. Duplicate
        labels are rejected, as they make the mapping ambiguous.
        """
        if self.__expected_fields is not None:
            return self.__expected_fields

        if not self.__matches_by_name:
            self.__expected_fields = self.__fields
            return self.__expected_fields

        if len(self.__labels) != len(set(self.__labels)):
            note = (
                f'matching fields by name ("fieldsMatch": "{self.__fields_match}") '
                "requires unique labels in the header"
            )
            raise FrictionlessException(note)

        expected: List[Field] = []
        for label in self.__labels:
            field = self.__find_field_by_name(label)
            if field is None:
                field = Field.from_descriptor({"name": label, "type": "any"})
            expected.append(field)
        self.__expected_fields = expected
        return self.__expected_fields

    def _get_extra_labels(self) -> List[Tuple[int, str]]:
        """Returns (field_number, label) pairs for labels in the data that
        don't correspond to any schema field.

        Under `exact`, the extras are the labels beyond the schema's field
        count. Under name matching, an extra label is one whose name matches no
        field.

        `subset` and `partial` accept extra labels, so they report none.
        """
        labels = self.__labels

        if not self.__matches_by_name:
            return [
                (number, label)
                for number, label in enumerate(labels, start=1)
                if number > len(self.__fields)
            ]

        if self.__fields_match in TOLERATES_EXTRA_LABELS:
            return []

        return [
            (number, label)
            for number, label in enumerate(labels, start=1)
            if self.__find_field_by_name(label) is None
        ]

    def _get_missing_fields(self) -> List[Tuple[int, Field]]:
        """Returns (field_number, field) pairs for schema fields that don't
        have a corresponding label.

        Under `exact`, the missing fields are those beyond the labels count.
        Under name matching, they are the fields whose name is not among the
        labels — restricted to the required ones for `superset` and `partial`,
        which otherwise accept a data source with fewer fields.

        The field_number is `len(labels) + offset + 1` in every mode: under
        `exact` the missing fields are precisely the tail of the schema, so
        this matches their position; under name matching the missing fields
        have no natural position in the data, so we place them after the
        labels by convention.
        """
        fields = self.__fields
        labels = self.__labels

        if not self.__matches_by_name:
            missing = fields[len(labels) :] if len(fields) > len(labels) else []
        else:
            normalized_labels = [self.__normalize(label) for label in labels]

            def is_absent(field: Field) -> bool:
                return self.__normalize(field.name) not in normalized_labels

            def is_required(field: Field) -> bool:
                return field.required or (
                    field.schema is not None and field.name in field.schema.primary_key
                )

            missing = [field for field in fields if is_absent(field)]
            if self.__fields_match in TOLERATES_MISSING_FIELDS:
                missing = [field for field in missing if is_required(field)]

        start = len(labels) + 1
        return [(start + offset, field) for offset, field in enumerate(missing)]

    def __has_matching_field(self) -> bool:
        """Whether at least one label corresponds to a schema field"""
        return any(
            self.__find_field_by_name(label) is not None for label in self.__labels
        )

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
        """Convert to a list of the schema field names"""
        return list(self.__field_names)

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
        if (
            self.__fields_match == "partial"
            and fields
            and not self.__has_matching_field()
        ):
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
