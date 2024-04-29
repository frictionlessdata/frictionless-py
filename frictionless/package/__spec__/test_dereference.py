from frictionless import Package


def test_package_dereference_forced():
    package = Package.from_descriptor("data/package-with-dereferencing.json")
    package.dereference()
    descriptor = package.to_descriptor()
    assert isinstance(descriptor["resources"][0]["dialect"], dict)
    assert isinstance(descriptor["resources"][0]["schema"], dict)
