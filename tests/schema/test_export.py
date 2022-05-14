import json
import yaml
from frictionless import Schema, describe_schema


DESCRIPTOR_MIN = {"fields": [{"name": "id"}, {"name": "height", "type": "integer"}]}


def test_schema_to_copy():
    source = describe_schema("data/table.csv")
    target = source.to_copy()
    assert source is not target
    assert source == target


def test_schema_to_json(tmpdir):
    target = str(tmpdir.join("schema.json"))
    schema = Schema(DESCRIPTOR_MIN)
    schema.to_json(target)
    with open(target, encoding="utf-8") as file:
        assert schema == json.load(file)


def test_schema_to_yaml(tmpdir):
    target = str(tmpdir.join("schema.yaml"))
    schema = Schema(DESCRIPTOR_MIN)
    schema.to_yaml(target)
    with open(target, encoding="utf-8") as file:
        assert schema == yaml.safe_load(file)


def test_schema_from_jsonschema():
    schema = Schema.from_jsonschema("data/ecrin.json")
    assert schema == {
        "fields": [
            {"name": "file_type", "type": "string", "description": "always 'study'"},
            {
                "name": "id",
                "type": "integer",
                "description": "Internal accession number of the study within the MDR database",
                "constraints": {"required": True},
            },
            {
                "name": "display_title",
                "type": "string",
                "description": "By default the public or brief study title. If that is missing then the full scientific title, as used on the protocol document",
                "constraints": {"required": True},
            },
            {
                "name": "brief_description",
                "type": "object",
                "description": "Brief description, usually a few lines, of the study",
            },
            {
                "name": "data_sharing_statement",
                "type": "object",
                "description": "A statement from the sponsor and / or study leads about their intentions for IPD sharing",
            },
            {
                "name": "study_type",
                "type": "object",
                "description": "Categorisation of study type, e.g. 'Interventional', or 'Observational'",
            },
            {
                "name": "study_status",
                "type": "object",
                "description": "Categorisation of study status, e.g. 'Active, not recruiting', or 'Completed'",
            },
            {
                "name": "study_enrolment",
                "type": "integer",
                "description": "The anticipated or actual total number of participants in the clinical study.",
            },
            {
                "name": "study_gender_elig",
                "type": "object",
                "description": "Whether the study is open to all genders, or just male or female",
            },
            {
                "name": "min_age",
                "type": "object",
                "description": "The minimum age, if any, for a study participant",
            },
            {
                "name": "max_age",
                "type": "object",
                "description": "The maximum age, if any, for a study participant",
            },
            {"name": "study_identifiers", "type": "array"},
            {"name": "study_titles", "type": "array"},
            {"name": "study_features", "type": "array"},
            {"name": "study_topics", "type": "array"},
            {"name": "study_relationships", "type": "array"},
            {"name": "linked_data_objects", "type": "array"},
            {
                "name": "provenance_string",
                "type": "string",
                "description": "A listing of the source or sources (usually a trial registry) from which the data for the study has been drawn, and the date-time(s) when the data was last downloaded",
            },
        ]
    }
