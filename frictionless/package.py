import json
import zipfile
import tempfile
from pathlib import Path
from copy import deepcopy
from .exception import FrictionlessException
from .metadata import Metadata
from .resource import Resource
from .system import system
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
        resources? (dict|Resource[]): list of resource descriptors
        name? (str): package name (for machines)
        id? (str): package id (for machines)
        licenses? (dict[]): package licenses
        profile? (str): profile name like 'data-package'
        title? (str): package title (for humans)
        description? (str): package description
        homepage? (str): package homepage
        version? (str): package version
        sources? (dict[]): package sources
        contributors? (dict[]): package contributors
        keywords? (str[]): package keywords
        image? (str): package image
        created? (str): package created
        hashing? (str): a hashing algorithm for resources
        basepath? (str): a basepath of the package
        onerror? (ignore|warn|raise): behaviour if there is an error
        trusted? (bool): don't raise an exception on unsafe paths

    Raises:
        FrictionlessException: raise any error that occurs during the process
    """

    def __init__(
        self,
        source=None,
        *,
        descriptor=None,
        # Required
        resources=None,
        # Recommended
        name=None,
        id=None,
        licenses=None,
        profile=None,
        # Optional
        title=None,
        description=None,
        homepage=None,
        version=None,
        sources=None,
        contributors=None,
        keywords=None,
        image=None,
        created=None,
        # Extra
        hashing=None,
        basepath="",
        onerror="ignore",
        trusted=False,
    ):

        # Handle source
        if source is not None:
            if descriptor is None:
                descriptor = source
                file = system.create_file(source, basepath=basepath)
                if file.multipart:
                    descriptor = {"resources": []}
                    for part in file.normpath:
                        descriptor["resources"].append({"path": part})
                elif file.type == "table" and not file.compression:
                    descriptor = {"resources": [{"path": file.normpath}]}

        # Handle pathlib
        if isinstance(descriptor, Path):
            descriptor = str(descriptor)

        # Handle zip
        if helpers.is_zip_descriptor(descriptor):
            descriptor = helpers.unzip_descriptor(descriptor, "datapackage.json")

        # Set attributes
        self.setinitial("resources", resources)
        self.setinitial("name", name)
        self.setinitial("id", id)
        self.setinitial("licenses", licenses)
        self.setinitial("profile", profile)
        self.setinitial("title", title)
        self.setinitial("description", description)
        self.setinitial("homepage", homepage)
        self.setinitial("version", version)
        self.setinitial("sources", sources)
        self.setinitial("contributors", contributors)
        self.setinitial("keywords", keywords)
        self.setinitial("image", image)
        self.setinitial("created", created)
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
    def id(self):
        """
        Returns:
            str?: package id
        """
        return self.get("id")

    @Metadata.property
    def licenses(self):
        """
        Returns:
            dict?: package licenses
        """
        return self.get("licenses")

    @Metadata.property
    def profile(self):
        """
        Returns:
            str: package profile
        """
        return self.get("profile", config.DEFAULT_PACKAGE_PROFILE)

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
    def homepage(self):
        """
        Returns:
            str?: package homepage
        """
        return self.get("homepage")

    @Metadata.property
    def version(self):
        """
        Returns:
            str?: package version
        """
        return self.get("version")

    @Metadata.property
    def sources(self):
        """
        Returns:
            dict[]?: package sources
        """
        return self.get("sources")

    @Metadata.property
    def contributors(self):
        """
        Returns:
            dict[]?: package contributors
        """
        return self.get("contributors")

    @Metadata.property
    def keywords(self):
        """
        Returns:
            str[]?: package keywords
        """
        return self.get("keywords")

    @Metadata.property
    def image(self):
        """
        Returns:
            str?: package image
        """
        return self.get("image")

    @Metadata.property
    def created(self):
        """
        Returns:
            str?: package created
        """
        return self.get("created")

    @Metadata.property(cache=False, write=False)
    def hashing(self):
        """
        Returns:
            str: package hashing
        """
        return self.__hashing

    @Metadata.property(cache=False, write=False)
    def basepath(self):
        """
        Returns:
            str: package basepath
        """
        return self.__basepath

    @Metadata.property(cache=False, write=False)
    def onerror(self):
        """
        Returns:
            ignore|warn|raise: on error bahaviour
        """
        return self.__onerror

    @Metadata.property(cache=False, write=False)
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

    @Metadata.property(cache=False, write=False)
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
        raise FrictionlessException(error)

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

    def infer(self, *, stats=False):
        """Infer package's attributes

        Parameters:
            stats? (bool): stream files completely and infer stats
        """

        # General
        self.setdefault("profile", config.DEFAULT_PACKAGE_PROFILE)
        for resource in self.resources:
            resource.infer(stats=stats)

        # Deduplicate names
        if len(self.resource_names) != len(set(self.resource_names)):
            seen_names = []
            for index, name in enumerate(self.resource_names):
                count = seen_names.count(name) + 1
                if count > 1:
                    self.resources[index].name = "%s%s" % (name, count)
                seen_names.append(name)

    # Import/Export

    @staticmethod
    def from_zip(path, **options):
        """Create a package from ZIP"""
        return Package(descriptor=path, **options)

    @staticmethod
    def from_storage(storage):
        """Import package from storage

        Parameters:
            storage (Storage): storage instance
        """
        return storage.read_package()

    @staticmethod
    def from_ckan(*, url, dataset, apikey=None):
        """Import package from CKAN

        Parameters:
            url (string): CKAN instance url e.g. "https://demo.ckan.org"
            dataset (string): dataset id in CKAN e.g. "my-dataset"
            apikey? (str): API key for CKAN e.g. "51912f57-a657-4caa-b2a7-0a1c16821f4b"
        """
        return Package.from_storage(
            system.create_storage(
                "ckan",
                url=url,
                dataset=dataset,
                apikey=apikey,
            )
        )

    @staticmethod
    def from_sql(*, url=None, engine=None, prefix="", namespace=None):
        """Import package from SQL

        Parameters:
            url? (string): SQL connection string
            engine? (object): `sqlalchemy` engine
            prefix? (str): prefix for all tables
            namespace? (str): SQL scheme
        """
        return Package.from_storage(
            system.create_storage(
                "sql", url=url, engine=engine, prefix=prefix, namespace=namespace
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

    # TODO: support multipart
    def to_zip(self, path, *, resolve=[], encoder_class=None):
        """Save package to a zip

        Parameters:
            path (str): target path
            resolve (str[]): Data sources to resolve.
                For "memory" data it means saving them as CSV and including into ZIP.
                For "remote" data it means downloading them and including into ZIP.
                For example, `resolve=["memory", "remote"]`
            encoder_class (object): json encoder class

        Raises:
            FrictionlessException: on any error
        """
        try:
            with zipfile.ZipFile(path, "w") as zip:
                package_descriptor = self.to_dict()
                for index, resource in enumerate(self.resources):
                    descriptor = package_descriptor["resources"][index]

                    # Multipart data
                    if resource.multipart:
                        note = "Zipping multipart resource is not yet supported"
                        raise FrictionlessException(errors.ResourceError(note=note))

                    # Memory data
                    elif resource.memory:
                        if "memory" in resolve:
                            path = f"{resource.name}.csv"
                            descriptor["path"] = path
                            del descriptor["data"]
                            with tempfile.NamedTemporaryFile() as file:
                                tgt = Resource(path=file.name, format="csv", trusted=True)
                                resource.write(tgt)
                                zip.write(file.name, path)
                        elif not isinstance(resource.data, list):
                            note = f"Use resolve argument to zip {resource.data}"
                            raise FrictionlessException(errors.ResourceError(note=note))

                    # Remote data
                    elif resource.remote:
                        if "remote" in resolve:
                            path = f"{resource.name}.{resource.format}"
                            descriptor["path"] = path
                            with tempfile.NamedTemporaryFile() as file:
                                # TODO: rebase on resource here?
                                with system.create_loader(resource) as loader:
                                    while True:
                                        chunk = loader.byte_stream.read(1024)
                                        if not chunk:
                                            break
                                        file.write(chunk)
                                    file.flush()
                                zip.write(file.name, path)

                    # Local Data
                    else:
                        path = resource.path
                        if not helpers.is_safe_path(path):
                            path = f"{resource.name}.{resource.format}"
                            descriptor["path"] = path
                        zip.write(resource.fullpath, path)

                # Metadata
                zip.writestr(
                    "datapackage.json",
                    json.dumps(
                        package_descriptor,
                        indent=2,
                        ensure_ascii=False,
                        cls=encoder_class,
                    ),
                )

        except Exception as exception:
            error = errors.PackageError(note=str(exception))
            raise FrictionlessException(error) from exception

    def to_storage(self, storage, *, force=False):
        """Export package to storage

        Parameters:
            storage (Storage): storage instance
            force (bool): overwrite existent
        """
        storage.write_package(self.to_copy(), force=force)
        return storage

    def to_ckan(self, *, url, dataset, apikey=None, force=False):
        """Export package to CKAN

        Parameters:
            url (string): CKAN instance url e.g. "https://demo.ckan.org"
            dataset (string): dataset id in CKAN e.g. "my-dataset"
            apikey? (str): API key for CKAN e.g. "51912f57-a657-4caa-b2a7-0a1c16821f4b"
            force (bool): (optional) overwrite existing data
        """
        return self.to_storage(
            system.create_storage(
                "ckan",
                url=url,
                dataset=dataset,
                apikey=apikey,
            ),
            force=force,
        )

    def to_sql(self, *, url=None, engine=None, prefix="", namespace=None, force=False):
        """Export package to SQL

        Parameters:
            url? (string): SQL connection string
            engine? (object): `sqlalchemy` engine
            prefix? (str): prefix for all tables
            namespace? (str): SQL scheme
            force (bool): overwrite existent
        """
        return self.to_storage(
            system.create_storage(
                "sql", url=url, engine=engine, prefix=prefix, namespace=namespace
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
