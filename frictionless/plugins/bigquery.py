import io
import re
import json
import time
import unicodecsv
from slugify import slugify
from ..resource import Resource
from ..storage import Storage
from ..plugin import Plugin
from ..schema import Schema
from ..field import Field
from .. import exceptions
from .. import helpers
from .. import errors


# Plugin


class BigqueryPlugin(Plugin):
    """Plugin for BigQuery

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.bigquery import BigqueryPlugin`

    """

    def create_storage(self, name, **options):
        pass


# Storage


class BigqueryStorage(Storage):
    """BigQuery storage implementation"""

    def __init__(self, service, project, dataset, prefix=""):
        self.__service = service
        self.__project = project
        self.__dataset = dataset
        self.__prefix = prefix
        self.__names = None
        self.__tables = {}
        self.__fallbacks = {}

    def __repr__(self):
        template = "Storage <{service}/{project}-{dataset}>"
        return template.format(
            service=self.__service, project=self.__project, dataset=self.__dataset
        )

    # Read

    def read_table_names(self):

        # No cached value
        if self.__names is None:

            # Get response
            response = (
                self.__service.tables()
                .list(projectId=self.__project, datasetId=self.__dataset)
                .execute()
            )

            # Extract buckets
            self.__names = []
            for table in response.get("tables", []):
                table_name = table["tableReference"]["tableId"]
                bucket = self.__mapper.restore_bucket(table_name)
                if bucket is not None:
                    self.__names.append(bucket)

        return self.__names

    def read_table(self, name):
        table = self.__tables.get(name)
        if table is None:
            table_id = self.write_table_convert_name(name)
            response = (
                self.__service.tables()
                .get(
                    projectId=self.__project,
                    datasetId=self.__dataset,
                    tableId=table_id,
                )
                .execute()
            )
            meta = response["schema"]
            table = self.read_convert_table(name, meta)
        return table

    def read_table_convert_name(self, name):
        if name.startswith(self.__prefix):
            return name.replace(self.__prefix, "", 1)
        return None

    def read_table_convert_table(self, meta):
        schema = Schema()

        # Fields
        for bq_field in meta["fields"]:
            field_type = self.read_table_convert_field_type(bq_field["type"])
            field = Field(name=bq_field["name"], type=field_type)
            if bq_field.get("mode", "NULLABLE") != "NULLABLE":
                field.required = True
            schema.fields.append(field)

        # Table
        table = Resource(name="table", schema=schema)
        return table

    def read_table_convert_field_type(self, type):

        # Mapping
        mapping = {
            "BOOLEAN": "boolean",
            "DATE": "date",
            "DATETIME": "datetime",
            "INTEGER": "integer",
            "FLOAT": "number",
            "STRING": "string",
            "TIME": "time",
        }

        # Return type
        if type in mapping:
            return mapping[type]

        # Not supported
        note = "Type %s is not supported" % type
        raise exceptions.FrictionlessException(errors.StorageError(note=note))

    def read_table_row_stream(self, name):

        # Get schema/data
        table = self.read_table(name)
        table_id = self.write_table_convert_name(table.name)
        response = (
            self.__service.tabledata()
            .list(projectId=self.__project, datasetId=self.__dataset, tableId=table_id)
            .execute()
        )

        # Collect rows
        rows = []
        for fields in response["rows"]:
            row = [field["v"] for field in fields["f"]]
            rows.append(row)

        # Sort rows
        # NOTE: provide proper sorting solution
        rows = sorted(rows, key=lambda row: row[0] if row[0] is not None else "null")

        # Emit rows
        for row in rows:
            #  row = self.__mapper.restore_row(row, schema=schema)
            yield row

    # Write

    def write_table(self, *tables, force=False):

        # Iterate over tables
        for table in tables:

            # Existent bucket
            if table.name in self.read_table_names():
                if not force:
                    note = f'Table "{table.name}" already exists'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                self.write_table_remove(table.name)

            # Prepare job body
            table_id = self.write_table_convert_name(table.name)
            meta, fallbacks = self.write_table_convert_table(table)
            body = {
                "tableReference": {
                    "projectId": self.__project,
                    "datasetId": self.__dataset,
                    "tableId": table_id,
                },
                "schema": meta,
            }

            # Make request
            self.__service.tables().insert(
                projectId=self.__project, datasetId=self.__dataset, body=body
            ).execute()

            # Add to descriptors/fallbacks
            self.__tables[table.name] = table
            self.__fallbacks[table.name] = fallbacks

        # Remove buckets cache
        self.__names = None

    def write_table_convert_name(self, name):
        return self.__prefix + name

    def write_table_convert_table(self, table):

        # Fields
        fields = []
        fallbacks = []
        schema = table.schema
        for index, field in enumerate(schema.fields):
            converted_type = self.convert_type(field.type)
            if not converted_type:
                converted_type = "STRING"
                fallbacks.append(index)
            mode = "NULLABLE"
            if field.required:
                mode = "REQUIRED"
            fields.append(
                {
                    "name": _slugify_field_name(field.name),
                    "type": converted_type,
                    "mode": mode,
                }
            )

        # Descriptor
        converted_descriptor = {
            "fields": fields,
        }

        return (converted_descriptor, fallbacks)

    def write_table_convert_field_type(self, type):
        """Convert type to BigQuery"""

        # Mapping
        mapping = {
            "any": "STRING",
            "array": None,
            "boolean": "BOOLEAN",
            "date": "DATE",
            "datetime": "DATETIME",
            "duration": None,
            "geojson": None,
            "geopoint": None,
            "integer": "INTEGER",
            "number": "FLOAT",
            "object": None,
            "string": "STRING",
            "time": "TIME",
            "year": "INTEGER",
            "yearmonth": None,
        }

        # Return type
        if type in mapping:
            return mapping[type]

        # Not supported
        note = "Type %s is not supported" % type
        raise exceptions.FrictionlessException(errors.StorageError(note=note))

    def write_table_remove(self, *names, ignore=False):

        # Iterater over buckets
        for name in names:

            # Check existent
            if name not in self.read_table_names():
                if not ignore:
                    note = f'Table "{name}" does not exist'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                continue

            # Remove from descriptors
            if name in self.__tables:
                del self.__tables[name]

            # Make delete request
            table_id = self.write_table_convert_name(name)
            self.__service.tables().delete(
                projectId=self.__project, datasetId=self.__dataset, tableId=table_id
            ).execute()

        # Remove tables cache
        self.__names = None

    def write_table_row_stream(self, name, row_stream):

        # Write buffer
        BUFFER_SIZE = 10000

        # Prepare schema, fallbacks
        table = self.read_table(name)
        schema = table.schema
        fallbacks = self.__fallbacks.get(name, [])

        # Write data
        rows_buffer = []
        for row in row_stream:
            row = self.__mapper.convert_row(row, schema=schema, fallbacks=fallbacks)
            rows_buffer.append(row)
            if len(rows_buffer) > BUFFER_SIZE:
                self.__write_rows_buffer(name, rows_buffer)
                rows_buffer = []
        if len(rows_buffer) > 0:
            self.__write_rows_buffer(name, rows_buffer)

    # Private

    def __write_rows_buffer(self, bucket, rows_buffer):
        http = helpers.import_from_plugin("apiclient.http", plugin="bigquery")

        # Attributes

        # Process data to byte stream csv
        bytes = io.BufferedRandom(io.BytesIO())
        writer = unicodecsv.writer(bytes, encoding="utf-8")
        for row in rows_buffer:
            writer.writerow(row)
        bytes.seek(0)

        # Prepare job body
        table_name = self.__mapper.convert_bucket(bucket)
        body = {
            "configuration": {
                "load": {
                    "destinationTable": {
                        "projectId": self.__project,
                        "datasetId": self.__dataset,
                        "tableId": table_name,
                    },
                    "sourceFormat": "CSV",
                }
            }
        }

        # Prepare job media body
        mimetype = "application/octet-stream"
        media_body = http.MediaIoBaseUpload(bytes, mimetype=mimetype)

        # Make request to Big Query
        response = (
            self.__service.jobs()
            .insert(projectId=self.__project, body=body, media_body=media_body)
            .execute()
        )
        self.__wait_response(response)

    def __wait_response(self, response):

        # Get job instance
        job = self.__service.jobs().get(
            projectId=response["jobReference"]["projectId"],
            jobId=response["jobReference"]["jobId"],
        )

        # Wait done
        while True:
            result = job.execute(num_retries=1)
            if result["status"]["state"] == "DONE":
                if result["status"].get("errors"):
                    errors = result["status"]["errors"]
                    note = "\n".join(error["message"] for error in errors)
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                break
            time.sleep(1)


# Internal


def _slugify_field_name(name):

    # Referene:
    # https://cloud.google.com/bigquery/docs/reference/v2/tables
    MAX_LENGTH = 128
    VALID_NAME = r"^[a-zA-Z_]\w{0,%d}$" % (MAX_LENGTH - 1)

    # Convert
    if not re.match(VALID_NAME, name):
        name = slugify(name, separator="_")
        if not re.match("^[a-zA-Z_]", name):
            name = "_" + name

    return name[:MAX_LENGTH]


def _uncast_value(value, field):
    # Eventially should be moved to:
    # https://github.com/frictionlessdata/tableschema-py/issues/161
    if isinstance(value, (list, dict)):
        value = json.dumps(value)
    else:
        value = str(value)
    return value
