# NOTE:
# We might consider reducing this API to something like
# Storage.read/write_package although I have already made
# a few attempts using parser.write_row_stream to achieve this goal
# and this doesn't seem to work as storage.write_package needs to
# handle transactions and relation order in e.g. SQL plugin.
# So, as for now, we will continue to call Storage API
# from Parser API for plugin where there is a storage.


class Storage:
    def __init__(self, source, **options):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    # Read

    def read_resource(self, name, **options):
        raise NotImplementedError()

    def read_package(self, **options):
        raise NotImplementedError()

    # Write

    def write_resource(self, resource, *, force=False, **options):
        raise NotImplementedError()

    def write_package(self, package, *, force=False, **options):
        raise NotImplementedError()

    # Delete

    def delete_resource(self, name, *, ignore=False, **options):
        raise NotImplementedError()

    def delete_package(self, names, *, ignore=False, **options):
        raise NotImplementedError()
