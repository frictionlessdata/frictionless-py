import codecs
import chardet
from copy import copy, deepcopy
from typing import List, Dict
from .exception import FrictionlessException
from .system import system
from .layout import Layout
from .schema import Schema
from .field import Field
from . import settings
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

        sample_size? (int): The amount of rows to be extracted as a sample.
            It defaults to 100

        encoding_function? (func): A custom encoding function for the file.

        encoding_confidence? (float): Confidence value for encoding function.

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
    def buffer_size(self) -> int:
        """Returns buffer size of the detector. Default value is 10000.

        Returns:
            int: detector buffer size
        """
        return self.__buffer_size

    @buffer_size.setter
    def buffer_size(self, value: int):
        """Sets buffer size for detector.

        Parameters:
            value (int): detector buffer size
        """
        self.__buffer_size = value

    @property
    def sample_size(self) -> int:
        """Returns sample size of the detector. Default value is 100.

        Returns:
            int: detector sample size
        """
        return self.__sample_size

    @sample_size.setter
    def sample_size(self, value: int):
        """Sets sample size for detector.

        Parameters:
            value (int): detector sample size
        """
        self.__sample_size = value

    @property
    def encoding_function(self) -> any:
        """Returns detector custom encoding function

        Returns:
            any: detector custom encoding function
        """
        return self.__encoding_function

    @encoding_function.setter
    def encoding_function(self, value: any):
        """Sets detector custom encoding function for the resource to be read.

        Parameters:
            value (any): detector custom encoding function
        """
        self.__encoding_function = value

    @property
    def encoding_confidence(self) -> float:
        """Returns confidence value for detector encoding function.

        Returns:
            float: detector encoding function confidence
        """
        return self.__encoding_confidence

    @encoding_confidence.setter
    def encoding_confidence(self, value: float):
        """Sets confidence value for detector encoding function. Default value
        is None.

        Parameters:
            value (float): detector encoding function confidence
        """
        self.__encoding_confidence = value

    @property
    def field_type(self) -> str:
        """Returns field type of the detector. Default value is None.

        Returns:
            str: detector inferred field types
        """
        return self.__field_type

    @field_type.setter
    def field_type(self, value: str):
        """Sets field type for all inferred fields by the detector.

        Parameters:
            value (str): detector inferred field types
        """
        self.__field_type = value

    @property
    def field_names(self) -> List[str]:
        """Returns inferred field names list.

        Returns:
            str[]: detector inferred field names
        """
        return self.__field_names

    @field_names.setter
    def field_names(self, value: List[str]):
        """Sets field names for all inferred fields by the detector.

        Parameters:
            value (str[]): detector inferred field names
        """
        self.__field_names = value

    @property
    def field_confidence(self) -> float:
        """Returns detector inference confidence value. Default value is 0.9.

        Returns:
            float: detector inference confidence value
        """
        return self.__field_confidence

    @field_confidence.setter
    def field_confidence(self, value: float):
        """Sets inference confidence value for detector. Default value is 0.9.

        Parameters:
            value (float): detector inference confidence value
        """
        self.__field_confidence = value

    @property
    def field_float_numbers(self) -> bool:
        """Returns detector convert decimal to float flag value.

        Returns:
            bool: detector convert decimal to float flag
        """
        return self.__field_float_numbers

    @field_float_numbers.setter
    def field_float_numbers(self, value: bool):
        """Sets detector convert decimal to float flag.

        Parameters:
            value (bool): detector convert decimal to float flag
        """
        self.__field_float_numbers = value

    @property
    def field_missing_values(self) -> List[str]:
        """Returns detector fields missing values list.

        Returns:
            str[]: detector fields missing values list
        """
        return self.__field_missing_values

    @field_missing_values.setter
    def field_missing_values(self, value: List[str]):
        """Sets detector fields missing values list.

        Parameters:
            value (str[]): detector fields missing values list
        """
        self.__field_missing_values = value

    @property
    def schema_sync(self) -> bool:
        """Returns detector schema_sync flag value.

        Returns:
            bool: detector schema_sync flag value
        """
        return self.__schema_sync

    @schema_sync.setter
    def schema_sync(self, value: bool):
        """Sets detector schema_sync flag value. If set to true, it
        syncs provided schema's field order based on the header's
        field order.

        Parameters:
            value (bool): detector schema_sync flag value
        """
        self.__schema_sync = value

    @property
    def schema_patch(self) -> Dict:
        """Returns detector resource fields to change.

        Returns:
            Dict: detector resource fields to change
        """
        return self.__schema_patch

    @schema_patch.setter
    def schema_patch(self, value: Dict):
        """Sets detector resource fields to change.

        Parameters:
            value (Dict): detector resource fields to change
        """
        self.__schema_patch = value

    # Detect

    def detect_encoding(self, buffer, *, encoding=None):
        """Detect encoding from buffer

        Parameters:
            buffer (byte): byte buffer

        Returns:
            str: encoding
        """

        # User defined
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

            # This algorithm tries to find a header row
            # that is close to average sample width or use default one
            # We use it to eleminate initial rows that are comments/etc

            # Get header rows
            row_number = 0
            header_rows = settings.DEFAULT_HEADER_ROWS
            width = round(sum(widths) / len(widths))
            drift = max(round(width * 0.1), 1)
            match = list(range(width - drift, width + drift + 1))
            for row_position, cells in enumerate(sample, start=1):
                if layout.read_filter_rows(cells, row_position=row_position):
                    row_number += 1
                    if len(cells) in match:
                        header_rows = [row_number]
                        break

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

            # Prepare runners
            runners = []
            runner_fields = []  # we use shared fields
            for candidate in system.create_candidates():
                field = Field(candidate)
                if field.type == "number" and self.__field_float_numbers:
                    field.float_number = True
                runner_fields.append(field)
            for index, name in enumerate(names):
                runners.append([])
                for field in runner_fields:
                    runners[index].append({"field": field, "score": 0})

            # Infer fields
            fields = [None] * len(names)
            max_score = [len(fragment)] * len(names)
            treshold = len(fragment) * (self.__field_confidence - 1)
            for cells in fragment:
                for index, name in enumerate(names):
                    if fields[index] is not None:
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
                            field = runner["field"].to_copy()
                            field.name = name
                            field.schema = schema
                            fields[index] = field
                            break

            # Fill/set fields
            # For not inferred fields we use the "any" type field as a default
            for index, name in enumerate(names):
                if fields[index] is None:
                    fields[index] = Field(name=name, type="any", schema=schema)
            schema.fields = fields

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
            if self.__schema_sync:
                note = 'Duplicate labels in header is not supported with "schema_sync"'
                raise FrictionlessException(errors.GeneralError(note=note))
            note = "Schemas with duplicate field names are not supported"
            raise FrictionlessException(errors.SchemaError(note=note))

        return schema
