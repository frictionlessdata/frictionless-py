import datetime
import json
import urllib
from decimal import Decimal

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


def _mock_json_call(url, json_file, *, method=responses.GET, status=200, **kwargs):
    body = json.load(open(json_file, encoding="utf-8"))
    responses.add(method, url, json=body, status=status, **kwargs)


class TestRead:
    def _assert_resource_valid(self, resource):
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
        assert rows[1].to_dict() == {
            "id": 2,
            "parent": 1,
            "name": "中国人",
            "current": False,
            "rating": Decimal("7.0"),
            "created_year": 2015,
            "created_date": datetime.date(2015, 12, 31),
            "created_time": datetime.time(15, 45, 33),
            "created_datetime": datetime.datetime(2015, 12, 31, 15, 45, 33),
            "stats": {"chars": 970, "height": 40},
            "persons": ["chen", "alice"],
            "location": {"type": "Point", "coordinates": [33.33, 33.33]},
        }
        assert rows[2].to_dict() == {
            "id": 3,
            "parent": 1,
            "name": None,
            "current": False,
            "rating": None,
            "created_year": None,
            "created_date": None,
            "created_time": None,
            "created_datetime": None,
            "stats": None,
            "persons": None,
            "location": None,
        }

    @responses.activate
    def test_read_package_valid(self):
        resources_ids = [
            "bd79c992-40f0-454a-a0ff-887f84a792fb",
            "79843e49-7974-411c-8eb5-fb2d1111d707",
        ]
        filter_qs = urllib.parse.urlencode(
            {"filters": json.dumps({"name": resources_ids})}
        )
        dataset_id = "my-dataset-id"
        base_url = "https://demo.ckan.org"

        _mock_json_call(
            f"{base_url}/api/3/action/package_show?id={dataset_id}",
            "data/ckan_mock_responses/package_show.json",
        )

        # First response gets the _table_metadata results
        _mock_json_call(
            f"{base_url}/api/3/action/datastore_search?resource_id=_table_metadata&{filter_qs}",
            "data/ckan_mock_responses/datastore_search_table_metadata_01.json",
        )
        # Second response is empty, indicating the results are exhausted
        _mock_json_call(
            f"{base_url}/api/3/action/datastore_search?offset=100&{filter_qs}&resource_id=_table_metadata",
            "data/ckan_mock_responses/datastore_search_table_metadata_02.json",
        )

        for resource_id in resources_ids:
            _mock_json_call(
                f"{base_url}/api/3/action/datastore_search?limit=0&resource_id={resource_id}",
                "data/ckan_mock_responses/datastore_search_describe.json",
            )

            # First response gets the data rows
            _mock_json_call(
                f"{base_url}/api/3/action/datastore_search?resource_id={resource_id}",
                "data/ckan_mock_responses/datastore_search_rows.json",
            )
            # Second response is empty, indicating the results are exhausted
            _mock_json_call(
                f"{base_url}/api/3/action/datastore_search?resource_id={resource_id}&offset=100",
                "data/ckan_mock_responses/datastore_search_rows_empty.json",
            )

        package = Package.from_ckan(
            base_url=base_url,
            dataset_id=dataset_id,
            api_key="env:CKAN_API_KEY",
        )

        resource = package.get_resource(resources_ids[1])
        resource.onerror = "raise"  # be strict about errors under test

        self._assert_resource_valid(resource)

    @responses.activate
    def test_read_resource_valid(self):
        resource_id = "79843e49-7974-411c-8eb5-fb2d1111d707"
        base_url = "https://demo.ckan.org"

        _mock_json_call(
            f"{base_url}/api/3/action/datastore_search?limit=0&resource_id={resource_id}",
            "data/ckan_mock_responses/datastore_search_describe.json",
        )

        # First response gets the data rows
        _mock_json_call(
            f"{base_url}/api/3/action/datastore_search?resource_id={resource_id}",
            "data/ckan_mock_responses/datastore_search_rows.json",
        )
        # Second response is empty, indicating the results are exhausted
        _mock_json_call(
            f"{base_url}/api/3/action/datastore_search?resource_id={resource_id}&offset=100",
            "data/ckan_mock_responses/datastore_search_rows_empty.json",
        )

        resource = Resource.from_ckan(
            base_url=base_url,
            resource_id=resource_id,
            api_key="env:CKAN_API_KEY",
        )
        resource.onerror = "raise"  # be strict about errors under test

        self._assert_resource_valid(resource)


