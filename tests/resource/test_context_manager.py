import pytest

from frictionless import FrictionlessException, Resource

# Test that the context manager implementation works correctly

# As per PEP-343, the context manager should be a single-use object (like files)
# See https://peps.python.org/pep-0343/#caching-context-managers


def test_context_manager_opens_resource():
    with Resource("data/table.csv") as resource:
        assert resource.closed is False


def test_context_manager_closes_resource():
    with Resource("data/table.csv") as resource:
        pass
    assert resource.closed is True


def test_context_manager_returns_same_resource():
    resource = Resource("data/table.csv")
    with resource as context_manager_return_value:
        assert resource == context_manager_return_value


def test_nested_context_causes_exception():
    with pytest.raises(FrictionlessException):
        # Create nested with statements to test that we can't open
        # the same resource twice via context managers
        with Resource("data/table.csv") as resource:
            with resource:
                pass


def test_resource_copy_can_use_nested_context():
    # Create nested with statements to test that we can still open
    # the same resource twice via context if we copy the resource
    # before the second `with`
    with Resource("data/table.csv") as resource:
        copy = resource.to_copy()
        with copy:
            assert copy.closed is False
            assert resource.closed is False

        # Check that the original resource is still open
        assert copy.closed is True
        assert resource.closed is False


def test_resource_can_use_repeated_non_nested_contexts():
    # Repeat context allowed
    resource = Resource("data/table.csv")
    with resource:
        assert resource.closed is False

    assert resource.closed is True

    with resource:
        assert resource.closed is False
    assert resource.closed is True


def test_resource_copy_can_use_repeated_context():
    # Repeated context with a copy is allowed
    resource = Resource("data/table.csv")
    copy = resource.to_copy()
    with resource:
        assert resource.closed is False
        assert copy.closed is True

    with copy:
        assert resource.closed is True
        assert copy.closed is False


def test_context_manager_on_open_resource_throw_exception():
    """
    Using the Resource in a `with` statement after it has been opened will unexpectedly close the resource
    at the end of the context.  So this is prevented by throwing an exception.
    """
    resource = Resource("data/table.csv")
    resource.open()
    assert resource.closed is False
    with pytest.raises(FrictionlessException):
        with resource:
            pass


def test_explicit_open_can_be_repeated():
    # Explicit open can be nested
    # Note that the first close() call will close the resource, so anyone
    # using explicit open() calls must be aware of that.
    resource = Resource("data/table.csv")
    resource.open()
    assert resource.closed is False
    resource.open()
    assert resource.closed is False
    resource.close()
    assert resource.closed is True
    resource.close()
    assert resource.closed is True
