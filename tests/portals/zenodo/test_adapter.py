# type: ignore
import pytest
from decimal import Decimal
from frictionless import portals, Catalog, Package, FrictionlessException


PACKAGE_WITHOUT_DP = {
    "title": "Frictionless Data Test Dataset Without Descriptor",
    "resources": [
        {
            "name": "capitals",
            "type": "table",
            "path": "capitals.csv",
            "scheme": "https",
            "format": "csv",
            "encoding": "utf-8",
            "mediatype": "text/csv",
            "dialect": {"csv": {"skipInitialSpace": True}},
            "schema": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "cid", "type": "integer"},
                    {"name": "name", "type": "string"},
                ]
            },
        },
        {
            "name": "table",
            "type": "table",
            "path": "table.xls",
            "scheme": "https",
            "format": "xls",
            "encoding": "utf-8",
            "mediatype": "application/vnd.ms-excel",
            "schema": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"},
                ]
            },
        },
    ],
}
PACKAGE_WITH_DP = {
    "title": "Frictionless Data Test Dataset",
    "name": "testing",
    "resources": [
        {
            "name": "data",
            "path": "data.csv",
            "schema": {
                "fields": [
                    {"name": "id", "type": "string", "constraints": {"required": True}},
                    {"name": "name", "type": "string"},
                    {"name": "description", "type": "string"},
                    {"name": "amount", "type": "number"},
                ],
                "primaryKey": ["id"],
            },
        },
        {
            "name": "data2",
            "path": "data2.csv",
            "schema": {
                "fields": [
                    {"name": "parent", "type": "string"},
                    {"name": "comment", "type": "string"},
                ],
                "foreignKeys": [
                    {
                        "fields": ["parent"],
                        "reference": {"resource": "data", "fields": ["id"]},
                    }
                ],
            },
        },
    ],
}

ZIPPED_PACKAGE_WITH_DP = {
    "name": "testing",
    "title": "Frictionless Data Test Dataset Zip -2",
    "resources": [
        {
            "name": "data",
            "path": "data.csv",
            "schema": {
                "fields": [
                    {"name": "id", "type": "string", "constraints": {"required": True}},
                    {"name": "name", "type": "string"},
                    {"name": "description", "type": "string"},
                    {"name": "amount", "type": "number"},
                ],
                "primaryKey": ["id"],
            },
        },
        {
            "name": "data2",
            "path": "data2.csv",
            "schema": {
                "fields": [
                    {"name": "parent", "type": "string"},
                    {"name": "comment", "type": "string"},
                ],
                "foreignKeys": [
                    {
                        "fields": ["parent"],
                        "reference": {"resource": "data", "fields": ["id"]},
                    }
                ],
            },
        },
    ],
}

# Read


@pytest.mark.vcr
def test_zenodo_adapter_read_record_without_descriptor(options_without_dp):
    url = options_without_dp.pop("url")
    package = Package(url)
    package.infer()
    assert len(package.resources) == 2
    assert package.to_descriptor() == PACKAGE_WITHOUT_DP


@pytest.mark.vcr
def test_zenodo_adapter_read_record_using_alias_function(options_without_dp):
    url = options_without_dp.pop("url")
    package = Package(url)
    package.infer()
    assert len(package.resources) == 2
    assert package.to_descriptor() == PACKAGE_WITHOUT_DP


@pytest.mark.vcr
def test_zenodo_adapter_read_record_basepath_isset(options_without_dp):
    url = options_without_dp.pop("url")
    package = Package(url)
    assert package.resources[0].path == "capitals.csv"
    assert (
        package.resources[0].basepath
        == "https://zenodo.org/api/files/d24cde89-1d38-4713-b6f2-6a3796e458a6"
    )


@pytest.mark.vcr
def test_zenodo_adapter_read_record_with_descriptor_basepath_isset(options_with_dp):
    url = options_with_dp.pop("url")
    package = Package(url)
    assert package.resources[0].path == "data.csv"
    assert (
        package.resources[0].basepath
        == "https://zenodo.org/api/files/bc520c46-ee9e-4245-8c57-2a7203062e14"
    )


@pytest.mark.vcr
def test_zenodo_adapter_read_record_without_apikey(options_without_dp):
    url = options_without_dp.pop("url")
    control = portals.ZenodoControl(apikey=None)
    package = Package(url, control=control)
    package.infer()
    assert control.apikey == None
    assert package.to_descriptor() == PACKAGE_WITHOUT_DP


