import io
import re
import json
import time
import unicodecsv
from functools import partial
from slugify import slugify
from ..resource import Resource
from ..package import Package
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
        if name == "bigquery":
            return BigqueryStorage(**options)


# Storage


class BigqueryStorage(Storage):
    """BigQuery storage implementation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.bigquery import BigqueryStorage`

    Parameters:
        service (object): BigQuery `Service` object
        project (str): BigQuery project name
        dataset (str): BigQuery dataset name
        prefix? (str): prefix for all names

    """

    def __init__(self, service, project, dataset, prefix=""):
        self.__service = service
        self.__project = project
        self.__dataset = dataset
        self.__prefix = prefix

    def __iter__(self):
        names = []

        # Get response
        response = (
            self.__service.tables()
            .list(projectId=self.__project, datasetId=self.__dataset)
            .execute()
        )

        # Extract names
        for table in response.get("tables", []):
            table_id = table["tableReference"]["tableId"]
            name = self.__read_convert_name(table_id)
            if name is not None:
                names.append(name)

        return names

    # Read

    def read_resource(self, name):
        bq_name = self.__write_convert_name(name)

        # Check existence
        if not bq_name:
            note = f'Resource "{name}" does not exist'
            raise exceptions.FrictionlessException(errors.StorageError(note=note))

        # Get response
        response = (
            self.__service.tables()
            .get(
                projectId=self.__project,
                datasetId=self.__dataset,
                tableId=bq_name,
            )
            .execute()
        )

        # Create resource
        schema = self.__read_convert_schema(name, response["schema"])
        data = partial(self.__read_data_stream, name)
        resource = Resource(name=name, schema=schema, data=data)

        return resource

    def read_package(self, name):
        package = Package()
        for name in self:
            resource = self.read_resource(name)
            package.resources.append(resource)
        return package

    def __read_convert_name(self, bq_name):
        if bq_name.startswith(self.__prefix):
            return bq_name.replace(self.__prefix, "", 1)
        return None

    def __read_convert_schema(self, bq_schema):
        schema = Schema()

        # Fields
        for bq_field in bq_schema["fields"]:
            field_type = self.__read_convert_type(bq_field["type"])
            field = Field(name=bq_field["name"], type=field_type)
            if bq_field.get("mode", "NULLABLE") != "NULLABLE":
                field.required = True
            schema.fields.append(field)

        return schema

    def __read_convert_type(self, bq_type):

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
        if bq_type in mapping:
            return mapping[bq_type]

        # Not supported
        note = "Type %s is not supported" % type
        raise exceptions.FrictionlessException(errors.StorageError(note=note))

    # NOTE: can it be streaming?
    # NOTE: provide a proper sorting solution?
    def __read_data_stream(self, name):
        bq_name = self.__write_convert_name(name)

        # Get response
        response = (
            self.__service.tabledata()
            .list(projectId=self.__project, datasetId=self.__dataset, tableId=bq_name)
            .execute()
        )

        # Collect rows
        data = []
        for fields in response["rows"]:
            cells = [field["v"] for field in fields["f"]]
            data.append(cells)

        # Sort data
        data = sorted(
            data, key=lambda cells: cells[0] if cells[0] is not None else "null"
        )

        # Emit data
        yield from data

    # Write

    def write_package(self, package, *, force=False):
        existent_names = list(self)

        # Copy/infer package
        package = Package(package)
        package.infer()

        # Iterate resources
        for resource in package.resources:

            # Check existence
            if resource.name in existent_names:
                if not force:
                    note = f'Resource "{resource.name}" already exists'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                self.delete_resource(resource.name)

            # Prepare job body
            bq_name = self.__write_convert_name(resource.name)
            meta, fallbacks = self.write_convert_schema(resource.schema)
            body = {
                "tableReference": {
                    "projectId": self.__project,
                    "datasetId": self.__dataset,
                    "tableId": bq_name,
                },
                "schema": meta,
            }

            # Make request
            self.__service.tables().insert(
                projectId=self.__project, datasetId=self.__dataset, body=body
            ).execute()

    def __write_convert_name(self, name):
        return self.__prefix + name

    def __write_convert_schema(self, table):

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

    def __write_convert_type(self, type):

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

    def __write_row_stream(self, name, row_stream):

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

    # Delete

    def delete_resource(self, name, *, ignore=False):
        return self.delete_package([name], ignore=ignore)

    def delete_package(self, names, *, ignore=False):
        existent_names = list(self)

        # Iterater over buckets
        for name in names:

            # Check existent
            if name not in existent_names:
                if not ignore:
                    note = f'Table "{name}" does not exist'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                continue

            # Make delete request
            bq_name = self.__write_convert_name(name)
            self.__service.tables().delete(
                projectId=self.__project, datasetId=self.__dataset, tableId=bq_name
            ).execute()

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
