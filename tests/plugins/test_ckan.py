import datetime
from frictionless import Package


# Storage


def test_storage_types():
    url = "https://demo.ckan.org/"
    dataset = "frictionless"
    apikey = "51912f57-a657-4caa-b2a7-0a1c16821f4b"

    # Export/Import
    source = Package("data/storage/types.json")
    storage = source.to_ckan(url=url, dataset=dataset, apikey=apikey, force=True)
    target = Package.from_ckan(url=url, dataset=dataset)

    # Assert metadata
    assert target.get_resource("types").schema == {
        "fields": [
            {"name": "any", "type": "string"},  # type fallback
            {"name": "array", "type": "string"},  # type fallback
            {"name": "boolean", "type": "boolean"},
            {"name": "date", "type": "date"},
            {"name": "date_year", "type": "date"},  # format removal
            {"name": "datetime", "type": "datetime"},
            {"name": "duration", "type": "string"},  # type fallback
            {"name": "geojson", "type": "string"},  # type fallback
            {"name": "geopoint", "type": "string"},  # type fallback
            {"name": "integer", "type": "integer"},
            {"name": "number", "type": "number"},
            {"name": "object", "type": "string"},  # type fallback
            {"name": "string", "type": "string"},
            {"name": "time", "type": "time"},
            {"name": "year", "type": "integer"},  # type downgrade
            {"name": "yearmonth", "type": "string"},  # type fallback
        ],
    }

    # Assert data
    assert target.get_resource("types").read_rows() == [
        {
            "any": "中国人",
            "array": '["Mike", "John"]',
            "boolean": True,
            "date": datetime.date(2015, 1, 1),
            "date_year": datetime.date(2015, 1, 1),
            "datetime": datetime.datetime(2015, 1, 1, 3, 0),
            "duration": "P1Y1M",
            "geojson": '{"type": "Point", "coordinates": [33, 33.33]}',
            "geopoint": "30,70",
            "integer": 1,
            "number": 7,
            "object": '{"chars": 560}',
            "string": "english",
            "time": datetime.time(3, 0),
            "year": 2015,
            "yearmonth": "2015-01",
        },
    ]

    # Cleanup storage
    storage.delete_package(target.resource_names)