@pytest.mark.vcr
def test_zenodo_adapter_read_record_only_csv(options_with_dp_multiple_files_without_dp):
    url = options_with_dp_multiple_files_without_dp.pop("url")
    control = portals.ZenodoControl(formats=["csv"])
    package = Package(url, control=control)
    package.infer()
    assert len(package.resources) == 1
    assert package.to_descriptor() == {
        "title": "Frictionless Data Test Dataset Multiple File Types Without Descriptor",
        "resources": [
            {
                "name": "capitals",
                "type": "table",
                "path": "capitals.csv",
                "scheme": "https",
                "format": "csv",
                "encoding": "utf-8",
                "mediatype": "text/csv",
                "dialect": {"csv": {"skipInitialSpace": True}},
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "cid", "type": "integer"},
                        {"name": "name", "type": "string"},
                    ]
                },
            }
        ],
    }


@pytest.mark.vcr
def test_zenodo_adapter_read_record_with_datapackage_descriptor(options_with_dp):
    url = options_with_dp.pop("url")
    package = Package(url)
    assert len(package.resources) == 2
    assert package.to_descriptor() == PACKAGE_WITH_DP


@pytest.mark.vcr
def test_zenodo_adapter_read_record_with_datapackage_descriptor_zipped_files(
    options_with_dp_multiple_files_with_zipped_files,
):
    url = options_with_dp_multiple_files_with_zipped_files.pop("url")
    package = Package(url)
    assert len(package.resources) == 2
    assert package.to_descriptor() == ZIPPED_PACKAGE_WITH_DP


@pytest.mark.vcr
def test_zenodo_adapter_read_record_without_datapackage_descriptor_zipped_files(
    options_without_dp_with_zipped_files,
):
    # zipped folder but without package.json file
    url = options_without_dp_with_zipped_files.pop("url")
    with pytest.raises(FrictionlessException) as excinfo:
        Package(url)
    error = excinfo.value.error
    assert error.message == "Package/s not found"


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_with_wrong_record():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("https://zenodo.org/record/68358988")
    error = excinfo.value.error
    assert error.message == "Zenodo API errorKeyError('metadata')"


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_with_wrong_url():
    with pytest.raises(FrictionlessException) as excinfo:
        Package("https://zenodo.org/6835898")
    error = excinfo.value.error
    assert error.message == "Record is required."


@pytest.mark.vcr
def test_zenodo_adapter_read_record_with_control_param_record(options_without_dp):
    record = options_without_dp.pop("record")
    control = portals.ZenodoControl(record=record)
    package = Package(control=control)
    package.infer()
    assert len(package.resources) == 2
    assert package.to_descriptor() == PACKAGE_WITHOUT_DP


@pytest.mark.vcr
def test_zenodo_adapter_read_record_without_record_and_url():
    control = portals.ZenodoControl()
    with pytest.raises(FrictionlessException) as excinfo:
        Package(control=control)
    error = excinfo.value.error
    assert error.message == "Record is required."


@pytest.mark.vcr
def test_zenodo_adapter_read_record_with_empty_package(
    options_with_dp_multiple_files_without_dp,
):
    record = options_with_dp_multiple_files_without_dp.pop("record")
    with pytest.raises(FrictionlessException) as excinfo:
        Package(control=portals.ZenodoControl(record=record, formats=["tst"]))
    error = excinfo.value.error
    assert error.message == "Package/s not found"


# Read - Data


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data(options_without_dp):
    url = options_without_dp.pop("url")
    package = Package(url)
    assert len(package.resources) == 2
    assert package.resources[0].read_rows() == [
        {"id": 1, "cid": 1, "name": "London"},
        {"id": 2, "cid": 2, "name": "Paris"},
        {"id": 3, "cid": 3, "name": "Berlin"},
        {"id": 4, "cid": 4, "name": "Rome"},
        {"id": 5, "cid": 5, "name": "Lisbon"},
    ]


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_with_datapackage_descriptor(options_with_dp):
    url = options_with_dp.pop("url")
    package = Package(url)
    assert len(package.resources) == 2
    assert package.resources[0].read_rows() == [
        {
            "id": "A3001",
            "name": "Taxes",
            "description": "Taxes we collect",
            "amount": Decimal("10000.5"),
        },
        {
            "id": "A5032",
            "name": "Parking Fees",
            "description": "Parking fees we collect",
            "amount": Decimal("2000.5"),
        },
    ]


