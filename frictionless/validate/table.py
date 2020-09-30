from .. import config
from .. import errors
from .. import helpers
from .. import exceptions
from ..table import Table
from ..system import system
from ..report import Report, ReportTable


@Report.from_validate
def validate_table(
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
    # Validation
    checksum=None,
    extra_checks=None,
    pick_errors=None,
    skip_errors=None,
    limit_errors=None,
    limit_memory=config.DEFAULT_LIMIT_MEMORY,
):
    """Validate table

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_table`

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

        checksum? (dict): a checksum dictionary
        extra_checks? (list): a list of extra checks
        pick_errors? ((str|int)[]): pick errors
        skip_errors? ((str|int)[]): skip errors
        limit_errors? (int): limit errors
        limit_memory? (int): limit memory

    Returns:
        Report: validation report

    """

    # Create state
    checks = []
    partial = False
    task_errors = []
    table_errors = TableErrors(pick_errors, skip_errors, limit_errors)
    timer = helpers.Timer()

    # Create checks
    items = []
    items.append("baseline")
    items.append(("checksum", checksum))
    items.extend(extra_checks or [])
    create = system.create_check
    for item in items:
        p1, p2 = item if isinstance(item, (tuple, list)) else (item, None)
        check = p1(p2) if isinstance(p1, type) else create(p1, descriptor=p2)
        checks.append(check)

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
        infer_missing_values=infer_missing_values,
        # Lookup
        onerror=onerror,
        lookup=lookup,
    )

    # Open table
    try:
        table.open()
    except exceptions.FrictionlessException as exception:
        table_errors.append(exception.error, force=True)

    # Enter table
    if not table_errors:
        with table:

            # Prepare checks
            for check in checks:
                table_errors.register(check)
                check.connect(table)
                check.prepare()

            # Validate task
            for check in checks.copy():
                for error in check.validate_task():
                    task_errors.append(error)
                    if check in checks:
                        checks.remove(check)

            # Validate schema
            for check in checks:
                for error in check.validate_schema(table.schema):
                    table_errors.append(error)

            # Validate header
            if table.header:
                for check in checks:
                    for error in check.validate_header(table.header):
                        table_errors.append(error)

            # Validate rows
            for row in table.row_stream:

                # Validate row
                for check in checks:
                    for error in check.validate_row(row):
                        table_errors.append(error)

                # Limit errors
                if limit_errors and len(table_errors) >= limit_errors:
                    partial = True
                    break

                # Limit memory
                if limit_memory and not table.stats["rows"] % 100000:
                    memory = helpers.get_current_memory_usage()
                    if memory and memory > limit_memory:
                        note = f'exceeded memory limit "{limit_memory}MB"'
                        task_errors.append(errors.TaskError(note=note))
                        partial = True
                        break

            # Validate table
            if not partial:
                for check in checks:
                    for error in check.validate_table():
                        table_errors.append(error)

    # Return report
    return Report(
        time=timer.time,
        errors=task_errors,
        tables=[
            ReportTable(
                time=timer.time,
                scope=table_errors.scope,
                partial=partial,
                errors=table_errors,
                table=table,
            )
        ],
    )


# Internal


class TableErrors(list):
    def __init__(self, pick_errors, skip_errors, limit_errors):
        self.__pick_errors = set(pick_errors or [])
        self.__skip_errors = set(skip_errors or [])
        self.__limit_errors = limit_errors
        self.__scope = []

    @property
    def scope(self):
        return self.__scope

    def append(self, error, *, force=False):
        if not force:
            if self.__limit_errors:
                if len(self) >= self.__limit_errors:
                    return
            if not self.match(error):
                return
        super().append(error)

    def match(self, error):
        match = True
        if self.__pick_errors:
            match = False
            if error.code in self.__pick_errors:
                match = True
            if self.__pick_errors.intersection(error.tags):
                match = True
        if self.__skip_errors:
            match = True
            if error.code in self.__skip_errors:
                match = False
            if self.__skip_errors.intersection(error.tags):
                match = False
        return match

    def register(self, check):
        for error in check.possible_Errors:
            if not self.match(error):
                continue
            if error.code in self.__scope:
                continue
            self.__scope.append(error.code)
