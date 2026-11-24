import json
import socket
import sys

import pytest
import referencing.exceptions
import requests
import urllib3
import yaml

from frictionless import FrictionlessException, Package, Resource, system

# General


@pytest.mark.vcr
@pytest.mark.skipif(sys.version_info < (3, 10), reason="pytest-vcr bug in Python3.8/9")
def test_package_profiles_invalid_local():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile=profile)
    with pytest.raises(FrictionlessException) as excinfo:
        package.to_descriptor(validate=True)
    reasons = excinfo.value.reasons
    assert len(reasons) == 5
    for error in reasons:
        assert "required" in error.message


@pytest.mark.vcr
@pytest.mark.skipif(sys.version_info < (3, 10), reason="pytest-vcr bug in Python3.8/9")
def test_package_profiles_invalid_local_from_descriptor():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [resource.to_descriptor()], "profile": profile})
    reasons = excinfo.value.reasons
    assert len(reasons) == 5
    for error in reasons:
        assert "required" in error.message


# TODO: recover
@pytest.mark.skip
@pytest.mark.vcr
def test_package_external_profile_invalid_remote():
    profile = (
        "https://raw.githubusercontent.com/tdwg/camtrap-dp/main/camtrap-dp-profile.json"
    )
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile=profile)
    with pytest.raises(FrictionlessException) as excinfo:
        package.to_descriptor(validate=True)
    reasons = excinfo.value.reasons
    assert len(reasons) == 5
    for error in reasons:
        assert "required" in error.message


# TODO: recover
@pytest.mark.skip
@pytest.mark.vcr
def test_package_external_profile_invalid_remote_from_descriptor():
    profile = (
        "https://raw.githubusercontent.com/tdwg/camtrap-dp/main/camtrap-dp-profile.json"
    )
    resource = Resource(name="table", path="data/table.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [resource.to_descriptor()], "profile": profile})
    reasons = excinfo.value.reasons
    assert len(reasons) == 5
    for error in reasons:
        assert "required" in error.message


def test_package_profile_unresolvable_ref_issue_1812(requests_mock):
    # A profile whose "$ref" cannot be fetched must not crash validation with a
    # jsonschema-internal exception: validate() has to return a report instead
    requests_mock.get(
        "https://example.org/schemas/missing.json",
        exc=requests.exceptions.SSLError("[SSL: CERTIFICATE_VERIFY_FAILED]"),
    )
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile="data/profiles/unresolvable-ref.json")
    report = package.validate()
    assert not report.valid
    assert "failed to resolve json-schema profile" in report.errors[0].note


def test_package_profile_unresolvable_ref_keeps_cause_issue_1812(requests_mock):
    # cause information should be preserved
    requests_mock.get(
        "https://example.org/schemas/missing.json",
        exc=requests.exceptions.SSLError("[SSL: CERTIFICATE_VERIFY_FAILED]"),
    )
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile="data/profiles/unresolvable-ref.json")
    with pytest.raises(FrictionlessException) as excinfo:
        package.to_descriptor(validate=True)
    causes = []
    cause = excinfo.value.__cause__
    while cause is not None:
        causes.append(cause)
        cause = cause.__cause__
    assert any(isinstance(cause, requests.exceptions.SSLError) for cause in causes)


def _connection_error(reason):
    """A requests.ConnectionError faithful to what urllib3 raises"""
    return requests.exceptions.ConnectionError(
        urllib3.exceptions.MaxRetryError(
            None, "https://example.org/schemas/missing.json", reason
        )
    )


def _name_resolution_error(host):
    """A urllib3 2.x NameResolutionError (DNS failure)

    urllib3 1.26 has no NameResolutionError (some environments resolve to it,
    e.g. Python 3.9). The note extraction under test is class-agnostic, so the
    urllib3 2.x error is simulated with NewConnectionError on such versions.
    """
    reason = socket.gaierror(-2, "Name or service not known")
    conn = urllib3.connection.HTTPSConnection(host, 443)
    error_class = getattr(urllib3.exceptions, "NameResolutionError", None)
    if error_class is not None:
        return error_class(host, conn, reason)
    return urllib3.exceptions.NewConnectionError(
        conn, f"Failed to resolve '{host}' ({reason})"
    )