@pytest.mark.vcr
def test_zenodo_adapter_read_record_and_validate(options_with_dp):
    url = options_with_dp.pop("url")
    package = Package(url)
    report = package.validate()
    assert report.valid is True


@pytest.mark.vcr
def test_zenodo_adapter_read_record_and_analyze(options_with_dp):
    url = options_with_dp.pop("url")
    package = Package(url)
    analysis = package.analyze()
    assert analysis["data"]["rows"] == 2
    assert analysis["data2"]["rows"] == 3


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_with_datapackage_descriptor_zipped_files(
    options_with_dp_multiple_files_with_zipped_files,
):
    url = options_with_dp_multiple_files_with_zipped_files.pop("url")
    package = Package(url)
    assert len(package.resources) == 2
    assert package.resources[0].read_rows() == [
        {
            "id": "A3001",
            "name": "Taxes",
            "description": "Taxes we collect",
            "amount": Decimal("10000.5"),
        },
        {
            "id": "A5032",
            "name": "Parking Fees",
            "description": "Parking fees we collect",
            "amount": Decimal("2000.5"),
        },
    ]


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_from_zipped_file(
    options_with_zipped_resource_file,
):
    url = options_with_zipped_resource_file.pop("url")
    package = Package(url)
    assert package.resources[0].name == "address3"


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_xls(options_with_dp_multiple_files_without_dp):
    record = options_with_dp_multiple_files_without_dp.pop("record")
    package = Package(control=portals.ZenodoControl(record=record, formats=["xls"]))
    assert package.resources[0].name == "table"
    assert package.resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_xlsx(options_with_dp_multiple_files_without_dp):
    record = options_with_dp_multiple_files_without_dp.pop("record")
    package = Package(control=portals.ZenodoControl(record=record, formats=["xlsx"]))
    assert package.resources[0].name == "table"
    assert package.resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_tsv(options_with_dp_multiple_files_without_dp):
    record = options_with_dp_multiple_files_without_dp.pop("record")
    package = Package(control=portals.ZenodoControl(record=record, formats=["tsv"]))
    assert package.resources[0].name == "table"
    assert package.resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
        {"id": 3, "name": "\\N"},
    ]


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_ods(options_with_dp_multiple_files_without_dp):
    record = options_with_dp_multiple_files_without_dp.pop("record")
    package = Package(control=portals.ZenodoControl(record=record, formats=["ods"]))
    assert package.resources[0].name == "table"
    assert package.resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_ndjson(
    options_with_dp_multiple_files_without_dp,
):
    record = options_with_dp_multiple_files_without_dp.pop("record")
    package = Package(control=portals.ZenodoControl(record=record, formats=["ndjson"]))
    assert package.resources[0].name == "table"
    assert package.resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_jsonl(options_with_dp_multiple_files_without_dp):
    record = options_with_dp_multiple_files_without_dp.pop("record")
    package = Package(control=portals.ZenodoControl(record=record, formats=["jsonl"]))
    assert package.resources[0].name == "table"
    assert package.resources[0].read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.vcr
def test_zenodo_adapter_read_record_data_remote(options_with_dp_with_remote_resources):
    record = options_with_dp_with_remote_resources.pop("record")
    package = Package(control=portals.ZenodoControl(record=record))
    assert package.resources[0].name == "first-http-resource"
    assert package.resources[0].read_rows() == [
        {"id": 1, "cid": "1", "name": "London"},
        {"id": 2, "cid": "2", "name": "Paris"},
        {"id": 3, "cid": "3", "name": "Berlin"},
        {"id": 4, "cid": "4", "name": "Rome"},
        {"id": 5, "cid": "5", "name": "Lisbon"},
    ]


# Write


@pytest.mark.vcr
def test_zenodo_adapter_write(tmp_path):
    control = portals.ZenodoControl(
        metafn="data/zenodo/metadata.json",
        tmp_path=tmp_path,
    )
    package = Package("data/datapackage.json")
    deposition_id = package.publish(control=control)
    assert deposition_id == 7098723


@pytest.mark.vcr
def test_zenodo_adapter_write_ods(tmp_path):
    control = portals.ZenodoControl(
        metafn="data/zenodo/ods.metadata.json",
        tmp_path=tmp_path,
    )
    package = Package("data/ods.datapackage.json")
    deposition_id = package.publish(control=control)
    assert deposition_id == 7098739