@responses.activate
def test_read_package_bad_package_id():
    dataset_id = "bad-dataset-id"
    base_url = "https://demo.ckan.org"

    _mock_json_call(
        f"{base_url}/api/3/action/package_show?id={dataset_id}",
        "data/ckan_mock_responses/ckan_error.json",
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
def test_read_resource_bad_resource_id():
    resource_id = "bad-resource-id"
    base_url = "https://demo.ckan.org"

    _mock_json_call(
        f"{base_url}/api/3/action/datastore_search?limit=0&resource_id={resource_id}",
        "data/ckan_mock_responses/ckan_error.json",
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


class TestDelete:
    def setup_method(self):
        self.resource_id = "79843e49-7974-411c-8eb5-fb2d1111d707"
        self.base_url = "https://demo.ckan.org"
        self.storage = CkanStorage(base_url=self.base_url)
        self.storage._CkanStorage__bucket_cache = [self.resource_id]
        _mock_json_call(
            f"{self.base_url}/api/3/action/datastore_delete",
            "data/ckan_mock_responses/doesnt_matter.json",
            method=responses.POST,
        )

    @responses.activate
    def test_delete_resource_exists(self):
        self.storage.delete_package([self.resource_id])
        assert responses.assert_call_count(
            f"{self.base_url}/api/3/action/datastore_delete", 1
        )

    @responses.activate
    def test_delete_package_exists(self):
        with pytest.raises(exceptions.FrictionlessException) as excinfo:
            self.storage.delete_package(["bad-id"])
        error = excinfo.value.error
        assert error.code == "storage-error"
        assert error.note.count('Table "bad-id" does not exist')

    @responses.activate
    def test_delete_resource_does_not_exist(self):
        self.storage.delete_resource(self.resource_id)
        assert responses.assert_call_count(
            f"{self.base_url}/api/3/action/datastore_delete", 1
        )

    @responses.activate
    def test_delete_package_does_not_exist(self):
        with pytest.raises(exceptions.FrictionlessException) as excinfo:
            self.storage.delete_resource("bad-id")
        error = excinfo.value.error
        assert error.code == "storage-error"
        assert error.note.count('Table "bad-id" does not exist')


class TestWriteDoesNotExist:
    def setup_method(self):
        self.existing_resources_ids = [
            "bd79c992-40f0-454a-a0ff-887f84a792fb",
            "79843e49-7974-411c-8eb5-fb2d1111d707",
        ]
        self.target_resource_id = self.existing_resources_ids[1]
        filter_qs = urllib.parse.urlencode(
            {"filters": json.dumps({"name": self.existing_resources_ids})}
        )
        self.dataset_id = "my-dataset-id"
        self.base_url = "https://demo.ckan.org"

        _mock_json_call(
            f"{self.base_url}/api/3/action/package_show?id={self.dataset_id}",
            "data/ckan_mock_responses/package_show.json",
        )

        _mock_json_call(
            f"{self.base_url}/api/3/action/datastore_search?resource_id=_table_metadata&{filter_qs}",
            "data/ckan_mock_responses/datastore_search_table_metadata_02.json",
        )

        _mock_json_call(
            f"{self.base_url}/api/3/action/datastore_create",
            "data/ckan_mock_responses/doesnt_matter.json",
            method=responses.POST,
        )

        _mock_json_call(
            f"{self.base_url}/api/3/action/datastore_upsert",
            "data/ckan_mock_responses/doesnt_matter.json",
            method=responses.POST,
        )

    @responses.activate
    def test_write_resource(self):
        package = Package("data/storage/types.json")
        package.resources[0].name = self.target_resource_id

        package.resources[0].to_ckan(
            base_url=self.base_url, dataset_id=self.dataset_id, api_key="env:CKAN_API_KEY"
        )
        assert responses.assert_call_count(
            f"{self.base_url}/api/3/action/datastore_upsert", 1
        )

    @responses.activate
    def test_write_package(self):
        package = Package("data/storage/types.json")
        package.resources[0].name = self.target_resource_id

        package.resources[0].to_ckan(
            base_url=self.base_url, dataset_id=self.dataset_id, api_key="env:CKAN_API_KEY"
        )
        assert responses.assert_call_count(
            f"{self.base_url}/api/3/action/datastore_upsert", 1
        )

    @responses.activate
    def test_write_types(self):
        package = Package("data/storage/types.json")
        package.resources[0].name = self.target_resource_id

        package.resources[0].to_ckan(
            base_url=self.base_url, dataset_id=self.dataset_id, api_key="env:CKAN_API_KEY"
        )
        assert json.loads(responses.calls[2].request.body) == {
            "fields": [
                {"id": "any", "type": "text"},  # type fallback
                {"id": "array", "type": "text[]"},
                {"id": "boolean", "type": "bool"},
                {"id": "date", "type": "text"},  # type downgrade
                {"id": "date_year", "type": "text"},  # type downgrade
                {"id": "datetime", "type": "timestamp"},
                {"id": "duration", "type": "text"},  # type fallback
                {"id": "geojson", "type": "json"},
                {"id": "geopoint", "type": "text"},  # type fallback
                {"id": "integer", "type": "int"},
                {"id": "number", "type": "float"},
                {"id": "object", "type": "json"},
                {"id": "string", "type": "text"},
                {"id": "time", "type": "time"},
                {"id": "year", "type": "int"},
                {"id": "yearmonth", "type": "text"},  # type fallback
            ],
            "resource_id": self.target_resource_id,
            "force": True,
            "primary_key": [],
        }

    @responses.activate
    def test_write_integrity(self):
        package = Package("data/storage/integrity.json")
        package.resources[0].name = self.existing_resources_ids[0]
        package.resources[1].name = self.existing_resources_ids[1]
        package.resources[1].schema["foreignKeys"][0]["reference"][
            "resource"
        ] = package.resources[0].name

        package.to_ckan(
            base_url=self.base_url, dataset_id=self.dataset_id, api_key="env:CKAN_API_KEY"
        )
        assert json.loads(responses.calls[2].request.body) == {
            "fields": [
                {"id": "id", "type": "int"},  # constraint removal
                {"id": "parent", "type": "int"},
                {"id": "description", "type": "text"},
            ],
            "resource_id": self.existing_resources_ids[0],
            "force": True,
            "primary_key": ["id"],
            # foreign keys removal
        }
        assert json.loads(responses.calls[6].request.body) == {
            "fields": [
                {"id": "main_id", "type": "int"},  # constraint removal
                {"id": "some_id", "type": "int"},  # constraint removal
                {"id": "description", "type": "text"},  # constraint removal
            ],
            "resource_id": self.existing_resources_ids[1],
            "force": True,
            "primary_key": ["main_id", "some_id"],
            # foreign keys removal
        }

    @responses.activate
    def test_write_constraints(self):
        package = Package("data/storage/constraints.json")
        package.resources[0].name = self.target_resource_id

        package.to_ckan(
            base_url=self.base_url, dataset_id=self.dataset_id, api_key="env:CKAN_API_KEY"
        )
        assert json.loads(responses.calls[2].request.body) == {
            "fields": [
                {"id": "required", "type": "text"},  # constraint removal
                {"id": "minLength", "type": "text"},  # constraint removal
                {"id": "maxLength", "type": "text"},  # constraint removal
                {"id": "pattern", "type": "text"},  # constraint removal
                {"id": "enum", "type": "text"},  # constraint removal
                {"id": "minimum", "type": "int"},  # constraint removal
                {"id": "maximum", "type": "int"},  # constraint removal
            ],
            "resource_id": self.target_resource_id,
            "force": True,
            "primary_key": [],
        }


class TestWriteExists:
    def setup_method(self):
        existing_resources_ids = [
            "bd79c992-40f0-454a-a0ff-887f84a792fb",
            "79843e49-7974-411c-8eb5-fb2d1111d707",
        ]
        self.target_resource_id = existing_resources_ids[1]
        filter_qs = urllib.parse.urlencode(
            {"filters": json.dumps({"name": existing_resources_ids})}
        )
        self.dataset_id = "my-dataset-id"
        self.base_url = "https://demo.ckan.org"

        _mock_json_call(
            f"{self.base_url}/api/3/action/package_show?id={self.dataset_id}",
            "data/ckan_mock_responses/package_show.json",
        )

        # First response gets the _table_metadata results
        _mock_json_call(
            f"{self.base_url}/api/3/action/datastore_search?resource_id=_table_metadata&{filter_qs}",
            "data/ckan_mock_responses/datastore_search_table_metadata_01.json",
        )
        # Second response is empty, indicating the results are exhausted
        _mock_json_call(
            f"{self.base_url}/api/3/action/datastore_search?offset=100&{filter_qs}&resource_id=_table_metadata",
            "data/ckan_mock_responses/datastore_search_table_metadata_02.json",
        )

        _mock_json_call(
            f"{self.base_url}/api/3/action/datastore_delete",
            "data/ckan_mock_responses/doesnt_matter.json",
            method=responses.POST,
        )

        _mock_json_call(
            f"{self.base_url}/api/3/action/datastore_create",
            "data/ckan_mock_responses/doesnt_matter.json",
            method=responses.POST,
        )

        _mock_json_call(
            f"{self.base_url}/api/3/action/datastore_upsert",
            "data/ckan_mock_responses/doesnt_matter.json",
            method=responses.POST,
        )

        self.package = Package("data/storage/types.json")
        self.package.resources[0].name = self.target_resource_id

    @responses.activate
    def test_write_resource_no_force(self):
        with pytest.raises(exceptions.FrictionlessException) as excinfo:
            self.package.to_ckan(
                base_url=self.base_url,
                dataset_id=self.dataset_id,
                api_key="env:CKAN_API_KEY",
            )
        error = excinfo.value.error
        assert error.code == "storage-error"
        assert error.note.count(f'Table "{self.target_resource_id}" already exists')

    @responses.activate
    def test_write_resource_with_force(self):
        self.package.to_ckan(
            base_url=self.base_url,
            dataset_id=self.dataset_id,
            api_key="env:CKAN_API_KEY",
            force=True,
        )
        assert responses.assert_call_count(
            f"{self.base_url}/api/3/action/datastore_upsert", 1
        )

    @responses.activate
    def test_write_package_no_force(self):
        with pytest.raises(exceptions.FrictionlessException) as excinfo:
            self.package.to_ckan(
                base_url=self.base_url,
                dataset_id=self.dataset_id,
                api_key="env:CKAN_API_KEY",
            )
        error = excinfo.value.error
        assert error.code == "storage-error"
        assert error.note.count(f'Table "{self.target_resource_id}" already exists')

    @responses.activate
    def test_write_package_with_force(self):
        self.package.to_ckan(
            base_url=self.base_url,
            dataset_id=self.dataset_id,
            api_key="env:CKAN_API_KEY",
            force=True,
        )
        assert responses.assert_call_count(
            f"{self.base_url}/api/3/action/datastore_upsert", 1
        )
