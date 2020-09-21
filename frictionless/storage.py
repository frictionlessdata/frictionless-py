class Storage:
    def __init__(self, **options):
        pass

    # Read

    def read_resource(self, name, **options):
        pass

    def read_package(self, **options):
        pass

    # Write

    def write_resource(self, resource, *, force=False, **options):
        pass

    def write_package(self, package, *, force=False, **options):
        pass

    # Delete

    def delete_resource(self, name, *, ignore=False, **options):
        pass

    def delete_package(self, names, *, ignore=False, **options):
        pass
