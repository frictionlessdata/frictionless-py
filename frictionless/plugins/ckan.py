import os
import json
import requests
from functools import partial
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..resource import Resource
from ..package import Package
from ..storage import Storage
from ..dialect import Dialect
from ..parser import Parser
from ..plugin import Plugin
from ..schema import Schema
from ..field import Field
from .. import errors


# Plugin


class CkanPlugin(Plugin):
    """Plugin for CKAN

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ckan import CkanPlugin`
    """

    code = "ckan"
    status = "experimental"

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "ckan":
            return CkanDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "ckan":
            return CkanParser(resource)

    def create_storage(self, name, source, **options):
        if name == "ckan":
            return CkanStorage(source, **options)


# Dialect


class CkanDialect(Dialect):
    """Ckan dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ckan import CkanDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        resource? (str): resource
        dataset? (str): dataset
        apikey? (str): apikey

    Raises:
        FrictionlessException: raise any error that occurs during the process
    """

    def __init__(self, descriptor=None, *, dataset=None, resource=None, apikey=None):
        self.setinitial("resource", resource)
        self.setinitial("dataset", dataset)
        self.setinitial("apikey", apikey)
        super().__init__(descriptor)

    @Metadata.property
    def resource(self):
        return self.get("resource")

    @Metadata.property
    def dataset(self):
        return self.get("dataset")

    @Metadata.property
    def apikey(self):
        return self.get("apikey")

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["resource", "dataset"],
        "additionalProperties": False,
        "properties": {
            "resource": {"type": "string"},
            "dataset": {"type": "string"},
            "apikey": {"type": "string"},
        },
    }


# Parser


class CkanParser(Parser):
    """Ckan parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.ckan import CkanParser`
    """

    supported_types = [
        "string",
    ]

    # Read

    def read_list_stream_create(self):
        storage = CkanStorage(self.resource.fullpath, dialect=self.resource.dialect)
        resource = storage.read_resource(self.resource.dialect.resource)
        self.resource.schema = resource.schema
        with resource:
            yield from resource.list_stream

    # Write

    # NOTE: this approach is questionable
    def write_row_stream(self, resource):
        source = resource
        target = self.resource
        storage = CkanStorage(target.fullpath, dialect=target.dialect)
        if not target.dialect.resource:
            note = 'Please provide "dialect.resource" for writing'
            raise FrictionlessException(errors.StorageError(note=note))
        source.name = target.dialect.resource
        storage.write_resource(source, force=True)


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

    def __init__(self, source, *, dialect=None):
        dialect = dialect or CkanDialect()
        self.__url = source.rstrip("/")
        self.__endpoint = f"{self.__url}/api/3/action"
        self.__dataset = dialect.dataset
        self.__apikey = dialect.apikey

    def __iter__(self):
        names = []
        params = {"id": self.__dataset}
        endpoint = f"{self.__endpoint}/package_show"
        response = self.__make_ckan_request(endpoint, params=params)
        for resource in response["result"]["resources"]:
            names.append(resource.get("name", resource["id"]))
        return iter(names)

    # Read

    def read_resource(self, name):
        ckan_table = self.__read_ckan_table(name)
        if ckan_table is None:
            note = f'Resource "{name}" does not exist'
            raise FrictionlessException(errors.StorageError(note=note))
        schema = self.__read_convert_schema(ckan_table)
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

    def __read_convert_schema(self, ckan_table):
        schema = Schema()

        # Fields
        for ckan_field in ckan_table["fields"]:
            if ckan_field["id"] != "_id":
                ckan_type = ckan_field["type"]
                type = self.__read_convert_type(ckan_type)
                field = Field(name=ckan_field["id"], type=type)
                schema.fields.append(field)

        return schema

    def __read_convert_data(self, ckan_table):
        endpoint = f"{self.__endpoint}/datastore_search"
        params = {"resource_id": ckan_table["resource_id"]}
        response = self.__make_ckan_request(endpoint, params=params)
        while response["result"]["records"]:
            for row in response["result"]["records"]:
                yield row
            next_url = self.__url + response["result"]["_links"]["next"]
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
        params = {"id": self.__dataset}
        endpoint = f"{self.__endpoint}/package_show"
        response = self.__make_ckan_request(endpoint, params=params)
        for resource in response["result"]["resources"]:
            if name == resource.get("name", resource["id"]):
                endpoint = f"{self.__endpoint}/datastore_search"
                params = {"limit": 0, "resource_id": resource["id"]}
                response = self.__make_ckan_request(endpoint, params=params)
                return response["result"]

    # Write

    def write_resource(self, resource, *, force=False):
        package = Package(resources=[resource])
        self.write_package(package, force=force)

    def write_package(self, package, *, force=False):
        existent_names = list(self)

        # Check existent
        for resource in package.resources:
            if resource.name in existent_names:
                if not force:
                    note = f'Resource "{resource.name}" already exists'
                    raise FrictionlessException(errors.StorageError(note=note))
                self.delete_resource(resource.name)

        # Write resources
        for resource in package.resources:
            if not resource.schema:
                resource.infer()
            endpoint = f"{self.__endpoint}/datastore_create"
            ckan_table = self.__write_convert_schema(resource)
            self.__make_ckan_request(endpoint, method="POST", json=ckan_table)
            self.__write_convert_data(resource)

    def __write_convert_schema(self, resource):
        ckan_table = {"resource": {"package_id": self.__dataset, "name": resource.name}}

        # Fields
        ckan_table["fields"] = []
        for field in resource.schema.fields:
            ckan_field = {"id": field.name}
            ckan_type = self.__write_convert_type(field.type)
            if ckan_type:
                ckan_field["type"] = ckan_type
            ckan_table["fields"].append(ckan_field)

        # Primary Key
        if resource.schema.primary_key is not None:
            ckan_table["primary_key"] = resource.schema.primary_key

        return ckan_table

    def __write_convert_data(self, resource):
        ckan_table = self.__read_ckan_table(resource.name)
        endpoint = f"{self.__endpoint}/datastore_upsert"
        with resource:
            records = [row.to_dict(json=True) for row in resource.row_stream]
        self.__make_ckan_request(
            endpoint,
            method="POST",
            json={
                "resource_id": ckan_table["resource_id"],
                "method": "insert",
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
            ckan_table = self.__read_ckan_table(name)
            endpoint = f"{self.__endpoint}/resource_delete"
            params = {"id": ckan_table["resource_id"]}
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
