import os
import json
from typing import Optional
from ...exception import FrictionlessException
from ...system import system, Adapter
from ...platform import platform
from ...catalog import Catalog
from ...package import Package
from ... import helpers
from .control import CkanControl


class CkanAdapter(Adapter):
    """Read and write data from/to Ckan"""

    def __init__(self, control: CkanControl):
        self.control = control

    # Read

    # TODO: improve
    def read_catalog(self):
        assert self.control.baseurl
        endpoint = f"{self.control.baseurl}/api/3/action/package_list"
        response = make_ckan_request(endpoint)
        catalog = Catalog()
        for dataset in response["result"]:
            package = self.read_package(dataset=dataset)
            catalog.add_package(package)
        return catalog

    # TODO: improve
    def read_package(self, *, dataset: Optional[str] = None):
        mapper = platform.frictionless_ckan_mapper_ckan_to_frictionless
        baseurl = self.control.baseurl
        dataset = dataset or self.control.dataset
        assert baseurl
        assert dataset
        params = {"id": dataset}
        endpoint = f"{self.control.baseurl}/api/3/action/package_show"
        response = make_ckan_request(endpoint, params=params)
        descriptor = mapper.dataset(response["result"])
        package = Package.from_descriptor(descriptor)
        for path in package.resource_paths:
            if path.endswith(("/datapackage.json", "/datapackage.yaml")):
                return Package.from_descriptor(path)
        for resource in package.resources:
            resource.name = helpers.slugify(resource.name)
            if resource.format:
                resource.format = resource.format.lower()
        return package

    # Write
    # TODO: implement


# Internal


def make_ckan_request(endpoint, *, method="GET", headers=None, apikey=None, **options):

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
    ).json()

    # Handle error
    try:
        ckan_error = None
        if not response["success"] and response["error"]:
            ckan_error = response["error"]
    except TypeError:
        ckan_error = response
    if ckan_error:
        note = "CKAN returned an error: " + json.dumps(ckan_error)
        raise FrictionlessException(note)

    return response