# Network errors are reported concisely, instead of the verbose urllib3
# message, which repeats the URL and hides the low-level cause
@pytest.mark.parametrize(
    "exception, reason",
    [
        pytest.param(
            _connection_error(_name_resolution_error("no-such-host.invalid")),
            "Failed to resolve 'no-such-host.invalid' "
            "([Errno -2] Name or service not known)",
            id="dns",
        ),
        pytest.param(
            _connection_error(
                urllib3.exceptions.NewConnectionError(
                    urllib3.connection.HTTPConnection("localhost", 9),
                    "Failed to establish a new connection: "
                    "[Errno 111] Connection refused",
                )
            ),
            "Failed to establish a new connection: [Errno 111] Connection refused",
            id="refused",
        ),
        pytest.param(
            _connection_error(
                urllib3.exceptions.ConnectTimeoutError(
                    None, "Connection to 192.0.2.1 timed out. (connect timeout=10)"
                )
            ),
            "Connection to 192.0.2.1 timed out. (connect timeout=10)",
            id="connect_timeout",
        ),
        pytest.param(
            requests.exceptions.ReadTimeout(
                urllib3.exceptions.ReadTimeoutError(
                    urllib3.connectionpool.HTTPConnectionPool("127.0.0.1", 443),
                    "https://example.org/schemas/missing.json",
                    "Read timed out. (read timeout=10)",
                )
            ),
            "Read timed out. (read timeout=10)",
            id="read_timeout",
        ),
    ],
)
def test_package_profile_remote_retrieval_network_error_note(
    exception, reason, requests_mock
):
    requests_mock.get("https://example.org/schemas/missing.json", exc=exception)
    resource = Resource(name="table", path="data/table.csv")
    package = Package(resources=[resource], profile="data/profiles/unresolvable-ref.json")
    report = package.validate()
    assert not report.valid
    note = report.errors[0].note
    assert (
        'cannot retrieve metadata "https://example.org/schemas/missing.json" '
        f'because "{reason}"' in note
    )
    # the urllib3 boilerplate is not repeated in the note
    assert "Max retries exceeded" not in note
    assert "HTTPSConnectionPool" not in note


# A failing JSON pointer or anchor must not disclose the content of the
# referenced document: a "$ref" can target any file of the working directory
@pytest.mark.parametrize(
    "ref, reason",
    [
        (
            "secret.json#/nope",
            "JSON pointer '/nope' does not exist within the referenced document",
        ),
        (
            "secret.json#/",
            "JSON pointer '/' does not exist within the referenced document "
            "(to point to the whole document, use '#')",
        ),
        (
            "secret.json#nope",
            "anchor 'nope' does not exist within the referenced document",
        ),
        (
            "#/nope",
            "JSON pointer '/nope' does not exist within the referenced document",
        ),
    ],
)
def test_package_profile_ref_error_does_not_disclose_document(
    ref, reason, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    secret = {"db_password": "s3cr3t"}
    (tmp_path / "secret.json").write_text(json.dumps(secret))
    (tmp_path / "profile.json").write_text(json.dumps({"allOf": [{"$ref": ref}]}))
    descriptor = {
        "profile": "profile.json",
        "resources": [{"name": "table", "data": [["id"], [1]]}],
    }
    report = Package.validate_descriptor(descriptor)
    notes = [error.note for error in report.errors]
    assert notes == [f'failed to resolve json-schema profile because "{reason}"']
    # the content of the referenced document is not disclosed
    assert "s3cr3t" not in notes[0]
    assert "db_password" not in notes[0]


# The redacted note keeps the original exception in the cause chain,
# so that --debug can still show the referenced document
def test_package_profile_pointer_error_keeps_cause(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "secret.json").write_text(json.dumps({"db_password": "s3cr3t"}))
    (tmp_path / "profile.json").write_text(
        json.dumps({"allOf": [{"$ref": "secret.json#/nope"}]})
    )
    descriptor = {
        "profile": "profile.json",
        "resources": [{"name": "table", "data": [["id"], [1]]}],
    }
    with pytest.raises(FrictionlessException) as excinfo:
        Package(descriptor).to_descriptor(validate=True)
    causes = []
    cause = excinfo.value.__cause__
    while cause is not None:
        causes.append(cause)
        cause = cause.__cause__
    assert any(
        isinstance(cause, referencing.exceptions.PointerToNowhere) for cause in causes
    )


# A remote "$ref" in a profile is resolved by frictionless (http session),
# not by jsonschema's deprecated automatic retrieval
@pytest.mark.filterwarnings("error::DeprecationWarning")
@pytest.mark.parametrize(
    "descriptor, notes",
    [
        ({"name": "package"}, []),
        ({}, ["'name' is a required property"]),
    ],
)
def test_package_profile_remote_ref_resolved_by_frictionless(
    descriptor, notes, tmp_path, mocker, requests_mock
):
    # jsonschema's own retrieval must not be used (nor hit the network)
    mocker.patch("urllib.request.urlopen", side_effect=AssertionError)
    remote = "https://example.com/profiles/remote.json"
    requests_mock.get(remote, json={"required": ["name"]})
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"allOf": [{"$ref": remote}]}))
    resource = Resource(name="table", path="data/table.csv")
    descriptor = {**descriptor, "resources": [resource.to_descriptor()]}
    with system.use_context(trusted=True):
        report = Package.validate_descriptor({**descriptor, "profile": str(profile)})
    assert [error.note for error in report.errors] == notes


