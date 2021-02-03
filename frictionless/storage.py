# NOTE:
# We might need to reconsider the whole storage concept as it doesn't play nice
# with the well-established and working good loader/parser concepts
# At least, we need to reverse BigQuery/CKAN/SQL logic where the storage
# depends on the parser although it should be the opposite (rework it)


class Storage:
    """Storage representation"""

    def __init__(self, **options):
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
