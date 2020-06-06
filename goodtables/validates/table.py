import tabulator
import tableschema
from .. import config
from .. import helpers
from ..row import Row
from ..system import system
from ..headers import Headers
from ..errors import Error, TaskError
from ..report import Report, ReportTable
from ..checks import BaselineCheck, IntegrityCheck


@Report.catch
def validate_table(
    source,
    *,
    # Source
    scheme=None,
    format=None,
    encoding=None,
    compression=None,
    # Headers
    headers_row=1,
    headers_joiner=' ',
    # Fields
    pick_fields=None,
    skip_fields=None,
    limit_fields=None,
    offset_fields=None,
    # Rows
    pick_rows=None,
    skip_rows=None,
    limit_rows=None,
    offset_rows=None,
    # Schema
    schema=None,
    sync_schema=False,
    patch_schema=False,
    infer_type=None,
    infer_names=None,
    infer_sample=100,
    infer_confidence=0.75,
    # Integrity
    lookup=None,
    size=None,
    hash=None,
    # Validation
    pick_errors=None,
    skip_errors=None,
    limit_errors=1000,
    extra_checks=None,
    # Dialect
    **dialect
):
    """Validate table

    # Arguments
        source (any)

        scheme? (str)
        format? (str)
        encoding? (str)
        compression? (str)

        headers_row? (int | int[])
        headers_joiner? (str)

        pick_fields? ((int | str)[])
        skip_fields? ((int | str)[])
        limit_fields? (int)
        offset_fields? (int)

        pick_rows? ((int | str)[])
        skip_rows? ((int | str)[])
        limit_rows? (int)
        offset_rows? (int)

        schema? (str | dict)
        sync_schema? (bool)
        patch_schema? (dict)
        infer_type? (str)
        infer_names? (str[])
        infer_sample? (int)
        infer_confidence? (float)

        lookup? (dict)
        size? (int)
        hash? (str)

        pick_errors? (str[])
        skip_errors? (str[])
        limit_errors? (int)
        extra_checks? (list)

        **dialect (dict)

    # Returns
        Report

    """

    # Prepare state
    checks = []
    exited = False
    row_number = 0
    task_errors = []
    timer = helpers.Timer()
    errors = Errors(
        pick_errors=pick_errors, skip_errors=skip_errors, limit_errors=limit_errors
    )

    # Create stream
    stream = tabulator.Stream(
        source,
        scheme=scheme,
        format=format,
        encoding=encoding,
        compression=compression,
        headers=helpers.translate_headers(headers_row),
        multiline_headers_joiner=headers_joiner,
        pick_fields=helpers.translate_pick_fields(pick_fields),
        skip_fields=helpers.translate_skip_fields(skip_fields),
        limit_fields=limit_fields,
        offset_fields=offset_fields,
        pick_rows=helpers.translate_pick_rows(pick_rows),
        skip_rows=helpers.translate_skip_rows(skip_rows),
        limit_rows=limit_rows,
        offset_rows=offset_rows,
        sample_size=infer_sample,
        hashing_algorithm=helpers.parse_hashing_algorithm(hash),
        **dialect
    )

    # Open stream
    try:
        stream.open()
        if not stream.sample:
            message = 'There are no rows available'
            raise tabulator.exceptions.SourceError(message)
    except Exception as exception:
        errors.add(Error.from_exception(exception))
        exited = True

    # Create schema
    try:
        schema = tableschema.Schema(schema or {})
    except tableschema.exceptions.TableSchemaException as exception:
        errors.add(Error.from_exception(exception))
        schema = None
        exited = True

    # Prepare schema
    if not exited:

        # Infer schema
        if schema and not schema.fields:
            infer_headers = stream.headers
            if not infer_headers:
                infer_headers = infer_names
            if not infer_headers:
                field_numbers = list(range(1, len(stream.sample[0]) + 1))
                infer_headers = ['field%s' % number for number in field_numbers]
            if infer_type:
                schema.descriptor['fields'] = []
                schema.descriptor['missingValues'] = config.MISSING_VALUES
                for header in infer_headers:
                    field = {'name': header, 'type': infer_type, 'format': 'default'}
                    schema.descriptor['fields'].append(field)
                schema.commit()
            else:
                schema.infer(
                    stream.sample, headers=infer_headers, confidence=infer_confidence
                )

        # Sync schema
        if schema and sync_schema:
            new_fields = []
            old_fields = schema.descriptor.get('fields', [])
            map_fields = {field.get('name'): field for field in old_fields}
            for header in stream.headers:
                field = map_fields.get(header)
                if field:
                    new_fields.append(field)
            schema.descriptor['fields'] = new_fields
            schema.commit()

        # Patch schema
        if schema and patch_schema:
            fields = patch_schema.pop('fields', {})
            schema.descriptor.update(patch_schema)
            for field in schema.descriptor['fields']:
                field.update((fields.get(field.get('name'), {})))
            schema.commit()

        # Validate schema
        if schema and schema.errors:
            for error in schema.errors:
                errors.add(Error.from_exception(error))
            schema = None
            exited = True

        # Confirm schema
        if schema and len(schema.field_names) != len(set(schema.field_names)):
            message = 'Schemas with duplicate field names are not supported'
            error = tableschema.exceptions.TableSchemaException(message)
            errors.add(Error.from_exception(error))
            schema = None
            exited = True

    # Create checks
    if not exited:
        Checks = []
        Checks.append(BaselineCheck)
        Checks.append((IntegrityCheck, {'size': size, 'hash': hash}))
        Checks.extend(extra_checks or [])
        for Check in Checks:
            Check = Check if isinstance(Check, (tuple, list)) else (Check, None)
            check = system.create_check(Check[0], descriptor=Check[1])
            check.connect(stream=stream, schema=schema)
            check.prepare()
            checks.append(check)
            errors.register(check)

    # Validate task
    if not exited:
        for check in checks.copy():
            for error in check.validate_task():
                task_errors.append(error)
                if check in checks:
                    checks.remove(check)

    # Validate headers
    if not exited:
        if stream.headers:

            # Get headers
            headers = Headers(
                stream.headers,
                fields=schema.fields,
                field_positions=stream.field_positions,
            )

            # Validate headers
            for check in checks:
                for error in check.validate_headers(headers):
                    errors.add(error)

    # Validate rows
    if not exited:
        fields = schema.fields
        iterator = stream.iter(extended=True)
        field_positions = stream.field_positions
        if not field_positions:
            field_positions = list(range(1, len(schema.fields) + 1))
        while True:

            # Read cells
            try:
                row_position, _, cells = next(iterator)
            except StopIteration:
                break
            except Exception as exception:
                errors.add(Error.from_exception(exception))
                exited = True
                break

            # Create row
            row_number += 1
            row = Row(
                cells,
                fields=fields,
                field_positions=field_positions,
                row_position=row_position,
                row_number=row_number,
            )

            # Validate row
            for check in checks:
                for error in check.validate_row(row):
                    errors.add(error)

            # Limit errors
            if limit_errors and len(errors) >= limit_errors:
                details = 'source "%s" reached the error limit "%s"'
                details = details % (source, limit_errors)
                task_errors.append(TaskError(details=details))
                break

    # Validate table
    if not exited:
        for check in checks:
            for error in check.validate_table():
                errors.add(error)

    # Return report
    time = timer.get_time()
    if schema:
        schema = schema.descriptor
    return Report(
        time=time,
        errors=task_errors,
        tables=[
            ReportTable(
                time=time,
                scope=errors.scope,
                row_count=row_number,
                source=str(stream.source),
                scheme=stream.scheme,
                format=stream.format,
                encoding=stream.encoding,
                compression=stream.compression,
                headers=stream.headers,
                headers_row=headers_row,
                headers_joiner=headers_joiner,
                pick_fields=pick_fields,
                skip_fields=skip_fields,
                limit_fields=limit_fields,
                offset_fields=offset_fields,
                pick_rows=pick_rows,
                skip_rows=skip_rows,
                limit_rows=limit_rows,
                offset_rows=offset_rows,
                schema=schema,
                dialect=dialect,
                errors=errors,
            )
        ],
    )


# Internal


class Errors(list):
    def __init__(self, *, pick_errors=None, skip_errors=None, limit_errors=None):
        self.__pick_errors = set(pick_errors or [])
        self.__skip_errors = set(skip_errors or [])
        self.__limit_errors = limit_errors
        self.__scope = []

    @property
    def scope(self):
        return self.__scope

    def add(self, error):
        if self.__limit_errors:
            if len(self) >= self.__limit_errors:
                return
        if not self.match(error):
            return
        self.append(error)

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
