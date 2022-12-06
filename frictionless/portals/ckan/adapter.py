import os
import json
from typing import List, Union
from ...exception import FrictionlessException
from ...system import system, Adapter
from ...platform import platform
from ...catalog import Catalog
from ...package import Package
from ...resource import Resource
from ... import helpers
from .control import CkanControl


class CkanAdapter(Adapter):
    """Read and write data from/to Ckan"""

    def __init__(self, control: CkanControl):
        self.control = control
        self.mapper = {
            "ckan_to_fric": platform.frictionless_ckan_mapper_ckan_to_frictionless,
            "fric_to_ckan": platform.frictionless_ckan_mapper_frictionless_to_ckan,
        }

    # Read a set of CKAN datasets as a Catalog
    def read_catalog(self) -> Catalog:
        packages: List[Union[Package, str]] = []
        params = {}
        endpoint: str = ""
        response: dict = {}
        descriptor: dict = {}
        num_packages: Union[int, None] = None
        headers = set_headers(self)

        assert self.control.baseurl
        if self.control.group_id:
            # Search only packages from a group
            params = {"id": self.control.group_id}
            endpoint = f"{self.control.baseurl}/api/3/action/group_package_show"
        elif self.control.organization_name:
            # Search only packages from an organization using search
            params = {"q": f"organization:{self.control.organization_name}"}
            endpoint = f"{self.control.baseurl}/api/3/action/package_search"
        elif self.control.search:
            params = self.control.search
            endpoint = f"{self.control.baseurl}/api/3/action/package_search"
        else:
            # Get all packages from a CKAN instance
            params = {"q": "*:*"}
            endpoint = f"{self.control.baseurl}/api/3/action/package_search"

        if self.control.num_packages:
            if not self.control.group_id:
                params["rows"] = str(self.control.num_packages)
            else:
                params["limit"] = str(self.control.num_packages)

        if self.control.results_offset:
            params["start"] = str(self.control.results_offset)

        response = make_ckan_request(endpoint, headers=headers, params=params)
        if not self.control.group_id:
            results = response["result"]["results"]
            num_packages = response["result"]["count"]
        else:
            results = response["result"]

        for dataset in results:
            try:
                descriptor = self.mapper["ckan_to_fric"].dataset(dataset)
                package = Package.from_descriptor(descriptor)
                packages.append(package)
            except FrictionlessException as e:
                if self.control.ignore_package_errors:
                    print(f'Error in CKAN dataset {descriptor["id"]}: {e}')
                    continue
                else:
                    raise e

        if num_packages:
            print(f"Total number of packages: {num_packages}")

        return Catalog(name="catalog", packages=packages)

    # Read a package from a CKAN instance
    def read_package(self) -> Package:
        baseurl = self.control.baseurl
        dataset = self.control.dataset
        assert baseurl
        assert dataset
        params = {"id": dataset}
        args = {}

        if self.control.apikey:
            args["apikey"] = self.control.apikey

        endpoint = f"{self.control.baseurl}/api/3/action/package_show"
        response = make_ckan_request(endpoint, **args, params=params)
        descriptor = self.mapper["ckan_to_fric"].dataset(response["result"])

        try:
            package = Package.from_descriptor(descriptor)
        except FrictionlessException as e:
            if self.control.ignore_schema:
                for res in descriptor["resources"]:
                    res["original_schema"] = res["schema"]
                    del res["schema"]
                package = Package.from_descriptor(descriptor)
            else:
                raise e

        for path in package.resource_paths:
            if (
                path.endswith(("/datapackage.json", "/datapackage.yaml"))
                and not self.control.ignore_schema
            ):
                return Package.from_descriptor(path)

        for resource in package.resources:
            resource.name = helpers.slugify(resource.name)
            if resource.format:
                resource.format = resource.format.lower()

        return package

    # Write a Package to a CKAN instance as a dataset
    def write_package(self, package: Package) -> Union[None, str]:
        baseurl = self.control.baseurl
        endpoint = f"{baseurl}/api/action/package_create"
        headers = set_headers(self)

        remote_resources = []
        not_remote_resources = []
        for res in package.resources:
            if res.remote:
                remote_resources.append(res)
            else:
                not_remote_resources.append(res)

        package.resources = remote_resources
        package_descriptor = package.to_descriptor()
        package_data = self.mapper["fric_to_ckan"].package(package_descriptor)

        # Assure that the package has a name
        if "name" not in package_data:
            note = "Your package has no name. CKAN requires a name to publish a package"
            raise FrictionlessException(note)

        # if "id" exist and control is set to allow updates, try to update dataset
        if "id" in package_data and self.control.allow_update:
            endpoint = f"{baseurl}/api/action/package_update"

        try:
            # Make request
            response = system.http_session.request(
                method="POST",
                url=endpoint,
                headers=headers,
                allow_redirects=True,
                json=package_data,
            )

            if response.status_code == 200:
                response_dict = json.loads(response.content)
                dataset_id = response_dict["result"]["id"]

                # upload resources
                for resource in not_remote_resources:
                    self.write_resource(dataset_id, resource)

                return f"{self.control.baseurl}/dataset/{dataset_id}"
            else:
                note = response.text
                raise FrictionlessException(note)

        except Exception as exception:
            note = "CKAN API error:" + repr(exception)
            raise FrictionlessException(note)

    def write_resource(self, dataset_id: str, resource: Resource):
        baseurl = self.control.baseurl
        endpoint = f"{baseurl}/api/action/resource_create"
        headers = set_headers(self)
        resource_descriptor = resource.to_descriptor()
        resource_data = self.mapper["fric_to_ckan"].resource(resource_descriptor)
        resource_data["package_id"] = dataset_id
        resource_filename = resource_data["url"].split("/")[-1]

        del resource_data["url"]

        try:
            response = system.http_session.request(
                method="POST",
                url=endpoint,
                headers=headers,
                allow_redirects=True,
                data=resource_data,
                files={
                    "upload": (
                        resource_filename,
                        resource.read_bytes(),
                        "application/octet-stream",
                    )
                },
            )

            if response.status_code != 200:
                note = response.text
                raise FrictionlessException(note)
        except Exception as exception:
            note = "CKAN API error:" + repr(exception)
            raise FrictionlessException(note)


def set_headers(adapter: CkanAdapter) -> dict:
    headers = {}

    if adapter.control.apikey:
        if adapter.control.apikey.startswith("env:"):
            apikey = os.environ.get(adapter.control.apikey[4:])
        else:
            apikey = adapter.control.apikey

        headers.update({"Authorization": apikey})

    return headers


def make_ckan_request(
    endpoint, *, method="GET", headers=None, apikey=None, **options
) -> dict:

    response_json: dict = {}
    # Handle headers
    if headers is None:
        headers = {}

    # Handle API key
    if apikey:
        if apikey.startswith("env:"):
            apikey = os.environ.get(apikey[4:])
        headers.update({"Authorization": apikey})

    # Make request
    response = system.http_session.request(
        method=method, url=endpoint, headers=headers, allow_redirects=True, **options
    )

    if response is not None:
        response_json = response.json()

    # Handle error
    try:
        ckan_error = None
        if not response_json.get("success") and response_json["error"]:
            ckan_error = response_json["error"]
    except TypeError:
        ckan_error = response
    if ckan_error:
        note = "CKAN returned an error: " + json.dumps(ckan_error)
        raise FrictionlessException(note)

    return response_json
