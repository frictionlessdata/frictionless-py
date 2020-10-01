from ..table import Table
from .. import config


def extract_table(
    source,
    *,
    # File
    scheme=None,
    format=None,
    hashing=None,
    encoding=None,
    compression=None,
    compression_path=None,
    # Control/Dialect/Query/Header
    control=None,
    dialect=None,
    query=None,
    headers=None,
    # Schema
    schema=None,
    sync_schema=False,
    patch_schema=False,
    # Infer
    infer_type=None,
    infer_names=None,
    infer_volume=config.DEFAULT_INFER_VOLUME,
    infer_confidence=config.DEFAULT_INFER_CONFIDENCE,
    infer_missing_values=config.DEFAULT_MISSING_VALUES,
    # Integrity
    onerror="ignore",
    lookup=None,
    # Extraction
    process=None,
    stream=False,
):
    """Extract table rows

    API      | Usage
    -------- | --------
    Public   | `from frictionless import extract_table`

    Parameters:

        source (any): Source of the file; can be in various forms.
            Usually, it's a string as `<scheme>://path/to/file.<format>`.
            It also can be, for example, an array of data arrays/dictionaries.

        scheme? (str): Scheme for loading the file (file, http, ...).
            If not set, it'll be inferred from `source`.

        format? (str): File source's format (csv, xls, ...).
            If not set, it'll be inferred from `source`.

        encoding? (str): An algorithm to hash data.
            It defaults to 'md5'.

        encoding? (str): Source encoding.
            If not set, it'll be inferred from `source`.

        compression? (str): Source file compression (zip, ...).
            If not set, it'll be inferred from `source`.

        compression_path? (str): A path within the compressed file.
            It defaults to the first file in the archive.

        control? (dict|Control): File control.
            For more infromation, please check the Control documentation.

        dialect? (dict|Dialect): Table dialect.
            For more infromation, please check the Dialect documentation.

        query? (dict|Query): Table query.
            For more infromation, please check the Query documentation.

        headers? (int|int[]|[int[], str]): Either a row
            number or list of row numbers (in case of multi-line headers) to be
            considered as headers (rows start counting at 1), or a pair
            where the first element is header rows and the second the
            header joiner.  It defaults to 1.

        schema? (dict|Schema): Table schema.
            For more infromation, please check the Schema documentation.

        sync_schema? (bool): Whether to sync the schema.
            If it sets to `True` the provided schema will be mapped to
            the inferred schema. It means that, for example, you can
            provide a subset of fileds to be applied on top of the inferred
            fields or the provided schema can have different order of fields.

        patch_schema? (dict): A dictionary to be used as an inferred schema patch.
            The form of this dictionary should follow the Schema descriptor form
            except for the `fields` property which should be a mapping with the
            key named after a field name and the values being a field patch.
            For more information, please check "Extracting Data" guide.

        infer_type? (str): Enforce all the inferred types to be this type.
            For more information, please check "Describing  Data" guide.

        infer_names? (str[]): Enforce all the inferred fields to have provided names.
            For more information, please check "Describing  Data" guide.

        infer_volume? (int): The amount of rows to be extracted as a samle.
            For more information, please check "Describing  Data" guide.
            It defaults to 100

        infer_confidence? (float): A number from 0 to 1 setting the infer confidence.
            If  1 the data is guaranteed to be valid against the inferred schema.
            For more information, please check "Describing  Data" guide.
            It defaults to 0.9

        infer_missing_values? (str[]): String to be considered as missing values.
            For more information, please check "Describing  Data" guide.
            It defaults to `['']`

        onerror? (ignore|warn|raise): Define behaviour if there is an error in the
            header or rows during the reading rows process.
            It defaults to `ignore`.

        lookup? (dict): The lookup is a special object providing relational information.
            For more information, please check "Extracting  Data" guide.

        process? (func): A row processor function.
            It should be in a form of `row -> result`

        stream? (bool): Return a row streams instead of loading into memory.
            It can be useful for a big data files.

    Returns:
        Row[]: an array/stream of rows

    """

    # Create table
    table = Table(
        source,
        # File
        scheme=scheme,
        format=format,
        hashing=hashing,
        encoding=encoding,
        compression=compression,
        compression_path=compression_path,
        # Control/Dialect/Query/Header
        control=control,
        dialect=dialect,
        query=query,
        headers=headers,
        # Schema
        schema=schema,
        sync_schema=sync_schema,
        patch_schema=patch_schema,
        # Infer
        infer_type=infer_type,
        infer_names=infer_names,
        infer_volume=infer_volume,
        infer_confidence=infer_confidence,
        # Integrity
        onerror=onerror,
        lookup=lookup,
    )

    # Extract table
    data = read_row_stream(table)
    data = (process(row) for row in data) if process else data
    return data if stream else list(data)


# Internal


def read_row_stream(table):
    with table as table:
        for row in table.row_stream:
            yield row
