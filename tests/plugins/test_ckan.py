import datetime
import json
import urllib

import pytest
import responses
from frictionless import Package, Resource, exceptions
from frictionless.plugins.ckan import CkanStorage

"""
Tests for CKAN plugin

Note: in this module we decorate all test functions with `@responses.activate` even
if we don't expect the test to make any HTTP calls. This way, if a test we are not
expecting to communicate over HTTP tries to make a HTTP request we will throw
`Connection refused by Responses - the call doesn't match any registered mock`
instead of silently making the request.
"""


def _assert_resource_valid(resource):
    assert resource.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "parent", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "current", "type": "boolean"},
            {"name": "rating", "type": "number"},
            {"name": "created_year", "type": "integer"},
            {"name": "created_date", "type": "date", "format": "any"},
            {"name": "created_time", "type": "time", "format": "any"},
            {"name": "created_datetime", "type": "datetime", "format": "any"},
            {"name": "stats", "type": "object"},
            {"name": "persons", "type": "array"},
            {"name": "location", "type": "object"},
        ]
    }

    rows = resource.read_rows()
    assert len(rows) == 3
    assert rows[0].to_dict() == {
        "id": 1,
        "parent": None,
        "name": "Taxes",
        "current": True,
        "rating": 9.5,
        "created_year": 2015,
        "created_date": datetime.date(2015, 1, 1),
        "created_time": datetime.time(3, 0),
        "created_datetime": datetime.datetime(2015, 1, 1, 3, 0),
        "stats": {"chars": 560, "height": 54.8},
        "persons": ["mike", "alice"],
        "location": {"type": "Point", "coordinates": [50.0, 50.0]},
    }


@responses.activate
def test_read_package_valid():
    resources_ids = [
        "bd79c992-40f0-454a-a0ff-887f84a792fb",
        "79843e49-7974-411c-8eb5-fb2d1111d707",
    ]
    filter_qs = urllib.parse.urlencode({"filters": json.dumps({"name": resources_ids})})
    dataset_id = "my-dataset-id"
    base_url = "https://demo.ckan.org"

    mock_package_show_payload = json.load(
        open("data/ckan_mock_responses/package_show.json", encoding="utf-8")
    )
    responses.add(
        responses.GET,
        f"{base_url}/api/3/action/package_show?id={dataset_id}",
        json=mock_package_show_payload,
        status=200,
    )

    # First response gets the _table_metadata results
    mock_datastore_search_01_payload = json.load(
        open(
            "data/ckan_mock_responses/datastore_search_table_metadata_01.json",
            encoding="utf-8",
        )
    )
    responses.add(
        responses.GET,
        f"{base_url}/api/3/action/datastore_search?resource_id=_table_metadata&{filter_qs}",
        json=mock_datastore_search_01_payload,
        status=200,
    )
    # Second response is empty, indicating the results are exhausted
    mock_datastore_search_02_payload = json.load(
        open(
            "data/ckan_mock_responses/datastore_search_table_metadata_02.json",
            encoding="utf-8",
        )
    )
    responses.add(
        responses.GET,
        f"{base_url}/api/3/action/datastore_search?offset=100&{filter_qs}&resource_id=_table_metadata",
        json=mock_datastore_search_02_payload,
        status=200,
    )

    for resource_id in resources_ids:
        mock_datastore_search_describe_payload = json.load(
            open(
                "data/ckan_mock_responses/datastore_search_describe.json",
                encoding="utf-8",
            )
        )
        responses.add(
            responses.GET,
            f"{base_url}/api/3/action/datastore_search?limit=0&resource_id={resource_id}",
            json=mock_datastore_search_describe_payload,
            status=200,
        )

        # First response gets the data rows
        mock_datastore_search_rows_payload = json.load(
            open(
                "data/ckan_mock_responses/datastore_search_rows.json",
                encoding="utf-8",
            )
        )
        responses.add(
            responses.GET,
            f"{base_url}/api/3/action/datastore_search?resource_id={resource_id}",
            json=mock_datastore_search_rows_payload,
            status=200,
        )
        # Second response is empty, indicating the results are exhausted
        mock_datastore_search_rows_empty_payload = json.load(
            open(
                "data/ckan_mock_responses/datastore_search_rows_empty.json",
                encoding="utf-8",
            )
        )
        responses.add(
            responses.GET,
            f"{base_url}/api/3/action/datastore_search?resource_id={resource_id}&offset=100",
            json=mock_datastore_search_rows_empty_payload,
            status=200,
        )

    package = Package.from_ckan(
        base_url=base_url,
        dataset_id=dataset_id,
        api_key="env:CKAN_API_KEY",
    )

    resource = package.get_resource(resources_ids[1])
    resource.onerror = "raise"  # be strict about errors under test

    _assert_resource_valid(resource)


