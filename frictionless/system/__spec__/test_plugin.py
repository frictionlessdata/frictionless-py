from frictionless import Plugin, Resource, system


def test_matches_datatype_routes_to_resource_class():
    class FooResource(Resource):
        datatype = "foo"

    class FooPlugin(Plugin):
        def matches_datatype(self, resource):
            if resource.format == "foo":
                return "foo"

        def select_resource_class(self, type=None, *, datatype=None):
            if datatype == "foo":
                return FooResource

    system.register("foo", FooPlugin())
    try:
        resource = Resource(path="test.foo")
        assert isinstance(resource, FooResource)
        assert resource.datatype == "foo"
    finally:
        system.deregister("foo")


def test_detect_resource_applies_guarded_defaults():
    class BarPlugin(Plugin):
        def matches_datatype(self, resource):
            if resource.format == "bar":
                return "file"

        def detect_resource(self, resource):
            if resource.format == "bar":
                resource.mediatype = resource.mediatype or "application/bar"

    system.register("bar", BarPlugin())
    try:
        resource = Resource(path="test.bar")
        assert resource.mediatype == "application/bar"
        # Resource with a different format must not receive the default
        other = Resource(path="test.csv")
        assert other.mediatype != "application/bar"
    finally:
        system.deregister("bar")


def test_detect_resource_can_set_scheme():
    class BazPlugin(Plugin):
        def detect_resource(self, resource):
            if resource.path and resource.path.endswith(".baz"):
                resource.scheme = "baz"

    system.register("baz", BazPlugin())
    try:
        resource = Resource(path="test.baz")
        assert resource.scheme == "baz"
    finally:
        system.deregister("baz")
