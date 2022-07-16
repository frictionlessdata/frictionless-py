import os
import json
from ...exception import FrictionlessException
from ...package import Package
from .control import CkanControl
from ...package import Manager
from ...system import system
from ... import helpers


class CkanManager(Manager[CkanControl]):

    # Read

    def read_package(self):
        mapper = helpers.import_from_extras(
            "frictionless_ckan_mapper.ckan_to_frictionless", name="ckan"
        )
        assert self.control.baseurl
        assert self.control.dataset
        params = {"id": self.control.dataset}
        endpoint = f"{self.control.baseurl}/api/3/action/package_show"
        response = make_ckan_request(endpoint, params=params)
        descriptor = mapper.dataset(response["result"])
        package = Package.from_descriptor(descriptor)
        for resource in package.resources:
            resource.name = helpers.slugify(resource.name)
            if resource.format:
                resource.format = resource.format.lower()
        return package


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

    # Make a request
    http_session = system.get_http_session()
    response = http_session.request(
        method=method, url=endpoint, headers=headers, allow_redirects=True, **options
    ).json()

    # Get an error
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
