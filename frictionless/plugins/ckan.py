import os
import json
import logging
import requests
from ..field import Field
from ..schema import Schema
from ..plugin import Plugin
from ..storage import Storage
from ..resource import Resource
from .. import exceptions
from .. import errors

log = logging.getLogger(__name__)


# Plugin


class CkanPlugin(Plugin):
    """Plugin for CKAN

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ckan import CkanPlugin`
    """

    def create_dialect(self, resource, *, descriptor):
        pass

    def create_parser(self, resource):
        pass

    def create_storage(self, name, **options):
        pass


# TODO: implement Dialect
# TODO: implement Parser


# Storage


class CkanStorage(Storage):
    """Ckan storage implementation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ckan import CkanStorage`
    """

    def __init__(self, base_url, dataset_id=None, api_key=None):
        base_path = "/api/3/action"
        self.__base_url = base_url.rstrip("/")
        self.__base_endpoint = self.__base_url + base_path
        self.__dataset_id = dataset_id
        self.__api_key = api_key
        self.__max_pages = 100
        self.__bucket_cache = None
        self.__tables = {}

    # Read

    @property
    def read_table_names(self):
        if self.__bucket_cache:
            return self.__bucket_cache
        params = {"resource_id": "_table_metadata"}
        if self.__dataset_id is not None:
            filter_ids = self.__get_resource_ids_for_dataset(self.__dataset_id)
            params.update({"filters": json.dumps({"name": filter_ids})})
        datastore_search_url = "{}/datastore_search".format(self.__base_endpoint)
        response = self.__make_ckan_request(datastore_search_url, params=params)
        names = [r["name"] for r in response["result"]["records"]]
        count = 1
        while response["result"]["records"]:
            count += 1
            next_url = self.__base_url + response["result"]["_links"]["next"]
            response = self.__make_ckan_request(next_url)
            records = response["result"]["records"]
            if records:
                names = names + [r["name"] for r in response["result"]["records"]]
            if count == self.__max_pages:
                log.warn("Max name count exceeded. {} names returned.".format(len(names)))
                break
        self.__name_cache = names
        return names

    def read_table(self, name):
        table = self.__table.get(name)
        if table is None:
            datastore_search_url = "{}/datastore_search".format(self.__base_endpoint)
            params = {"limit": 0, "resource_id": name}
            response = self.__make_ckan_request(datastore_search_url, params=params)
            ckan_table = response["result"]["fields"]
            table = self.read_table_convert_table(name, ckan_table)
        return table

    def read_table_convert_table(self, name, ckan_table):
        schema = Schema()

        # Fields
        for f in ckan_table:
            # Don't include datastore internal field '_id'.
            if f["id"] == "_id":
                continue
            datastore_type = f["type"]
            datastore_id = f["id"]
            ts_type, ts_format = self.datastore_field_type_to_schema_type(datastore_type)
            field = Field(name=datastore_id, type=ts_type)
            if ts_format is not None:
                field.format = ts_format
            schema.fields.append(field)

        # Table
        table = Resource(name=name, schema=schema)
        return table

    def read_table_convert_field_type(self, dstore_type):
        dstore_type = dstore_type.rstrip("0123456789")
        if dstore_type.startswith("_"):
            dstore_type = "array"
        DATASTORE_TYPE_MAPPING = {
            "int": ("integer", None),
            "float": ("number", None),
            "smallint": ("integer", None),
            "bigint": ("integer", None),
            "integer": ("integer", None),
            "numeric": ("number", None),
            "money": ("number", None),
            "timestamp": ("datetime", "any"),
            "date": ("date", "any"),
            "time": ("time", "any"),
            "interval": ("duration", None),
            "text": ("string", None),
            "varchar": ("string", None),
            "char": ("string", None),
            "uuid": ("string", "uuid"),
            "boolean": ("boolean", None),
            "bool": ("boolean", None),
            "json": ("object", None),
            "jsonb": ("object", None),
            "array": ("array", None),
        }
        try:
            return DATASTORE_TYPE_MAPPING[dstore_type]
        except KeyError:
            log.warn(
                "Unsupported DataStore type '{}'. Using 'string'.".format(dstore_type)
            )
            return ("string", None)

    def read_table_row_stream(self, name):
        table = self.read_table(name)
        datastore_search_url = "{}/datastore_search".format(self.__base_endpoint)
        params = {"resource_id": table.name}
        response = self.__make_ckan_request(datastore_search_url, params=params)
        while response["result"]["records"]:
            for row in response["result"]["records"]:
                #  row = self.__mapper.restore_row(row, schema=table.schema)
                yield row
            next_url = self.__base_url + response["result"]["_links"]["next"]
            response = self.__make_ckan_request(next_url)

    # Write

    def write_table(self, *tables, force=False):

        # Check for existence
        for table in tables:
            if table.name in self.read_table_names():
                if not force:
                    note = f'Table "{table.name}" already exists'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                self.write_table_remove(table.name)

        # Define tables
        for table in tables:
            self.__tables[table.name] = table
            datastore_dict = self.write_table_convert_table(table)
            datastore_url = "{}/datastore_create".format(self.__base_endpoint)
            self.__make_ckan_request(datastore_url, method="POST", json=datastore_dict)

        # Invalidate cache
        self.__bucket_cache = None

    def write_table_remove(self, *names, ignore=False):

        # Remove tables
        for name in names:

            # Check existent
            if name not in self.read_table_names():
                if not ignore:
                    note = f'Table "{name}" already exists'
                    raise exceptions.FrictionlessException(errors.StorageError(note=note))
                continue

            # Remove from table
            if name in self.__tables:
                del self.__tables[name]

            # Remove from ckan
            datastore_delete_url = "{}/datastore_delete".format(self.__base_endpoint)
            params = {"resource_id": name, "force": True}
            self.__make_ckan_request(datastore_delete_url, method="POST", json=params)

        # Invalidate cache
        self.__bucket_cache = None

    def write_table_convert_table(self, table):
        schema = table.schema
        datastore_dict = {"fields": [], "resource_id": table.name, "force": True}
        for field in schema.fields:
            datastore_field = {"id": field.name}
            datastore_type = self.descritor_type_to_datastore_type(field.type)
            if datastore_type:
                datastore_field["type"] = datastore_type
            datastore_dict["fields"].append(datastore_field)
        if schema.primary_key is not None:
            datastore_dict["primary_key"] = schema.primary_key
        return datastore_dict

    def write_table_convert_field_type(self, type):
        DESCRIPTOR_TYPE_MAPPING = {
            "number": "float",
            "string": "text",
            "integer": "int",
            "boolean": "bool",
            "object": "json",
            "array": "text[]",
            "geojson": "json",
            "date": "date",
            "time": "time",
            "year": "int",
            "datetime": "timestamp",
        }
        try:
            return DESCRIPTOR_TYPE_MAPPING[type]
        except KeyError:
            log.warn("Unsupported descriptor type '{}'.".format(type))
            return None

    def write_table_row_stream(self, name, row_stream, method="upsert"):
        table = self.read_table(name)
        datastore_upsert_url = "{}/datastore_upsert".format(self.__base_endpoint)
        records = []
        for r in row_stream:
            #  r = self.__mapper.convert_row(r, table.eschema)
            records.append(r)
        params = {
            "resource_id": table.name,
            "method": method,
            "force": True,
            "records": records,
        }
        self.__make_ckan_request(datastore_upsert_url, method="POST", json=params)

    # Private

    def __get_resource_ids_for_dataset(self, dataset_id):
        """Get a list of resource ids for the passed dataset id."""
        package_show_url = "{}/package_show".format(self.__base_endpoint)
        response = self.__make_ckan_request(package_show_url, params=dict(id=dataset_id))
        dataset = response["result"]
        resources = dataset["resources"]
        resource_ids = [r["id"] for r in resources]
        return resource_ids

    def __make_ckan_request(self, datastore_url, **kwargs):
        response = make_ckan_request(datastore_url, api_key=self.__api_key, **kwargs)
        ckan_error = get_ckan_error(response)
        if ckan_error:
            note = "CKAN returned an error: " + json.dumps(ckan_error)
            raise exceptions.FrictionlessException(errors.StorageError(note=note))
        return response


# Internal


def make_ckan_request(url, method="GET", headers=None, api_key=None, **kwargs):
    """Make a CKAN API request to `url` and return the json response. **kwargs
    are passed to requests.request()"""

    if headers is None:
        headers = {}

    if api_key:
        if api_key.startswith("env:"):
            api_key = os.environ.get(api_key[4:])
        headers.update({"Authorization": api_key})

    response = requests.request(
        method=method, url=url, headers=headers, allow_redirects=True, **kwargs
    )

    try:
        return response.json()
    except json.decoder.JSONDecodeError:
        log.error("Expected JSON in response from: {}".format(url))
        raise


def get_ckan_error(response):
    """Return the error from a ckan json response, or None."""
    ckan_error = None
    try:
        if not response["success"] and response["error"]:
            ckan_error = response["error"]
    except TypeError:
        ckan_error = response

    return ckan_error
