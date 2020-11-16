import os
import json
import glob
import zipfile
from copy import deepcopy
from .metadata import Metadata
from .resource import Resource
from .system import system
from . import exceptions
from . import helpers
from . import errors
from . import config


class Package(Metadata):
    """Package representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Package`

    ```python
    package = Package(resources=[Resource(path="data/table.csv")])
    package.get_resoure('table').read_rows() == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]
    ```

    Parameters:
        descriptor? (str|dict): package descriptor
        name? (str): package name (for machines)
        title? (str): package title (for humans)
        description? (str): package description
        profile? (str): profile name like 'data-package'
        resources? (dict|Resource[]): list of resource descriptors
        hashing? (str): a hashing algorithm for resources
        basepath? (str): a basepath of the package
        onerror? (ignore|warn|raise): behaviour if there is an error
        trusted? (bool): don't raise an exception on unsafe paths

    Raises:
        FrictionlessException: raise any error that occurs during the process
    """

    def __init__(
        self,
        descriptor=None,
        *,
        name=None,
        title=None,
        description=None,
        profile=None,
        resources=None,
        hashing=None,
        basepath=None,
        onerror="ignore",
        trusted=False,
    ):

        # Handle zip
        if helpers.is_zip_descriptor(descriptor):
            descriptor = helpers.unzip_descriptor(descriptor, "datapackage.json")

        # Set attributes
        self.setinitial("name", name)
        self.setinitial("title", title)
        self.setinitial("description", description)
        self.setinitial("profile", profile)
        self.setinitial("resources", resources)
        self.__hashing = hashing
        self.__basepath = basepath or helpers.detect_basepath(descriptor)
        self.__onerror = onerror
        self.__trusted = trusted
        super().__init__(descriptor)

    def __setattr__(self, name, value):
        if name == "hashing":
            self.__hashing = value
        elif name == "basepath":
            self.__basepath = value
        elif name == "onerror":
            self.__onerror = value
        elif name == "trusted":
            self.__trusted = value
        else:
            return super().__setattr__(name, value)
        self.metadata_process()

    @Metadata.property
    def name(self):
        """
        Returns:
            str?: package name
        """
        return self.get("name")

    @Metadata.property
    def title(self):
        """
        Returns:
            str?: package title
        """
        return self.get("title")

    @Metadata.property
    def description(self):
        """
        Returns:
            str?: package description
        """
        return self.get("description")

    @Metadata.property
    def profile(self):
        """
        Returns:
            str: package profile
        """
        return self.get("profile", config.DEFAULT_PACKAGE_PROFILE)

    @Metadata.property(write=False)
    def hashing(self):
        """
        Returns:
            str: package hashing
        """
        return self.__hashing

    @Metadata.property(write=False)
    def basepath(self):
        """
        Returns:
            str: package basepath
        """
        return self.__basepath

    @property
    def onerror(self):
        """
        Returns:
            ignore|warn|raise: on error bahaviour
        """
        assert self.__onerror in ["ignore", "warn", "raise"]
        return self.__onerror

    @Metadata.property(write=False)
    def trusted(self):
        """
        Returns:
            str: package trusted
        """
        return self.__trusted

    # Resources

    @Metadata.property
    def resources(self):
        """
        Returns:
            Resources[]: package resource
        """
        resources = self.get("resources", [])
        return self.metadata_attach("resources", resources)

    @Metadata.property(write=False)
    def resource_names(self):
        """
        Returns:
            str[]: package resource names
        """
        return [resource.name for resource in self.resources]

    def add_resource(self, descriptor):
        """Add new resource to package.

        Parameters:
            descriptor (dict): resource descriptor

        Returns:
            Resource/None: added `Resource` instance or `None` if not added
        """
        self.setdefault("resources", [])
        self["resources"].append(descriptor)
        return self.resources[-1]

    def get_resource(self, name):
        """Get resource by name.

        Parameters:
            name (str): resource name

        Raises:
            FrictionlessException: if resource is not found

        Returns:
           Resource/None: `Resource` instance or `None` if not found
        """
        for resource in self.resources:
            if resource.name == name:
                return resource
        error = errors.PackageError(note=f'resource "{name}" does not exist')
        raise exceptions.FrictionlessException(error)

    def has_resource(self, name):
        """Check if a resource is present

        Parameters:
            name (str): schema resource name

        Returns:
           bool: whether there is the resource
        """
        for resource in self.resources:
            if resource.name == name:
                return True
        return False

    def remove_resource(self, name):
        """Remove resource by name.

        Parameters:
            name (str): resource name

        Raises:
            FrictionlessException: if resource is not found

        Returns:
            Resource/None: removed `Resource` instances or `None` if not found
        """
        resource = self.get_resource(name)
        self.resources.remove(resource)
        return resource

    # Expand

    def expand(self):
        """Expand metadata

        It will add default values to the package.
        """
        self.setdefault("resources", [])
        self.setdefault("profile", config.DEFAULT_PACKAGE_PROFILE)
        for resource in self.resources:
            resource.expand()

    # Infer

    # TODO: use stats=True instead of only_sample?
    def infer(self, source=None, *, only_sample=False):
        """Infer package's attributes

        Parameters:
            source (str|str[]): path, list of paths or glob pattern
            only_sample? (bool): infer whatever possible but only from the sample
        """
        self.setdefault("profile", config.DEFAULT_PACKAGE_PROFILE)

        # From source
        if source:
            self.resources.clear()
            if isinstance(source, str) and os.path.isdir(source):
                source = f"{source}/*"
            for pattern in source if isinstance(source, list) else [source]:
                options = {"recursive": True} if "**" in pattern else {}
                pattern = os.path.join(self.basepath, pattern)
                for path in sorted(glob.glob(pattern, **options)):
                    if path.endswith("package.json"):
                        continue
                    self.resources.append({"path": os.path.relpath(path, self.basepath)})

        # General
        for resource in self.resources:
            resource.infer(only_sample=only_sample)

    # Import/Export

    @staticmethod
    def from_storage(storage):
        """Import package from storage

        Parameters:
            storage (Storage): storage instance
        """
        return storage.read_package()

    @staticmethod
    def from_ckan(*, base_url, dataset_id, api_key=None):
        """Import package from CKAN

        Parameters:
            base_url (str): (required) URL for CKAN instance (e.g: https://demo.ckan.org/ )
            dataset_id (str): (required) ID or slug of dataset to fetch
            api_key (str): (optional) Your CKAN API key
        """
        return Package.from_storage(
            system.create_storage(
                "ckan_datastore",
                base_url=base_url,
                dataset_id=dataset_id,
                api_key=api_key,
            )
        )

    @staticmethod
    def from_sql(*, engine, prefix="", namespace=None):
        """Import package from SQL

        Parameters:
            engine (object): `sqlalchemy` engine
            prefix (str): prefix for all tables
            namespace (str): SQL scheme
        """
        return Package.from_storage(
            system.create_storage(
                "sql", engine=engine, prefix=prefix, namespace=namespace
            )
        )

    @staticmethod
    def from_pandas(*, dataframes):
        """Import package from Pandas dataframes

        Parameters:
            dataframes (dict): mapping of Pandas dataframes
        """
        return Package.from_storage(
            system.create_storage("pandas", dataframes=dataframes)
        )

    @staticmethod
    def from_spss(*, basepath):
        """Import package from SPSS directory

        Parameters:
            basepath (str): SPSS dir path
        """
        return Package.from_storage(system.create_storage("spss", basepath=basepath))

    @staticmethod
    def from_bigquery(*, service, project, dataset, prefix=""):
        """Import package from Bigquery

        Parameters:
            service (object): BigQuery `Service` object
            project (str): BigQuery project name
            dataset (str): BigQuery dataset name
            prefix? (str): prefix for all names
        """
        return Package.from_storage(
            system.create_storage(
                "bigquery",
                service=service,
                project=project,
                dataset=dataset,
                prefix=prefix,
            ),
        )

    def to_copy(self):
        """Create a copy of the package"""
        descriptor = self.to_dict()
        # Resource's data can be not serializable (generators/functions)
        descriptor.pop("resources", None)
        resources = []
        for resource in self.resources:
            resources.append(resource.to_copy())
        return Package(
            descriptor,
            resources=resources,
            basepath=self.__basepath,
            onerror=self.__onerror,
            trusted=self.__trusted,
        )

    # NOTE: support multipart
    def to_zip(self, target, encoder_class=None):
        """Save package to a zip

        Parameters:
            target (str): target path

        Raises:
            FrictionlessException: on any error
        """
        try:
            with zipfile.ZipFile(target, "w") as zip:
                descriptor = self.copy()
                for resource in self.resources:
                    if resource.inline:
                        continue
                    if resource.remote:
                        continue
                    if resource.multipart:
                        continue
                    if not helpers.is_safe_path(resource.path):
                        continue
                    zip.write(resource.source, resource.path)
                descriptor = json.dumps(
                    descriptor, indent=2, ensure_ascii=False, cls=encoder_class
                )
                zip.writestr("datapackage.json", descriptor)
        except Exception as exception:
            error = errors.PackageError(note=str(exception))
            raise exceptions.FrictionlessException(error) from exception

    def to_storage(self, storage, *, force=False):
        """Export package to storage

        Parameters:
            storage (Storage): storage instance
            force (bool): overwrite existent
        """
        storage.write_package(self.to_copy(), force=force)
        return storage

    def to_ckan(self, *, base_url, dataset_id=None, api_key=None, force=False):
        """Export package to CKAN

        Parameters:
            base_url (str): (required) URL for CKAN instance (e.g: https://demo.ckan.org/ )
            dataset_id (str): (optional) ID or slug of dataset this resource belongs to
            api_key (str): (optional) Your CKAN API key
            force (bool): (optional) overwrite existing data
        """
        return self.to_storage(
            system.create_storage(
                "ckan_datastore",
                base_url=base_url,
                dataset_id=dataset_id,
                api_key=api_key,
            ),
            force=force,
        )

    def to_sql(self, *, engine, prefix="", namespace=None, force=False):
        """Export package to SQL

        Parameters:
            engine (object): `sqlalchemy` engine
            prefix (str): prefix for all tables
            namespace (str): SQL scheme
            force (bool): overwrite existent
        """
        return self.to_storage(
            system.create_storage(
                "sql", engine=engine, prefix=prefix, namespace=namespace
            ),
            force=force,
        )

    def to_pandas(self):
        """Export package to Pandas dataframes"""
        return self.to_storage(system.create_storage("pandas"))

    def to_spss(self, *, basepath, force=False):
        """Export package to SPSS directory

        Parameters:
            basepath (str): SPSS dir path
            force (bool): overwrite existent
        """
        return self.to_storage(
            system.create_storage("spss", basepath=basepath), force=force
        )

    def to_bigquery(self, *, service, project, dataset, prefix="", force=False):
        """Export package to Bigquery

        Parameters:
            service (object): BigQuery `Service` object
            project (str): BigQuery project name
            dataset (str): BigQuery dataset name
            prefix? (str): prefix for all names
            force (bool): overwrite existent
        """
        return self.to_storage(
            system.create_storage(
                "bigquery",
                service=service,
                project=project,
                dataset=dataset,
                prefix=prefix,
            ),
            force=force,
        )

    # Metadata

    metadata_duplicate = True
    metadata_Error = errors.PackageError  # type: ignore
    metadata_profile = deepcopy(config.PACKAGE_PROFILE)
    metadata_profile["properties"]["resources"] = {
        "type": "array",
        "items": {"type": "object"},
    }

    def metadata_process(self):

        # Resources
        resources = self.get("resources")
        if isinstance(resources, list):
            for index, resource in enumerate(resources):
                if not isinstance(resource, Resource):
                    if not isinstance(resource, dict):
                        resource = {"name": f"resource{index+1}"}
                    resource = Resource(
                        resource,
                        hashing=self.__hashing,
                        basepath=self.__basepath,
                    )
                    list.__setitem__(resources, index, resource)
                resource.onerror = self.__onerror
                resource.trusted = self.__trusted
                resource.package = self
            if not isinstance(resources, helpers.ControlledList):
                resources = helpers.ControlledList(resources)
                resources.__onchange__(self.metadata_process)
                dict.__setitem__(self, "resources", resources)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Extensions
        if self.profile == "fiscal-data-package":
            yield from super().metadata_validate(config.FISCAL_PACKAGE_PROFILE)

        # Resources
        for resource in self.resources:
            yield from resource.metadata_errors