@pytest.mark.vcr
def test_zenodo_adapter_write_jsonl(tmp_path):
    control = portals.ZenodoControl(
        metafn="data/zenodo/jsonl.metadata.json",
        tmp_path=tmp_path,
    )
    package = Package("data/jsonl.datapackage.json")
    deposition_id = package.publish(control=control)
    assert deposition_id == 7098741


@pytest.mark.vcr
def test_zenodo_adapter_write_ndjson(tmp_path):
    control = portals.ZenodoControl(
        metafn="data/zenodo/ndjson.metadata.json",
        tmp_path=tmp_path,
    )
    package = Package("data/ndjson.datapackage.json")
    deposition_id = package.publish(control=control)
    assert deposition_id == 7098743


@pytest.mark.vcr
def test_zenodo_adapter_write_with_descriptor(tmp_path):
    descriptor = {
        "name": "test-tabulator",
        "resources": [
            {
                "name": "first-resource",
                "path": "data/table.xls",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "number"},
                        {"name": "name", "type": "string"},
                    ]
                },
            }
        ],
    }
    control = portals.ZenodoControl(
        metafn="data/zenodo/metadata.json",
        tmp_path=tmp_path,
    )
    package = Package(descriptor)
    deposition_id = package.publish(control=control)
    assert deposition_id == 7098745


@pytest.mark.vcr
def test_zenodo_adapter_write_without_apikey():
    control = portals.ZenodoControl(
        metafn="data/zenodo/metadata.json",
        apikey=None,
    )
    package = Package("data/datapackage.json")
    with pytest.raises(AssertionError) as excinfo:
        package.publish(control=control)
    assert "AssertionError" in str(excinfo)


@pytest.mark.vcr
def test_zenodo_adapter_write_without_wrong_apikey():
    control = portals.ZenodoControl(
        metafn="data/zenodo/metadata.json",
        apikey="test",
    )
    package = Package("data/datapackage.json")
    with pytest.raises(FrictionlessException) as excinfo:
        package.publish(control=control)
    error = excinfo.value.error
    assert (
        "You either supplied the wrong credentials (e.g. a bad password),"
        in error.message
    )


@pytest.mark.vcr
def test_zenodo_adapter_write_without_metadata(tmp_path):
    control = portals.ZenodoControl(
        tmp_path=tmp_path,
    )
    package = Package("data/datapackage.json")
    with pytest.raises(FrictionlessException) as excinfo:
        package.publish(control=control)
    error = excinfo.value.error
    assert "Zenodo API Metadata Creation error" in error.message


@pytest.mark.vcr
def test_zenodo_adapter_write_default_base_url(tmp_path):
    control = portals.ZenodoControl(
        tmp_path=tmp_path,
    )
    assert control.base_url == "https://zenodo.org/api/"


@pytest.mark.vcr
def test_zenodo_adapter_write_without_base_url():
    control = portals.ZenodoControl(base_url=None)
    package = Package("data/datapackage.json")
    with pytest.raises(AssertionError) as excinfo:
        package.publish(control=control)
    assert "AssertionError" in str(excinfo)


@pytest.mark.vcr
def test_zenodo_adapter_write_read_package_published_to_zenodo():
    package = Package("https://zenodo.org/record/7096849")
    assert package.resources[1].read_rows() == [
        {"id": 1, "name": "中国人"},
        {"id": 2, "name": "english"},
    ]


@pytest.mark.vcr
def test_zenodo_adapter_write_resources_with_inline_data(tmp_path):
    descriptor = {
        "name": "test-package-with_inline-data",
        "resources": [{"name": "test", "data": [{"a": 1, "b": 2}]}],
    }
    control = portals.ZenodoControl(
        metafn="data/zenodo/data.metadata.json",
        tmp_path=tmp_path,
    )
    package = Package(descriptor)
    deposition_id = package.publish(control=control)
    assert deposition_id == 7098747


@pytest.mark.vcr
def test_zenodo_adapter_write_resources_with_remote_url(tmp_path):
    descriptor = {
        "name": "test-repo-resources-with-http-data-csv",
        "resources": [
            {
                "name": "first-http-resource",
                "path": "https://raw.githubusercontent.com/fdtester/test-repo-with-datapackage-yaml/master/data/capitals.csv",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer"},
                        {"name": "cid", "type": "string"},
                        {"name": "name", "type": "string"},
                    ]
                },
            }
        ],
    }
    control = portals.ZenodoControl(
        metafn="data/zenodo/remote.metadata.json",
        tmp_path=tmp_path,
    )
    package = Package(descriptor)
    deposition_id = package.publish(control=control)
    assert deposition_id == 7098749


