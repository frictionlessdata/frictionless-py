from ..resource import Resource
from ..table import Table
from .. import helpers
from .. import config


# TODO: support only_sample
def describe_resource(
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
    # Infer
    infer_type=None,
    infer_names=None,
    infer_volume=config.DEFAULT_INFER_VOLUME,
    infer_confidence=config.DEFAULT_INFER_CONFIDENCE,
    infer_missing_values=config.DEFAULT_MISSING_VALUES,
    # Description
    expand=False,
):
    """Describe the given source as a resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe_resource`

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

        expand? (bool): if `True` it will expand the metadata
            It defaults to `False`

    Returns:
        Resource: data resource

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
        # Control/Dilect/Query/Header
        control=control,
        dialect=dialect,
        query=query,
        headers=headers,
        # Infer
        infer_type=infer_type,
        infer_names=infer_names,
        infer_volume=infer_volume,
        infer_confidence=infer_confidence,
        infer_missing_values=infer_missing_values,
    )

    # Create resource
    with table as table:
        helpers.pass_through(table.data_stream)
        resource = Resource(
            name=helpers.detect_name(table.path),
            path=table.path,
            scheme=table.scheme,
            format=table.format,
            hashing=table.hashing,
            encoding=table.encoding,
            compression=table.compression,
            compression_path=table.compression_path,
            control=table.control,
            dialect=table.dialect,
            query=table.query,
            schema=table.schema,
            stats=table.stats,
            profile="tabular-data-resource",
            trusted=True,
        )

    # Inline resource
    if not isinstance(table.source, str):
        resource.data = table.source

    # Expand resource
    if expand:
        resource.expand()

    return resource
