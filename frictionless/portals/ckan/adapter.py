import json
import os
from pathlib import PurePosixPath
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from ... import helpers, models
from ...catalog import Catalog, Dataset
from ...exception import FrictionlessException
from ...package import Package
from ...platform import platform
from ...resource import Resource
from ...system import Adapter, system
from .control import CkanControl


class CkanAdapter(Adapter):
    """Read and write data from/to Ckan"""

    def __init__(self, control: CkanControl):
        self.control = control
        self.mapper = {
            "ckan_to_fric": platform.frictionless_ckan_mapper_ckan_to_frictionless,
            "fric_to_ckan": platform.frictionless_ckan_mapper_frictionless_to_ckan,
        }

    # Read

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
        response = make_ckan_request(endpoint, **args, params=params)  # type: ignore
        descriptor = self.mapper["ckan_to_fric"].dataset(response["result"])  # type: ignore
        descriptor.pop("type", None)
        descriptor.pop("sources", None)
        for res in descriptor.get("resources", []):
            res.pop("fields", None)
            if "format" in res:
                res["format"] = res["format"].lower()

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
            if path.endswith("/datapackage.json") and not self.control.ignore_schema:
                return Package.from_descriptor(path)

        for resource in package.resources:
            resource.name = helpers.slugify(resource.name)

        return package

    # Write

    def write_package(self, package: Package):
        baseurl = self.control.baseurl
        endpoint = f"{baseurl}/api/action/package_create"
        headers = set_headers(self)
        package_descriptor = package.to_descriptor()
        package_data = self.mapper["fric_to_ckan"].package(package_descriptor)  # type: ignore
        package_data["owner_org"] = self.control.organization_name

        # Assure that the package has a name
        if "name" not in package_data:
            if not self.control.dataset:
                note = (
                    "Your package has no name. CKAN requires a name to publish a package"
                )
                raise FrictionlessException(note)
            else:
                package_data["name"] = self.control.dataset

        # if "id" exist and control is set to allow updates, try to update dataset
        if self.control.allow_update:
            endpoint = f"{baseurl}/api/action/package_update"

        if "resources" in package_data:
            del package_data["resources"]

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
                dataset_name = response_dict["result"]["name"]
                package_descriptor = package.to_descriptor(validate=True)

                # upload resources
                # TODO: See if it's possible to upload only the resources that need to be uploaded
                for index, resource in enumerate(package.resources):
                    if resource.path:
                        _, resource_filename = os.path.split(resource.path)
                        resource_filename = (
                            f"{resource.name}.{resource_filename.split('.')[1]}"
                        )
                        package_descriptor["resources"][index]["path"] = resource_filename
                    self.write_resource(dataset_id, resource)

                # upload package
                package_resource_data = {
                    "name": "datapackage",
                    "type": "json",
                    "package_id": dataset_id,
                }
                endpoint = f"{baseurl}/api/action/resource_create"
                make_ckan_request(
                    endpoint,
                    method="POST",
                    headers=headers,
                    data=package_resource_data,
                    files={
                        "upload": (
                            "datapackage.json",
                            json.dumps(package_descriptor, indent=2).encode("utf-8"),
                            "application/octet-stream",
                        )
                    },
                )
                return models.PublishResult(
                    url=urljoin(
                        self.control.baseurl or "",
                        str(PurePosixPath("dataset").joinpath(dataset_name)),
                    ),
                    context=dict(dataset_id=dataset_id),
                )
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
        resource_data = self.mapper["fric_to_ckan"].resource(resource_descriptor)  # type: ignore
        resource_data["package_id"] = dataset_id
        _, resource_filename = os.path.split(resource_data["url"])
        resource_data["owner_org"] = self.control.organization_name

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

    # Experimental

    def read_catalog(self) -> Catalog:
        catalog = Catalog()
        params = {}
        endpoint: str = ""
        response: Dict[str, Any] = {}
        descriptor: Dict[str, Any] = {}
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
        else:
            results = response["result"]

        for dataset in results:
            try:
                descriptor = self.mapper["ckan_to_fric"].dataset(dataset)  # type: ignore
                descriptor.pop("type", None)
                descriptor.pop("sources", None)
                for res in descriptor.get("resources", []):
                    res.pop("fields", None)
                    if "format" in res:
                        res["format"] = res["format"].lower()
                package = Package.from_descriptor(descriptor)
                dataset = Dataset(name=package.name, package=package)  # type: ignore
                catalog.add_dataset(dataset)
            except FrictionlessException as e:
                if self.control.ignore_package_errors:
                    print(f'Error in CKAN dataset {descriptor["id"]}: {e}')
                    continue
                else:
                    raise e

        return catalog


def set_headers(adapter: CkanAdapter) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    if adapter.control.apikey:
        if adapter.control.apikey.startswith("env:"):
            apikey = os.environ.get(adapter.control.apikey[4:])
        else:
            apikey = adapter.control.apikey

        headers.update({"Authorization": apikey})

    return headers


def make_ckan_request(
    endpoint: str,
    *,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    apikey: Optional[str] = None,
    **options: Any,
) -> Dict[str, Any]:
    response_json: Dict[str, Any] = {}
    # Handle headers
    if headers is None:
        headers = {}

    # Handle API key
    if apikey:
        if apikey.startswith("env:"):
            apikey = os.environ.get(apikey[4:])
        headers.update({"Authorization": apikey})  # type: ignore

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
