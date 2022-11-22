import os
import json
from typing import TYPE_CHECKING, Optional, List, Union
from ...exception import FrictionlessException
from ...system import system, Adapter
from ...platform import platform
from ...catalog import Catalog
from ...package import Package
from ... import helpers
from .control import CkanControl


class CkanAdapter(Adapter):
    """Read and write data from/to Ckan"""

    mapper = {
        "ckan_to_fric": platform.frictionless_ckan_mapper_ckan_to_frictionless,
        "fric_to_ckan": platform.frictionless_ckan_mapper_frictionless_to_ckan,
    }

    def __init__(self, control: CkanControl):
        self.control = control

    # Read a set of CKAN datasets as a Catalog
    def read_catalog(self) -> Catalog:
        packages: List[Union[Package, str]] = []
        params = {}
        endpoint: str = ""
        response: dict = {}
        descriptor: dict = {}

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

        response = make_ckan_request(endpoint, params=params)
        results = response["result"]["results"]

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

        return Catalog(name="catalog", packages=packages)

    # Read a package from a CKAN instance
    def read_package(self, *, dataset: Optional[str] = None) -> Package:
        baseurl = self.control.baseurl
        dataset = dataset or self.control.dataset
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
        headers = {}

        if self.control.apikey:
            if self.control.apikey.startswith("env:"):
                apikey = os.environ.get(self.control.apikey[4:])
            else:
                apikey = self.control.apikey

            headers.update({"Authorization": apikey})

        package_data = self.mapper["fric_to_ckan"].package(package.to_descriptor())
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

                return f"{self.control.baseurl}/dataset/{dataset_id}"

        except Exception as exception:
            note = "CKAN API error:" + repr(exception)
            raise FrictionlessException(note)


# Internal
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

    if response:
        response_json = response.json()

    # Handle error
    try:
        ckan_error = None
        if not response_json["success"] and response_json["error"]:
            ckan_error = response_json["error"]
    except TypeError:
        ckan_error = response
    if ckan_error:
        note = "CKAN returned an error: " + json.dumps(ckan_error)
        raise FrictionlessException(note)

    return response_json