# A remote "$ref" shared by several resources is downloaded only once
# during the validation of a package
def test_package_profile_remote_ref_retrieved_once(tmp_path, requests_mock):
    remote = "https://example.com/profiles/remote.json"
    requests_mock.get(remote, json={"required": ["name"]})
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"allOf": [{"$ref": remote}]}))
    resources = [
        {"name": name, "path": "data/table.csv", "profile": str(profile)}
        for name in ["table1", "table2", "table3"]
    ]
    with system.use_context(trusted=True):
        report = Package.validate_descriptor({"resources": resources})
    assert report.valid
    assert requests_mock.call_count == 1


# A local "$ref" is subject to the same safety rules as the profile path:
# an untrusted profile cannot read an arbitrary file of the server
@pytest.mark.parametrize(
    "ref, trusted, read",
    [
        ("secret.json", False, True),
        ("{secret}", False, False),
        ("../outside/secret.json", False, False),
        ("{secret}", True, True),
    ],
)
def test_package_profile_local_ref_safety(ref, trusted, read, tmp_path, monkeypatch):
    workdir = tmp_path / "workdir"
    outside = tmp_path / "outside"
    workdir.mkdir()
    outside.mkdir()
    secret = {"required": ["secret"]}
    (workdir / "secret.json").write_text(json.dumps(secret))
    (outside / "secret.json").write_text(json.dumps(secret))
    ref = ref.format(secret=outside / "secret.json")
    (workdir / "profile.json").write_text(json.dumps({"allOf": [{"$ref": ref}]}))
    monkeypatch.chdir(workdir)
    descriptor = {
        "profile": "profile.json",
        "resources": [{"name": "table", "data": [["id"], [1]]}],
    }
    with system.use_context(trusted=trusted):
        report = Package.validate_descriptor(descriptor)
    notes = [error.note for error in report.errors]
    if read:
        assert notes == ["'secret' is a required property"]
    else:
        assert len(notes) == 1
        assert '"$ref" path is not safe' in notes[0]
        # the server's directories are not disclosed
        assert str(tmp_path) not in notes[0]


# A relative "$ref" is resolved against the location of the profile
# (JSON Schema base URI), not against the current working directory
@pytest.mark.parametrize(
    "profile, ref, required",
    [
        ("profiles/profile.json", "target.json", "sibling"),
        ("profiles/profile.json", "../target.json", "cwd"),
        ("https://example.com/profiles/profile.json", "target.json", "sibling"),
    ],
)
def test_package_profile_relative_ref_resolved_from_profile(
    profile, ref, required, tmp_path, monkeypatch, requests_mock
):
    profile_descriptor = {"allOf": [{"$ref": ref}]}
    (tmp_path / "profiles").mkdir()
    (tmp_path / "profiles" / "profile.json").write_text(json.dumps(profile_descriptor))
    (tmp_path / "profiles" / "target.json").write_text('{"required": ["sibling"]}')
    (tmp_path / "target.json").write_text('{"required": ["cwd"]}')
    requests_mock.get(
        "https://example.com/profiles/profile.json", json=profile_descriptor
    )
    requests_mock.get(
        "https://example.com/profiles/target.json", json={"required": ["sibling"]}
    )
    monkeypatch.chdir(tmp_path)
    descriptor = {
        "profile": profile,
        "resources": [{"name": "table", "data": [["id"], [1]]}],
    }
    report = Package.validate_descriptor(descriptor)
    assert [error.note for error in report.errors] == [
        f"'{required}' is a required property"
    ]


# When untrusted, a remote profile cannot reach a local file, even a safe one
# with a known location; and only http(s) and local "$ref"s are supported
@pytest.mark.parametrize(
    "profile, ref, reason",
    [
        (
            "https://example.com/profiles/profile.json",
            "{secret_uri}",
            '"$ref" path is not safe',
        ),
        (
            "profile.json",
            "ftp://example.com/target.json",
            '"$ref" scheme "ftp" is not supported',
        ),
        (
            "profile.json",
            'data:application/json,{"required":["x"]}',
            '"$ref" scheme "data" is not supported',
        ),
    ],
)
def test_package_profile_ref_unsafe_or_unsupported(
    profile, ref, reason, tmp_path, monkeypatch, requests_mock
):
    (tmp_path / "secret.json").write_text('{"required": ["secret"]}')
    ref = ref.replace("{secret_uri}", (tmp_path / "secret.json").as_uri())
    profile_descriptor = {"allOf": [{"$ref": ref}]}
    (tmp_path / "profile.json").write_text(json.dumps(profile_descriptor))
    requests_mock.get(
        "https://example.com/profiles/profile.json", json=profile_descriptor
    )
    monkeypatch.chdir(tmp_path)
    descriptor = {
        "profile": profile,
        "resources": [{"name": "table", "data": [["id"], [1]]}],
    }
    report = Package.validate_descriptor(descriptor)
    notes = [error.note for error in report.errors]
    assert len(notes) == 1
    assert reason in notes[0]