@responses.activate
def test_read_package_bad_package_id():
    dataset_id = "bad-dataset-id"
    base_url = "https://demo.ckan.org"

    error_payload = json.load(
        open(
            "data/ckan_mock_responses/ckan_error.json",
            encoding="utf-8",
        )
    )
    responses.add(
        responses.GET,
        f"{base_url}/api/3/action/package_show?id={dataset_id}",
        json=error_payload,
        status=404,
    )

    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        Package.from_ckan(
            base_url=base_url,
            dataset_id=dataset_id,
            api_key="env:CKAN_API_KEY",
        )
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("Not found")


@responses.activate
def test_read_resource_valid():
    resource_id = "79843e49-7974-411c-8eb5-fb2d1111d707"
    base_url = "https://demo.ckan.org"

    mock_datastore_search_describe_payload = json.load(
        open(
            "data/ckan_mock_responses/datastore_search_describe.json",
            encoding="utf-8",
        )
    )
    responses.add(
        responses.GET,
        f"{base_url}/api/3/action/datastore_search?limit=0&resource_id={resource_id}",
        json=mock_datastore_search_describe_payload,
        status=200,
    )

    # First response gets the data rows
    mock_datastore_search_rows_payload = json.load(
        open(
            "data/ckan_mock_responses/datastore_search_rows.json",
            encoding="utf-8",
        )
    )
    responses.add(
        responses.GET,
        f"{base_url}/api/3/action/datastore_search?resource_id={resource_id}",
        json=mock_datastore_search_rows_payload,
        status=200,
    )
    # Second response is empty, indicating the results are exhausted
    mock_datastore_search_rows_empty_payload = json.load(
        open(
            "data/ckan_mock_responses/datastore_search_rows_empty.json",
            encoding="utf-8",
        )
    )
    responses.add(
        responses.GET,
        f"{base_url}/api/3/action/datastore_search?resource_id={resource_id}&offset=100",
        json=mock_datastore_search_rows_empty_payload,
        status=200,
    )

    resource = Resource.from_ckan(
        base_url=base_url,
        resource_id=resource_id,
        api_key="env:CKAN_API_KEY",
    )
    resource.onerror = "raise"  # be strict about errors under test

    _assert_resource_valid(resource)


@responses.activate
def test_read_resource_bad_resource_id():
    resource_id = "bad-resource-id"
    base_url = "https://demo.ckan.org"

    error_payload = json.load(
        open(
            "data/ckan_mock_responses/ckan_error.json",
            encoding="utf-8",
        )
    )
    responses.add(
        responses.GET,
        f"{base_url}/api/3/action/datastore_search?limit=0&resource_id={resource_id}",
        json=error_payload,
        status=404,
    )

    with pytest.raises(exceptions.FrictionlessException) as excinfo:
        Resource.from_ckan(
            base_url=base_url,
            resource_id=resource_id,
            api_key="env:CKAN_API_KEY",
        )
    error = excinfo.value.error
    assert error.code == "storage-error"
    assert error.note.count("Not found")


@responses.activate
def test_delete_valid():
    resource_id = "79843e49-7974-411c-8eb5-fb2d1111d707"
    base_url = "https://demo.ckan.org"

    for method, params in [
        ("delete_package", [resource_id]),
        ("delete_resource", resource_id),
    ]:
        payload = json.load(
            open(
                "data/ckan_mock_responses/datastore_delete.json",
                encoding="utf-8",
            )
        )
        responses.add(
            responses.POST,
            f"{base_url}/api/3/action/datastore_delete",
            json=payload,
            status=200,
        )

        storage = CkanStorage(base_url=base_url)
        storage._CkanStorage__bucket_cache = [resource_id]
        getattr(storage, method)(params)

        assert responses.assert_call_count(f"{base_url}/api/3/action/datastore_delete", 1)
        responses.reset()


@responses.activate
def test_delete_bad_resource_id():
    for method, params in [("delete_package", ["bad-id"]), ("delete_resource", "bad-id")]:
        storage = CkanStorage(base_url="https://demo.ckan.org")
        storage._CkanStorage__bucket_cache = ["79843e49-7974-411c-8eb5-fb2d1111d707"]
        with pytest.raises(exceptions.FrictionlessException) as excinfo:
            getattr(storage, method)(params)
        error = excinfo.value.error
        assert error.code == "storage-error"
        assert error.note.count('Table "bad-id" does not exist')
