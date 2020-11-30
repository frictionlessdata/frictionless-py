import os
import json
import requests
from functools import partial
from ..exception import FrictionlessException
from ..field import Field
from ..package import Package
from ..plugin import Plugin
from ..resource import Resource
from ..schema import Schema
from ..storage import Storage
from .. import errors


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
        if name == "ckan":
            return CkanStorage(**options)


# TODO: implement Dialect
# TODO: implement Parser


# Storage


class CkanStorage(Storage):
    """Ckan storage implementation

    Parameters:
        url (string): CKAN instance url e.g. "https://demo.ckan.org"
        dataset (string): dataset id in CKAN e.g. "my-dataset"
        apikey? (str): API key for CKAN e.g. "51912f57-a657-4caa-b2a7-0a1c16821f4b"


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
            "int": "integer",
            "float": "number",
            "smallint": "integer",
            "bigint": "integer",
            "integer": "integer",
            "numeric": "number",
            "money": "number",
            "timestamp": "datetime",
            "date": "date",
            "time": "time",
            "interval": "duration",
            "text": "string",
            "varchar": "string",
            "char": "string",
            "uuid": "string",
            "boolean": "boolean",
            "bool": "boolean",
            "json": "object",
            "jsonb": "object",
            "array": "array",
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

    def write_resource(self, resource, *, force=False):
        package = Package(resources=[resource])
        return self.write_package(package, force=force)

    def write_package(self, package, *, force=False):
        existent_names = list(self)

        # Check existent
        delete_names = []
        for resource in package.resources:
            if resource.name in existent_names:
                if not force:
                    note = f'Resource "{resource.name}" already exists'
                    raise FrictionlessException(errors.StorageError(note=note))
                delete_names.append(resource.name)

        # Write resources
        for resource in package.resources:
            endpoint = f"{self.__endpoint}/datastore_create"
            ckan_table = self.__write_convert_schema(resource)
            self.__make_ckan_request(endpoint, method="POST", json=ckan_table)
            self.__write_convert_data(resource)

    def __write_convert_schema(self, resource):
        ckan_table = {"fields": [], "resource_id": resource.table.name, "force": True}
        for field in resource.schema.fields:
            ckan_field = {"id": field.name}
            ckan_type = self.__write_convert_type(field.type)
            if ckan_type:
                ckan_field["type"] = ckan_type
            ckan_table["fields"].append(ckan_field)
        if resource.schema.primary_key is not None:
            ckan_table["primary_key"] = resource.schema.primary_key
        return ckan_table

    def __write_convert_data(self, resource):
        ckan_table = self.__read_ckan_table(resource.name)
        endpoint = "{}/datastore_upsert".format(self.__endpoint)
        records = [row.to_dict(json=True) for row in resource.read_row_stream()]
        self.__make_ckan_request(
            endpoint,
            method="POST",
            json={
                "resource_id": ckan_table.name,
                "method": "insert",
                "force": True,
                "records": records,
            },
        )

    def __write_convert_type(self, type=None):

        # Create mapping
        mapping = {
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

        # Return type
        if type:
            return mapping.get(type, "text")

        # Return mapping
        return mapping

    # Delete

    def delete_resource(self, name, *, ignore=False):
        return self.delete_package([name], ignore=ignore)

    def delete_package(self, names, *, ignore=False):
        existent_names = list(self)

        # Delete resources
        for name in names:

            # Check existent
            if name not in existent_names:
                if not ignore:
                    note = f'Resource "{name}" does not exist'
                    raise FrictionlessException(errors.StorageError(note=note))
                continue

            # Remove from CKAN
            endpoint = f"{self.__endpoint}/datastore_delete"
            params = {"resource_id": name, "force": True}
            self.__make_ckan_request(endpoint, method="POST", json=params)

    # Helpers

    def __get_resource_ids_for_dataset(self, dataset):
        endpoint = f"{self.__endpoint}/package_show"
        response = self.__make_ckan_request(endpoint, params=dict(id=dataset))
        dataset = response["result"]
        resources = dataset["resources"]
        resource_ids = [resource["id"] for resource in resources]
        return resource_ids

    def __make_ckan_request(self, endpoint, **options):
        response = make_ckan_request(endpoint, apikey=self.__apikey, **options)
        ckan_error = get_ckan_error(response)
        if ckan_error:
            note = "CKAN returned an error: " + json.dumps(ckan_error)
            raise FrictionlessException(errors.StorageError(note=note))
        return response


# Internal


def make_ckan_request(url, method="GET", headers=None, apikey=None, **options):

    # Handle headers
    if headers is None:
        headers = {}

    # Handle API key
    if apikey:
        if apikey.startswith("env:"):
            apikey = os.environ.get(apikey[4:])
        headers.update({"Authorization": apikey})

    # Make a request
    return requests.request(
        method=method, url=url, headers=headers, allow_redirects=True, **options
    ).json()


def get_ckan_error(response):

    # Get an error
    try:
        ckan_error = None
        if not response["success"] and response["error"]:
            ckan_error = response["error"]
    except TypeError:
        ckan_error = response

    return ckan_error