@pytest.mark.vcr
def test_zenodo_adapter_write_resources_with_deposition_id(tmp_path):
    control = portals.ZenodoControl(
        metafn="data/zenodo/deposition.metadata.json",
        tmp_path=tmp_path,
        deposition_id=7098476,
    )
    package = Package("data/datapackage.json")
    deposition_id = package.publish(control=control)
    assert deposition_id == 7098476


@pytest.mark.vcr
def test_zenodo_adapter_write_resources_with_deposition_url(tmp_path):
    control = portals.ZenodoControl(
        metafn="data/zenodo/depositionurl.metadata.json",
        tmp_path=tmp_path,
    )
    package = Package("data/datapackage.json")
    deposition_id = package.publish("https://zenodo.org/deposit/7098479", control=control)
    assert deposition_id == 7098479


@pytest.mark.vcr
def test_zenodo_adapter_write_resources_to_publish(tmp_path):
    control = portals.ZenodoControl(
        metafn="data/zenodo/publish.metadata.json",
        tmp_path=tmp_path,
    )
    package = Package("data/datapackage.json")
    deposition_id = package.publish(control=control)
    assert deposition_id == 7098751


@pytest.mark.skip
@pytest.mark.vcr
def test_zenodo_adapter_write_resources_in_sandbox_without_metafile_partial_package_metadata(
    sandbox_api, tmp_path
):
    control = portals.ZenodoControl(
        apikey=sandbox_api, base_url="https://sandbox.zenodo.org/api/", tmp_path=tmp_path
    )
    package = Package("data/package/zenodo.packagepartialmeta.json")
    deposition_id = package.publish(control=control)
    assert deposition_id == 1132344


@pytest.mark.skip
@pytest.mark.vcr
def test_zenodo_adapter_write_resources_with_metadata_json(sandbox_api, tmp_path):
    control = portals.ZenodoControl(
        apikey=sandbox_api,
        tmp_path=tmp_path,
        base_url="https://sandbox.zenodo.org/api/",
        metafn={
            "creators": [{"name": "FD Tester", "affiliation": "FD Testing"}],
            "upload_type": "dataset",
            "title": "Test File",
            "description": "Test File",
        },
    )
    package = Package("data/package.json")
    deposition_id = package.publish(control=control)
    assert deposition_id == 1139855


@pytest.mark.skip
@pytest.mark.vcr
def test_zenodo_adapter_write_resources_in_sandbox_without_metafile(
    sandbox_api, tmp_path
):
    control = portals.ZenodoControl(
        apikey=sandbox_api, base_url="https://sandbox.zenodo.org/api/", tmp_path=tmp_path
    )
    package = Package("data/package/zenodo.packagewithmeta.json")
    deposition_id = package.publish(control=control)
    assert deposition_id == 1132346


@pytest.mark.vcr
def test_zenodo_adapter_write_resources_without_metafile(tmp_path):
    control = portals.ZenodoControl(tmp_path=tmp_path)
    package = Package("data/package/zenodo.packagewithmeta.json")
    deposition_id = package.publish(control=control)
    assert deposition_id == 7373765


# Read - Catalog


