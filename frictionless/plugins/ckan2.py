import json
import logging
import os
from functools import partial
import requests
from ..exception import FrictionlessException
from ..field import Field
from ..package import Package
from ..plugin import Plugin
from ..resource import Resource
from ..schema import Schema
from ..storage import Storage
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
        if name == "ckan_datastore":
            return CkanStorage(**options)


# TODO: implement Dialect
# TODO: implement Parser


# Storage


class CkanStorage(Storage):
    """Ckan storage implementation

    Parameters:
        url (string): CKAN instance url e.g. "https://demo.ckan.org"
        dataset (string): dataset id in CKAN e.g. "my-dataset"
        apikey? (str): API key for CKAN e.g. "xxxxxxxxxxxxxxxxxxx"


    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ckan import CkanStorage`
    """

    def __init__(self, *, url, dataset, apikey=None):
        self.__endpoint = f'{url.rstrip("/")}/api/3/action'
        self.__dataset = dataset
        self.__apikey = apikey

    def __iter__(self):
        params = {"resource_id": "_table_metadata"}
        filter_ids = self.__get_resource_ids_for_dataset(self.__dataset)
        params.update({"filters": json.dumps({"name": filter_ids})})
        datastore_search_url = "{}/datastore_search".format(self.__endpoint)
        response = self.__make_ckan_request(datastore_search_url, params=params)
        names = [r["name"] for r in response["result"]["records"]]
        while response["result"]["records"]:
            next_url = self.__base_url + response["result"]["_links"]["next"]
            response = self.__make_ckan_request(next_url)
            records = response["result"]["records"]
            if records:
                names = names + [r["name"] for r in response["result"]["records"]]
        return iter(names)

    # Read

    def read_resource(self, name):
        ckan_table = self.__read_ckan_table(name)
        schema = self.__read_convert_schema(name, ckan_table)
        resource = Resource(
            name=name,
            schema=schema,
            data=partial(self.__read_convert_data, ckan_table),
            dialect={"keys": schema.field_names},
        )
        return resource

    def read_package(self, **options):
        package = Package()
        for name in self:
            resource = self.read_resource(name)
            package.resources.append(resource)
        return package

    def __read_table_convert_schema(self, ckan_table):
        schema = Schema()

        # Fields
        for ckan_field in ckan_table["fields"]:
            # Don't include datastore internal field '_id'.
            if ckan_field["id"] == "_id":
                continue
            ckan_type = ckan_field["type"]
            type = self.__read_convert_type(ckan_type)
            field = Field(name=ckan_field["id"], type=type)
            # TODO: review
            if ckan_type in ["timestamp", "date", "time"]:
                field.format = "any"
            elif ckan_type in ["uuid"]:
                field.format = "uuid"
            schema.fields.append(field)

        return schema

    def __read_convert_data(self, ckan_table):
        datastore_search_url = "{}/datastore_search".format(self.__endpoint)
        params = {"resource_id": ckan_table.name}
        response = self.__make_ckan_request(datastore_search_url, params=params)
        while response["result"]["records"]:
            for row in response["result"]["records"]:
                yield row
            next_url = self.__base_url + response["result"]["_links"]["next"]
            response = self.__make_ckan_request(next_url)

    def __read_convert_type(self, ckan_type=None):

        # Create mapping
        mapping = {
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

        # Return type
        if ckan_type:
            ckan_type = ckan_type.rstrip("0123456789")
            if ckan_type.startswith("_"):
                ckan_type = "array"
            return mapping.get(ckan_type, "string")

        # Return mapping
        return mapping

    def __read_ckan_table(self, name):
        datastore_search_url = "{}/datastore_search".format(self.__endpoint)
        params = {"limit": 0, "resource_id": name}
        response = self.__make_ckan_request(datastore_search_url, params=params)
        return response["result"]

    # Write

    def _write_table(self, table, force=False):
        # Check for existence
        if table.name in self._read_table_names():
            if not force:
                note = f'Table "{table.name}" already exists'
                raise FrictionlessException(errors.StorageError(note=note))
            self._write_table_remove(table.name)

        # Define tables
        datastore_dict = self._write_table_convert_table(table)
        datastore_url = "{}/datastore_create".format(self.__endpoint)
        self.__make_ckan_request(datastore_url, method="POST", json=datastore_dict)

    def _write_table_convert_table(self, table):
        schema = table.schema
        datastore_dict = {"fields": [], "resource_id": table.name, "force": True}
        for field in schema.fields:
            datastore_field = {"id": field.name}
            ckan_type = self._write_table_convert_field_type(field.type)
            if ckan_type:
                datastore_field["type"] = ckan_type
            datastore_dict["fields"].append(datastore_field)
        if schema.primary_key is not None:
            datastore_dict["primary_key"] = schema.primary_key
        return datastore_dict

    def _write_table_convert_field_type(self, type):
        DESCRIPTOR_TYPE_MAPPING = {
            "number": "float",
            "string": "text",
            "integer": "int",
            "boolean": "bool",
            "object": "json",
            "array": "text[]",
            "geojson": "json",
            "date": "text",
            "time": "time",
            "year": "int",
            "datetime": "timestamp",
        }
        return DESCRIPTOR_TYPE_MAPPING.get(type, "text")

    def _write_table_row_stream(self, name, row_stream):
        table = self._read_table(name)
        datastore_upsert_url = "{}/datastore_upsert".format(self.__endpoint)
        records = [r.to_dict(json=True) for r in row_stream]
        params = {
            "resource_id": table.name,
            "method": "insert",
            "force": True,
            "records": records,
        }
        self.__make_ckan_request(datastore_upsert_url, method="POST", json=params)

    def write_resource(self, resource, *, force=False):
        self._write_table(resource, force=force)
        self._write_table_row_stream(resource.name, resource.read_row_stream())

    def write_package(self, package, *, force=False):
        for resource in package.resources:
            self.write_resource(resource, force=force)

    # Delete

    def _write_table_remove(self, name, ignore=False):
        # Check existent
        if name not in self._read_table_names():
            if not ignore:
                note = f'Table "{name}" does not exist'
                raise FrictionlessException(errors.StorageError(note=note))

        # Remove from ckan
        datastore_delete_url = "{}/datastore_delete".format(self.__endpoint)
        params = {"resource_id": name, "force": True}
        self.__make_ckan_request(datastore_delete_url, method="POST", json=params)

    def delete_resource(self, name, *, ignore=False):
        self._write_table_remove(name, ignore=ignore)

    def delete_package(self, names, *, ignore=False):
        for name in names:
            self._write_table_remove(name, ignore=ignore)

    # Private

    def __get_resource_ids_for_dataset(self, dataset):
        """Get a list of resource ids for the passed dataset id."""
        package_show_url = "{}/package_show".format(self.__endpoint)
        response = self.__make_ckan_request(package_show_url, params=dict(id=dataset))
        dataset = response["result"]
        resources = dataset["resources"]
        resource_ids = [r["id"] for r in resources]
        return resource_ids

    def __make_ckan_request(self, datastore_url, **kwargs):
        response = make_ckan_request(datastore_url, api_key=self.__api_key, **kwargs)
        ckan_error = get_ckan_error(response)
        if ckan_error:
            note = "CKAN returned an error: " + json.dumps(ckan_error)
            raise FrictionlessException(errors.StorageError(note=note))
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
