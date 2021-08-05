import codecs
import chardet
from copy import copy, deepcopy
from .exception import FrictionlessException
from .system import system
from .layout import Layout
from .schema import Schema
from .field import Field
from . import settings
from . import helpers
from . import errors


# NOTE:
# We might consider making this class instalce of Metadata
# It will alow providing detector options declaratively e.g. in validation Inquiry


class Detector:
    """Detector representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Detector`

    Parameters:

        buffer_size? (int): The amount of bytes to be extracted as a buffer.
            It defaults to 10000

        sample_size? (int): The amount of rows to be extracted as a samle.
            It defaults to 100

        field_type? (str): Enforce all the inferred types to be this type.
            For more information, please check "Describing  Data" guide.

        field_names? (str[]): Enforce all the inferred fields to have provided names.
            For more information, please check "Describing  Data" guide.

        field_confidence? (float): A number from 0 to 1 setting the infer confidence.
            If  1 the data is guaranteed to be valid against the inferred schema.
            For more information, please check "Describing  Data" guide.
            It defaults to 0.9

        field_float_numbers? (bool): Flag to indicate desired number type.
            By default numbers will be `Decimal`; if `True` - `float`.
            For more information, please check "Describing  Data" guide.
            It defaults to `False`

        field_missing_values? (str[]): String to be considered as missing values.
            For more information, please check "Describing  Data" guide.
            It defaults to `['']`

        schema_sync? (bool): Whether to sync the schema.
            If it sets to `True` the provided schema will be mapped to
            the inferred schema. It means that, for example, you can
            provide a subset of fileds to be applied on top of the inferred
            fields or the provided schema can have different order of fields.

        schema_patch? (dict): A dictionary to be used as an inferred schema patch.
            The form of this dictionary should follow the Schema descriptor form
            except for the `fields` property which should be a mapping with the
            key named after a field name and the values being a field patch.
            For more information, please check "Extracting Data" guide.
    """

    def __init__(
        self,
        buffer_size=settings.DEFAULT_BUFFER_SIZE,
        sample_size=settings.DEFAULT_SAMPLE_SIZE,
        encoding_function=None,
        encoding_confidence=settings.DEFAULT_ENCODING_CONFIDENCE,
        field_type=None,
        field_names=None,
        field_confidence=settings.DEFAULT_FIELD_CONFIDENCE,
        field_float_numbers=settings.DEFAULT_FLOAT_NUMBERS,
        field_missing_values=settings.DEFAULT_MISSING_VALUES,
        schema_sync=False,
        schema_patch=None,
    ):
        self.__buffer_size = buffer_size
        self.__sample_size = sample_size
        self.__encoding_function = encoding_function
        self.__encoding_confidence = encoding_confidence
        self.__field_type = field_type
        self.__field_names = field_names
        self.__field_confidence = field_confidence
        self.__field_float_numbers = field_float_numbers
        self.__field_missing_values = field_missing_values
        self.__schema_sync = schema_sync
        self.__schema_patch = schema_patch

    @property
    def buffer_size(self):
        return self.__buffer_size

    @property
    def sample_size(self):
        return self.__sample_size

    # Detect

    def detect_encoding(self, buffer, *, encoding=None):
        """Detect encoding from buffer

        Parameters:
            buffer (byte): byte buffer

        Returns:
            str: encoding
        """

        # Use defined
        if self.__encoding_function:
            return self.__encoding_function(buffer)

        # Detect encoding
        if not encoding:
            detector = chardet.UniversalDetector()
            for line in buffer.splitlines():
                detector.feed(line)
            detector.close()
            encoding = detector.result["encoding"] or settings.DEFAULT_ENCODING
            confidence = detector.result["confidence"] or 0
            if confidence < self.__encoding_confidence:
                encoding = settings.DEFAULT_ENCODING
            if encoding == "ascii":
                encoding = settings.DEFAULT_ENCODING
            if encoding is None:
                encoding = self.resource.detector.detect_encoding(buffer)

        # Normalize encoding
        encoding = codecs.lookup(encoding).name
        # Work around for incorrect inferion of utf-8-sig encoding
        if encoding == "utf-8":
            if buffer.startswith(codecs.BOM_UTF8):
                encoding = "utf-8-sig"
        # Use the BOM stripping name (without byte-order) for UTF-16 encodings
        elif encoding == "utf-16-be":
            if buffer.startswith(codecs.BOM_UTF16_BE):
                encoding = "utf-16"
        elif encoding == "utf-16-le":
            if buffer.startswith(codecs.BOM_UTF16_LE):
                encoding = "utf-16"

        return encoding

    def detect_layout(self, sample, *, layout=None):
        """Detect layout from sample

        Parameters:
            sample (any[][]): data sample
            layout? (Layout): data layout

        Returns:
            Layout: layout
        """
        layout = layout or Layout()

        # Infer header
        widths = [len(cells) for cells in sample]
        if layout.get("header") is None and layout.get("headerRows") is None and widths:

            # This algorithm tries to find a header row that:
            # - is close to average sample width
            # - doesn't have bad labels (non-string cells) OR
            # - have less bad labels (non-string cells) than the next row

            # Get header rows
            row_number = 0
            bad_labels = 0
            header_rows = None
            width = round(sum(widths) / len(widths))
            drift = max(round(width * 0.1), 1)
            match = list(range(width - drift, width + drift + 1))
            for row_position, cells in enumerate(sample, start=1):
                if layout.read_filter_rows(cells, row_position=row_position):
                    row_number += 1
                    if len(cells) in match:
                        row_bad_labels = helpers.count_bad_labels(cells)
                        if not row_bad_labels:
                            header_rows = [row_number]
                            break
                        elif bad_labels and bad_labels < row_bad_labels:
                            header_rows = [row_number - 1]
                            break
                        bad_labels = row_bad_labels

            # Set header rows
            if not header_rows:
                layout["header"] = False
            elif header_rows != settings.DEFAULT_HEADER_ROWS:
                layout["headerRows"] = header_rows

        return layout

    def detect_schema(self, fragment, *, labels=None, schema=None):
        """Detect schema from fragment

        Parameters:
            fragment (any[][]): data fragment
            labels? (str[]): data labels
            schema? (Schema): data schema

        Returns:
            Schema: schema
        """

        # Create schema
        if not schema or not schema.fields:
            schema = Schema()

            # Missing values
            if self.__field_missing_values != settings.DEFAULT_MISSING_VALUES:
                schema.missing_values = self.__field_missing_values

            # Prepare names
            names = copy(self.__field_names or labels or [])
            names = list(map(lambda cell: cell.replace("\n", " ").strip(), names))
            if not names:
                if not fragment:
                    return schema
                names = [f"field{number}" for number in range(1, len(fragment[0]) + 1)]

            # Handle name/empty
            for index, name in enumerate(names):
                names[index] = name or f"field{index+1}"

            # Deduplicate names
            if len(names) != len(set(names)):
                seen_names = []
                names = names.copy()
                for index, name in enumerate(names):
                    count = seen_names.count(name) + 1
                    names[index] = "%s%s" % (name, count) if count > 1 else name
                    seen_names.append(name)

            # Handle type/empty
            if self.__field_type or not fragment:
                type = self.__field_type
                schema.fields = [{"name": name, "type": type or "any"} for name in names]
                return schema

            # Prepare fields
            runners = []
            max_score = [len(fragment)] * len(names)
            for index, name in enumerate(names):
                runners.append([])
                for candidate in system.create_candidates():
                    field = Field(candidate, name=name, schema=schema)
                    if field.type == "number" and self.__field_float_numbers:
                        field.float_number = True
                    runners[index].append({"field": field, "score": 0})
                schema.fields.append(Field(name=name, type="any", schema=schema))

            # Infer fields
            treshold = len(fragment) * (self.__field_confidence - 1)
            for cells in fragment:
                for index, name in enumerate(names):
                    if schema.fields[index].type != "any":
                        continue
                    source = cells[index] if len(cells) > index else None
                    if source in self.__field_missing_values:
                        max_score[index] -= 1
                        continue
                    for runner in runners[index]:
                        if runner["score"] < treshold:
                            continue
                        target, notes = runner["field"].read_cell(source)
                        runner["score"] += 1 if not notes else -1
                        if runner["score"] >= max_score[index] * self.__field_confidence:
                            schema.fields[index] = runner["field"]
                            break

        # Sync schema
        if self.__schema_sync:
            if labels:
                fields = []
                mapping = {field.get("name"): field for field in schema.fields}
                for name in labels:
                    fields.append(mapping.get(name, {"name": name, "type": "any"}))
                schema.fields = fields

        # Patch schema
        if self.__schema_patch:
            schema_patch = deepcopy(self.__schema_patch)
            fields = schema_patch.pop("fields", {})
            schema.update(schema_patch)
            for field in schema.fields:
                field.update((fields.get(field.get("name"), {})))

        # Validate schema
        # NOTE: at some point we might need to remove it for transform needs
        if len(schema.field_names) != len(set(schema.field_names)):
            note = "Schemas with duplicate field names are not supported"
            raise FrictionlessException(errors.SchemaError(note=note))

        return schema
