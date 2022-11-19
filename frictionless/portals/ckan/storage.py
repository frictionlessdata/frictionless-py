# type: ignore
from __future__ import annotations
import os
import json
from functools import partial
from ...exception import FrictionlessException
from ...schema import Schema, Field
from ..inline import InlineControl
from ...resource import Resource
from ...package import Package
from .control import CkanControl


# General


# TODO: finish merging this with Adapter and remove Storage
class CkanStorage:
    """Ckan storage implementation"""

    def __init__(self, source, *, control=None):
        control = control or CkanControl()
        self.__url = source.rstrip("/")
        self.__endpoint = f"{self.__url}/api/3/action"
        self.__dataset = control.dataset
        self.__apikey = control.apikey
        self.__queryoptions = {
            "fields": control.fields,
            "limit": control.limit,
            "sort": control.sort,
            "filters": control.filters,
        }

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
            raise FrictionlessException(f'Resource "{name}" does not exist')
        schema = self.__read_convert_schema(ckan_table)
        resource = Resource(
            name=name,
            data=partial(self.__read_convert_data, ckan_table),
            schema=schema,
            control=InlineControl(keys=schema.field_names),  # type: ignore
        )
        return resource

    def read_package(self, **options):
        package = Package()
        for name in self:
            try:
                resource = self.read_resource(name)
                package.add_resource(resource)
            # We skip not tabular resources
            except FrictionlessException as exception:
                if not exception.error.note.count("Not Found Error"):
                    raise
        return package

    def __read_convert_schema(self, ckan_table):
        schema = Schema()

        # Fields
        for ckan_field in ckan_table["fields"]:
            if ckan_field["id"] != "_id":
                ckan_type = ckan_field["type"]
                type = self.__read_convert_type(ckan_type)
                field = Field.from_descriptor({"name": ckan_field["id"], "type": type})
                schema.add_field(field)

        return schema

    def __read_convert_data(self, ckan_table):
        endpoint = f"{self.__endpoint}/datastore_search"
        for key, option in self.__queryoptions.copy().items():
            if option is None or option == 0:
                self.__queryoptions.pop(key)
            if type(option) == list:
                self.__queryoptions[key] = ", ".join(self.__queryoptions[key])
            if type(option) == dict:
                self.__queryoptions[key] = json.dumps(self.__queryoptions[key])
        params = {
            "resource_id": ckan_table["resource_id"],
            "include_total": False,
            **self.__queryoptions,
        }

        response = self.__make_ckan_request(endpoint, params=params)
        while response["result"]["records"]:
            for row in response["result"]["records"]:
                yield row
            if "limit" not in self.__queryoptions:
                next_url = self.__url + response["result"]["_links"]["next"]  # type: ignore
                response = self.__make_ckan_request(next_url)
            else:
                response = dict(result=dict(records=[]))

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
                params = {
                    "resource_id": resource["id"],
                    "limit": 0,
                }
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
                    raise FrictionlessException(note)
                self.delete_resource(resource.name)

        # Write resources
        for resource in package.resources:
            if not resource.has_schema:
                resource.infer()
            endpoint = f"{self.__endpoint}/datastore_create"
            ckan_table = self.__write_convert_schema(resource)
            self.__make_ckan_request(endpoint, method="POST", json=ckan_table)
            self.__write_convert_data(resource)

    def __write_convert_schema(self, resource):
        ckan_table = {"resource": {"package_id": self.__dataset, "name": resource.name}}

        # Fields
        ckan_table["fields"] = []  # type: ignore
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
                "resource_id": ckan_table["resource_id"],  # type: ignore
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
                    raise FrictionlessException(note)
                continue

            # Remove from CKAN
            ckan_table = self.__read_ckan_table(name)
            endpoint = f"{self.__endpoint}/resource_delete"
            params = {"id": ckan_table["resource_id"]}  # type: ignore
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
            raise FrictionlessException(note)
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
    #  return system.http_session.request(
    #  method=method, url=url, headers=headers, allow_redirects=True, **options
    #  ).json()


def get_ckan_error(response):

    # Get an error
    try:
        ckan_error = None
        if not response["success"] and response["error"]:
            ckan_error = response["error"]
    except TypeError:
        ckan_error = response

    return ckan_error