# A remote profile or "$ref" is retrieved with the same timeout as remote data,
# so that an unresponsive server cannot block the validation forever
@pytest.mark.parametrize(
    "profile",
    [
        "https://example.com/profiles/profile.json",
        "profile.json",
    ],
)
def test_package_profile_remote_retrieval_timeout(
    profile, tmp_path, monkeypatch, requests_mock
):
    remote_ref = {"allOf": [{"$ref": "https://example.com/profiles/target.json"}]}
    (tmp_path / "profile.json").write_text(json.dumps(remote_ref))
    requests_mock.get("https://example.com/profiles/profile.json", json=remote_ref)
    requests_mock.get("https://example.com/profiles/target.json", json={})
    monkeypatch.chdir(tmp_path)
    descriptor = {
        "profile": profile,
        "resources": [{"name": "table", "data": [["id"], [1]]}],
    }
    report = Package.validate_descriptor(descriptor)
    assert report.valid
    assert requests_mock.request_history
    assert [request.timeout for request in requests_mock.request_history] == [
        10 for _ in requests_mock.request_history
    ]


@pytest.mark.skip
@pytest.mark.parametrize("profile", ["data-package", "tabular-data-package"])
def test_package_profile_type(profile):
    descriptor = {
        "resources": [{"name": "table", "path": "data/table.csv"}],
        "profile": profile,
    }
    package = Package.from_descriptor(descriptor)
    descriptor = package.to_descriptor()
    assert descriptor.get("profile") is None


# Legacy


@pytest.mark.vcr
@pytest.mark.skipif(sys.version_info < (3, 10), reason="pytest-vcr bug in Python3.8/9")
def test_package_profiles_from_descriptor_standards_v1():
    profile = "data/profiles/camtrap.json"
    resource = Resource(name="table", path="data/table.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Package({"resources": [resource.to_descriptor()], "profile": profile})
    reasons = excinfo.value.reasons
    assert len(reasons) == 5
    for error in reasons:
        assert "required" in error.message


@pytest.mark.skip
@pytest.mark.vcr
def test_package_profiles_to_descriptor_standards_v1():
    profile = "data/profiles/empty.json"
    descriptor = {
        "resources": [{"name": "table", "path": "data/table.csv"}],
        "profiles": [profile],
    }
    package = Package.from_descriptor(descriptor)
    with system.use_context(standards="v1"):
        descriptor = package.to_descriptor()
        assert descriptor["profile"] == profile


# Bugs


def test_package_preserver_profile_issue_1480():
    descriptor = yaml.safe_load("""
    profile: tabular-data-package
    resources:
      -
        name: some-table
        profile: tabular-data-resource
        path: some-file.csv
        format: csv
        mediatype: text/csv
        encoding: utf-8
        schema: schema.json
    """)
    package = Package(descriptor)
    assert package.profile == "tabular-data-package"
    assert package.get_resource("some-table").profile == "tabular-data-resource"


def test_package_profile_tabular_requirements_issue_1484():
    descriptor = yaml.safe_load("""
    profile: tabular-data-package
    resources:
      -
        name: some-table
        path: some-file.csv
        format: csv
        mediatype: text/csv
        encoding: utf-8
        schema: schema.json
    """)
    report = Package.validate_descriptor(descriptor)
    assert report.flatten(["type", "note"]) == [
        [
            "package-error",
            'profile "tabular-data-package" requires all the resources to be "tabular-data-resource"',
        ]
    ]


def test_package_profile_tabular_requirements_schema_issue_1484():
    descriptor = yaml.safe_load("""
    profile: tabular-data-package
    resources:
      -
        name: some-table
        profile: tabular-data-resource
        path: some-file.csv
        format: csv
        mediatype: text/csv
        encoding: utf-8
    """)
    report = Package.validate_descriptor(descriptor)
    assert report.flatten(["type", "note"]) == [
        [
            "resource-error",
            'profile "tabular-data-resource" requires "schema" to be present',
        ]
    ]