# TODO: recover
@pytest.mark.skip
@pytest.mark.vcr
def test_zenodo_adapter_catalog_search():
    control = portals.ZenodoControl(search='notes:"TDWD"')
    catalog = Catalog(control=control)
    assert catalog.packages[0].to_descriptor() == PACKAGE_WITHOUT_DP


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_by_notes():
    control = portals.ZenodoControl(search='notes:"TDBASIC"')
    catalog = Catalog(control=control)
    package = catalog.packages[0].to_descriptor()
    assert package["title"] == "Frictionless Data Test Dataset"


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_by_title():
    control = portals.ZenodoControl(
        search='title:"Frictionless Data Test Dataset Without Descriptor"'
    )
    catalog = Catalog(control=control)
    package = catalog.packages[0].to_descriptor()
    assert package["title"] == "Frictionless Data Test Dataset Without Descriptor"


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_by_creators_name():
    control = portals.ZenodoControl(search='creators.name:"FD Tester Creator"')
    catalog = Catalog(control=control)
    package = catalog.packages[0].to_descriptor()
    assert package["title"] == "Frictionless Data Test Dataset"


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_by_doi():
    control = portals.ZenodoControl(doi="10.5281/zenodo.7078768")
    catalog = Catalog(control=control)
    assert len(catalog.packages) == 1
    assert len(catalog.packages[0].resources) == 2


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_by_all_versions():
    control = portals.ZenodoControl(search='creators.name:"FD Tester"', all_versions=True)
    catalog = Catalog(control=control)
    assert len(catalog.packages) == 6
    assert catalog.packages[1].to_descriptor() == PACKAGE_WITH_DP


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_by_type():
    control = portals.ZenodoControl(search='creators.name:"FD Tester"', rtype="dataset")
    catalog = Catalog(control=control)
    assert len(catalog.packages) == 3


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_by_subtype():
    control = portals.ZenodoControl(
        search='creators.name:"FD Tester"', rtype="publication"
    )
    catalog = Catalog(control=control)
    assert len(catalog.packages) == 2
    assert catalog.packages[0].title == "Frictionless Data Test Publication Journal"
    assert catalog.packages[1].title == "Frictionless Data Test Publication"


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_by_bounds():
    control = portals.ZenodoControl(
        bounds="-124.277344,30.221102,-78.310547,49.152970",
        rtype="dataset",
        page=1,
        size=4,
    )
    catalog = Catalog(control=control)
    assert len(catalog.packages) == 1
    assert (
        catalog.packages[0].title
        == "Predicting drought tolerance from slope aspect preference in restored plant communities"
    )


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_by_size_and_page():
    control = portals.ZenodoControl(
        page=1, size=2, search='title:"Frictionless Data Test"'
    )
    catalog = Catalog(control=control)
    assert len(catalog.packages) == 2


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_sort_by_bestmatch():
    control = portals.ZenodoControl(
        search='creators.name:"FD Tester"', sort="bestmatch", page=1, size=1
    )
    catalog = Catalog(control=control)
    assert catalog.packages[0].title == "Frictionless Data Test Dataset - Draft"


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_sort_by_mostrecent():
    control = portals.ZenodoControl(
        search='creators.name:"FD Tester"', sort="mostrecent", page=1, size=1
    )
    catalog = Catalog(control=control)
    assert catalog.packages[0].title == "Test Write File - Remote"


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_sort_by_mostrecent_desc():
    control = portals.ZenodoControl(
        search='creators.name:"FD Tester"', sort="-mostrecent", page=1, size=1
    )
    catalog = Catalog(control=control)
    assert catalog.packages[0].title == "Frictionless Data Test Dataset"


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_with_communities():
    control = portals.ZenodoControl(rtype="dataset", communities="zenodo", page=3, size=1)
    catalog = Catalog(control=control)
    assert len(catalog.packages) == 1
    assert (
        catalog.packages[0].title.strip()
        == "Electrical half hourly raw and cleaned datasets for Great Britain from 2008-11-05"
    )


@pytest.mark.vcr
def test_zenodo_adapter_catalog_search_by_custom():
    control = portals.ZenodoControl(rcustom="[dwc:family]:[Felidae]")
    # No data package matches with the above custom keyword so
    # empty packages are returned
    with pytest.raises(FrictionlessException) as excinfo:
        Catalog(control=control)
    error = excinfo.value.error
    assert error.message == "Package/s not found"


# TODO: recover
@pytest.mark.skip
@pytest.mark.vcr
def test_zenodo_adapter_catalog_single_record():
    control = portals.ZenodoControl(record="7078768")
    catalog = Catalog(control=control)
    assert catalog.packages[0].to_descriptor() == PACKAGE_WITHOUT_DP


# Extra


def test_zenodo_adapter_metadata():
    metafn = portals.zenodo.adapter.generate_metadata
    package = Package("https://zenodo.org/record/7373765")
    metadata = metafn(package)
    assert "frictionlessdata" in metadata["metadata"]["keywords"]


def test_zenodo_adapter_metadata_json():
    metadata = portals.zenodo.adapter.generate_metadata(
        metadata={
            "creators": [{"name": "FD Tester", "affiliation": "FD Testing"}],
            "upload_type": "dataset",
            "title": "Test File",
            "description": "Test File",
        }
    )
    assert "frictionlessdata" in metadata["metadata"]["keywords"]
