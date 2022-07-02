from __future__ import annotations
import os
import json
import jinja2
import zipfile
import tempfile
import builtins
from copy import deepcopy
from collections import Mapping
from multiprocessing import Pool
from typing import TYPE_CHECKING, Optional, List, Any
from ..exception import FrictionlessException
from ..helpers import get_name
from ..pipeline import Pipeline
from ..checklist import Checklist
from ..metadata import Metadata
from ..detector import Detector
from ..resource import Resource
from ..dialect import Dialect
from ..report import Report
from ..schema import Field
from ..system import system
from .. import settings
from .. import helpers
from .. import errors

if TYPE_CHECKING:
    from ..interfaces import IDescriptor, IOnerror, FilterFunction, ProcessFunction


# TODO: add create_package hook
class Package(Metadata):
    """Package representation

    This class is one of the cornerstones of of Frictionless framework.
    It manages underlaying resource and provides an ability to describe a package.

    ```python
    package = Package(resources=[Resource(path="data/table.csv")])
    package.get_resoure('table').read_rows() == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]
    ```

    """

    def __init__(
        self,
        source: Optional[Any] = None,
        *,
        # Standard
        resources: List[Resource] = [],
        id: Optional[str] = None,
        name: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        licenses: List[dict] = [],
        sources: List[dict] = [],
        profile: str = settings.DEFAULT_PACKAGE_PROFILE,
        homepage: Optional[str] = None,
        version: Optional[str] = None,
        contributors: List[dict] = [],
        keywords: List[str] = [],
        image: Optional[str] = None,
        created: Optional[str] = None,
        # Software
        innerpath: str = settings.DEFAULT_PACKAGE_INNERPATH,
        basepath: str = settings.DEFAULT_BASEPATH,
        onerror: IOnerror = settings.DEFAULT_ONERROR,
        trusted: bool = settings.DEFAULT_TRUSTED,
        detector: Optional[Detector] = None,
        dialect: Optional[Dialect] = None,
        hashing: Optional[str] = None,
    ):

        # Store state
        self.source = source
        self.resources = resources.copy()
        self.id = id
        self.name = name
        self.title = title
        self.description = description
        self.licenses = licenses.copy()
        self.sources = sources.copy()
        self.profile = profile
        self.homepage = homepage
        self.version = version
        self.contributors = contributors.copy()
        self.keywords = keywords.copy()
        self.image = image
        self.created = created
        self.innerpath = innerpath
        self.basepath = basepath
        self.onerror = onerror
        self.trusted = trusted
        self.detector = detector or Detector()
        self.dialect = dialect
        self.hashing = hashing

        # Finalize creation
        self.metadata_initiated = True
        self.detector.detect_package(self)
        system.create_package(self)

    @classmethod
    def __create__(
        cls,
        source: Optional[Any] = None,
        innerpath: str = settings.DEFAULT_PACKAGE_INNERPATH,
        trusted: bool = False,
        **options,
    ):
        if source:
            if helpers.is_zip_descriptor(source):
                source = helpers.unzip_descriptor(source, innerpath)
            return Package.from_descriptor(
                source, innerpath=innerpath, trusted=trusted, **options  # type: ignore
            )

    # State

    resources: List[Resource]
    """
    A list of resource descriptors.
    It can be dicts or Resource instances
    """

    id: Optional[str]
    """
    A property reserved for globally unique identifiers.
    Examples of identifiers that are unique include UUIDs and DOIs.
    """

    name: Optional[str]
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “.”, “_” or “-” characters.
    """

    title: Optional[str]
    """
    A Package title according to the specs
    It should a human-oriented title of the resource.
    """

    description: Optional[str]
    """
    A Package description according to the specs
    It should a human-oriented description of the resource.
    """

    licenses: List[dict]
    """
    The license(s) under which the package is provided.
    """

    sources: List[dict]
    """
    The raw sources for this data package.
    It MUST be an array of Source objects.
    Each Source object MUST have a title and
    MAY have path and/or email properties.
    """
    profile: str
    """
    A string identifying the profile of this descriptor.
    For example, `fiscal-data-package`.
    """

    homepage: Optional[str]
    """
    A URL for the home on the web that is related to this package.
    For example, github repository or ckan dataset address.
    """

    version: Optional[str]
    """
    A version string identifying the version of the package.
    It should conform to the Semantic Versioning requirements and
    should follow the Data Package Version pattern.
    """

    contributors: List[dict]
    """
    The people or organizations who contributed to this package.
    It MUST be an array. Each entry is a Contributor and MUST be an object.
    A Contributor MUST have a title property and MAY contain
    path, email, role and organization properties.
    """

    keywords: List[str]
    """
    An Array of string keywords to assist users searching.
    For example, ['data', 'fiscal']
    """

    image: Optional[str]
    """
    An image to use for this data package.
    For example, when showing the package in a listing.
    """

    created: Optional[str]
    """
    The datetime on which this was created.
    The datetime must conform to the string formats for RFC3339 datetime,
    """

    innerpath: str
    """
    A ZIP datapackage descriptor inner path.
    Path to the package descriptor inside the ZIP datapackage.
    Example: some/folder/datapackage.yaml
    Default: datapackage.json
    """

    basepath: str
    """
    A basepath of the resource
    The fullpath of the resource is joined `basepath` and /path`
    """

    onerror: IOnerror
    """
    Behaviour if there is an error.
    It defaults to 'ignore'. The default mode will ignore all errors
    on resource level and they should be handled by the user
    being available in Header and Row objects.
    """

    trusted: bool
    """
    Don't raise an exception on unsafe paths.
    A path provided as a part of the descriptor considered unsafe
    if there are path traversing or the path is absolute.
    A path provided as `source` or `path` is alway trusted.
    """

    detector: Detector
    """
    File/table detector.
    For more information, please check the Detector documentation.
    """

    dialect: Optional[Dialect]
    """
    Table dialect.
    For more information, please check the Dialect documentation.
    """

    hashing: Optional[str]
    """
    A hashing algorithm for resources
    It defaults to 'md5'.
    """

    # Props

    @property
    def description_html(self):
        """Package description in HTML"""
        return helpers.md_to_html(self.description)

    @property
    def description_text(self):
        """Package description in Text"""
        return helpers.html_to_text(self.description_html)

    def resource_names(self):
        """Return names of resources"""
        return [resource.name for resource in self.resources]

    # Describe

    @staticmethod
    def describe(source=None, *, stats=False, **options):
        """Describe the given source as a package

        Parameters:
            source (any): data source
            stats? (bool): if `True` infer resource's stats
            **options (dict): Package constructor options

        Returns:
            Package: data package

        """
        package = Package(source, **options)
        package.infer(stats=stats)
        return package

    # Extract

    def extract(
        self,
        *,
        filter: Optional[FilterFunction] = None,
        process: Optional[ProcessFunction] = None,
        stream: bool = False,
    ):
        """Extract package rows

        Parameters:
            filter? (bool): a row filter function
            process? (func): a row processor function
            stream? (bool): return a row streams instead of loading into memory

        Returns:
            {path: Row[]}: a dictionary of arrays/streams of rows

        """
        result = {}
        for number, resource in enumerate(package.resources, start=1):  # type: ignore
            key = resource.fullpath if not resource.memory else f"memory{number}"
            data = read_row_stream(resource)
            data = builtins.filter(filter, data) if filter else data
            data = (process(row) for row in data) if process else data
            result[key] = data if stream else list(data)
        return result

    # Validate

    def validate(
        self,
        checklist: Optional[Checklist] = None,
        *,
        original: bool = False,
        parallel: bool = False,
    ):
        """Validate package

        Parameters:
            checklist? (checklist): a Checklist object
            parallel? (bool): run in parallel if possible

        Returns:
            Report: validation report

        """

        # Create state
        timer = helpers.Timer()
        reports: List[Report] = []
        with_fks = any(resource.schema.foreign_keys for resource in package.resources)  # type: ignore

        # Prepare checklist
        checklist = checklist or Checklist()
        if not checklist.metadata_valid:
            errors = checklist.metadata_errors
            return Report.from_validation(time=timer.time, errors=errors)

        # Validate metadata
        metadata_errors = []
        for error in self.metadata_errors:
            if error.code == "package-error":
                metadata_errors.append(error)
        if metadata_errors:
            return Report.from_validation(time=timer.time, errors=metadata_errors)

        # Validate sequential
        if not parallel or with_fks:
            for resource in package.resources:  # type: ignore
                report = validate_sequential(resource, original=original)
                reports.append(report)

        # Validate parallel
        else:
            with Pool() as pool:
                resource_descriptors: List[dict] = []
                for resource in package.resources:  # type: ignore
                    descriptor = resource.to_dict()
                    descriptor["basepath"] = resource.basepath
                    descriptor["trusted"] = resource.trusted
                    descriptor["original"] = original
                    resource_descriptors.append(descriptor)
                report_descriptors = pool.map(validate_parallel, resource_descriptors)
                for report_descriptor in report_descriptors:
                    reports.append(Report.from_descriptor(report_descriptor))  # type: ignore

        # Return report
        return Report.from_validation_reports(
            time=timer.time,
            reports=reports,
        )

    # Transform

    # TODO: save transform info into package.stats?
    def transform(self, pipeline: Pipeline):
        """Transform package

        Parameters:
            source (any): data source
            steps (Step[]): transform steps
            **options (dict): Package constructor options

        Returns:
            Package: the transform result
        """

        # Prepare package
        self.infer()

        # Prepare pipeline
        if not pipeline.metadata_valid:
            raise FrictionlessException(pipeline.metadata_errors[0])

        # Run transforms
        for step in pipeline.steps:

            # Transform
            try:
                step.transform_package(self)
            except Exception as exception:
                error = errors.StepError(note=f'"{get_name(step)}" raises "{exception}"')
                raise FrictionlessException(error) from exception

        return self

    # Resources

    def add_resource(self, resource: Resource) -> None:
        """Add new resource to the package"""
        self.resources.append(resource)
        resource.package = self

    def has_resource(self, name: str) -> bool:
        """Check if a resource is present"""
        for resource in self.resources:
            if resource.name == name:
                return True
        return False

    def get_resource(self, name: str) -> Resource:
        """Get resource by name"""
        for resource in self.resources:
            if resource.name == name:
                return resource
        error = errors.PackageError(note=f'resource "{name}" does not exist')
        raise FrictionlessException(error)

    def set_resource(self, resource: Resource) -> Optional[Resource]:
        """Set resource by name"""
        assert resource.name
        if self.has_resource(resource.name):
            prev_resource = self.get_resource(resource.name)
            index = self.resources.index(prev_resource)
            self.resources[index] = resource
            resource.package = self
            return prev_resource
        self.add_resource(resource)

    def remove_resource(self, name: str) -> Resource:
        """Remove resource by name"""
        resource = self.get_resource(name)
        self.resources.remove(resource)
        return resource

    # Infer

    def infer(self, *, stats=False):
        """Infer package's attributes

        Parameters:
            stats? (bool): stream files completely and infer stats
        """

        # General
        self.setdefault("profile", settings.DEFAULT_PACKAGE_PROFILE)
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

    # Convert

    def to_copy(self):
        """Create a copy of the package"""
        return super().to_copy(
            resources=[resource.to_copy() for resource in self.resources],
            basepath=self.basepath,
            onerror=self.onerror,
            trusted=self.trusted,
            detector=self.detector,
            dialect=self.dialect,
            hashing=self.hashing,
        )

    @classmethod
    def from_descriptor(cls, descriptor, **options):
        if isinstance(descriptor, str):
            options["basepath"] = helpers.parse_basepath(descriptor)
        package = super().from_descriptor(descriptor, **options)

        # Resources
        for resource in package.resources:
            resource.package = package

        return package

    # TODO: if path is not provided return as a string
    def to_er_diagram(self, path=None) -> str:
        """Generate ERD(Entity Relationship Diagram) from package resources
        and exports it as .dot file

        Based on:
        - https://github.com/frictionlessdata/frictionless-py/issues/1118

        Parameters:
            path (str): target path

        Returns:
            path(str): location of the .dot file

        """

        # Render diagram
        template_dir = os.path.join(os.path.dirname(__file__), "../assets/templates/erd")
        environ = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            lstrip_blocks=True,
            trim_blocks=True,
        )
        table_template = environ.get_template("table.html")
        field_template = environ.get_template("field.html")
        primary_key_template = environ.get_template("primary_key_field.html")
        graph = environ.get_template("graph.html")
        edges = []
        nodes = []
        for t_name in self.resource_names:
            resource = self.get_resource(t_name)
            templates = {k: primary_key_template for k in resource.schema.primary_key}
            t_fields = [
                templates.get(f.name, field_template).render(name=f.name, type=f.type)
                for f in resource.schema.fields
            ]
            nodes.append(table_template.render(name=t_name, rows="".join(t_fields)))
            child_table = t_name
            for fk in resource.schema.foreign_keys:
                for foreign_key in fk["fields"]:
                    if fk["reference"]["resource"] == "":
                        continue
                    parent_table = fk["reference"]["resource"]
                    for parent_primary_key in fk["reference"]["fields"]:
                        edges.append(
                            f'"{parent_table}":{parent_primary_key}n -> "{child_table}":{foreign_key}n;'
                        )
        text = graph.render(
            name=self.name,
            tables="\n\t".join(nodes),
            edges="\n\t".join(edges),
        )

        # Write diagram
        path = path if path else "package.dot"
        try:
            helpers.write_file(path, text)
        except Exception as exc:
            raise FrictionlessException(self.__Error(note=str(exc))) from exc

        return path

    @staticmethod
    def from_bigquery(source, *, control=None):
        """Import package from Bigquery

        Parameters:
            source (string): BigQuery `Service` object
            control (dict): BigQuery control

        Returns:
            Package: package
        """
        storage = system.create_storage("bigquery", source, control=control)
        return storage.read_package()

    def to_bigquery(self, target, *, control=None):
        """Export package to Bigquery

        Parameters:
            target (string): BigQuery `Service` object
            control (dict): BigQuery control

        Returns:
            BigqueryStorage: storage
        """
        storage = system.create_storage("bigquery", target, control=control)
        storage.write_package(self.to_copy(), force=True)
        return storage

    @staticmethod
    def from_ckan(source, *, control=None):
        """Import package from CKAN

        Parameters:
            source (string): CKAN instance url e.g. "https://demo.ckan.org"
            control (dict): CKAN control

        Returns:
            Package: package
        """
        storage = system.create_storage("ckan", source, control=control)
        return storage.read_package()

    def to_ckan(self, target, *, control=None):
        """Export package to CKAN

        Parameters:
            target (string): CKAN instance url e.g. "https://demo.ckan.org"
            control (dict): CKAN control

        Returns:
            CkanStorage: storage
        """
        storage = system.create_storage("ckan", target, control=control)
        storage.write_package(self.to_copy(), force=True)
        return storage

    @staticmethod
    def from_sql(source, *, control=None):
        """Import package from SQL

        Parameters:
            source (any): SQL connection string of engine
            control (dict): SQL control

        Returns:
            Package: package
        """
        storage = system.create_storage("sql", source, control=control)
        return storage.read_package()

    def to_sql(self, target, *, control=None):
        """Export package to SQL

        Parameters:
            target (any): SQL connection string of engine
            control (dict): SQL control

        Returns:
            SqlStorage: storage
        """
        storage = system.create_storage("sql", target, control=control)
        storage.write_package(self.to_copy(), force=True)
        return storage

    @staticmethod
    def from_zip(path, **options):
        """Create a package from ZIP

        Parameters:
            path(str): file path
            **options(dict): resouce options
        """
        return Package(descriptor=path, **options)

    def to_zip(self, path, *, encoder_class=None, compression=zipfile.ZIP_DEFLATED):
        """Save package to a zip

        Parameters:
            path (str): target path
            encoder_class (object): json encoder class
            compression (int): the ZIP compression method to use when
                writing the archive. Possible values are the ones supported
                by Python's `zipfile` module.

        Raises:
            FrictionlessException: on any error
        """
        try:
            with zipfile.ZipFile(path, "w", compression=compression) as archive:
                package_descriptor = self.to_dict()
                for index, resource in enumerate(self.resources):
                    descriptor = package_descriptor["resources"][index]

                    # Remote data
                    if resource.remote:
                        pass

                    # Memory data
                    elif resource.memory:
                        if not isinstance(resource.data, list):
                            path = f"{resource.name}.csv"
                            descriptor["path"] = path
                            descriptor.pop("data", None)
                            with tempfile.NamedTemporaryFile() as file:
                                tgt = Resource(path=file.name, format="csv", trusted=True)
                                resource.write(tgt)
                                archive.write(file.name, path)

                    # Multipart data
                    elif resource.multipart:
                        for path, fullpath in zip(resource.path, resource.fullpath):
                            if os.path.isfile(fullpath):
                                if not helpers.is_safe_path(fullpath):
                                    note = f'Zipping usafe "{fullpath}" is not supported'
                                    error = errors.PackageError(note=note)
                                    raise FrictionlessException(error)
                                archive.write(fullpath, path)

                    # Local Data
                    else:
                        path = resource.path
                        fullpath = resource.fullpath
                        if os.path.isfile(fullpath):
                            if not helpers.is_safe_path(fullpath):
                                note = f'Zipping usafe "{fullpath}" is not supported'
                                error = errors.PackageError(note=note)
                                raise FrictionlessException(error)
                            archive.write(fullpath, path)

                # Metadata
                archive.writestr(
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

    # Metadata

    metadata_duplicate = True
    metadata_Error = errors.PackageError  # type: ignore
    metadata_profile = deepcopy(settings.PACKAGE_PROFILE)
    metadata_profile["properties"]["resources"] = {"type": "array"}

    @classmethod
    def metadata_properties(cls):
        return super().metadata_properties(resources=Resource)

    def metadata_validate(self):
        # Check invalid properties
        invalid_fields = {
            "missingValues": "resource.schema.missingValues",
            "fields": "resource.schema.fields",
        }
        for invalid_field, object in invalid_fields.items():
            if invalid_field in self:
                note = f'"{invalid_field}" should be set as "{object}" (not "package.{invalid_field}").'
                yield errors.PackageError(note=note)

        # Package
        if self.profile == "data-package":
            yield from super().metadata_validate()
        elif self.profile == "fiscal-data-package":
            yield from super().metadata_validate(settings.FISCAL_PACKAGE_PROFILE)
        elif self.profile == "tabular-data-package":
            yield from super().metadata_validate(settings.TABULAR_PACKAGE_PROFILE)
        else:
            if not self.trusted:
                if not helpers.is_safe_path(self.profile):
                    note = f'path "{self.profile}" is not safe'
                    error = errors.PackageError(note=note)
                    raise FrictionlessException(error)
            profile = Metadata(self.profile).to_dict()
            yield from super().metadata_validate(profile)

        # Resources
        for resource in self.resources:
            yield from resource.metadata_errors
        if len(self.resource_names) != len(set(self.resource_names)):
            note = "names of the resources are not unique"
            yield errors.PackageError(note=note)

        # Created
        if self.get("created"):
            field = Field(type="datetime")
            cell = field.read_cell(self.get("created"))[0]
            if not cell:
                note = 'property "created" is not valid "datetime"'
                yield errors.PackageError(note=note)

        # Contributors/Sources
        for name in ["contributors", "sources"]:
            for item in self.get(name, []):
                if item.get("email"):
                    field = Field(type="string", format="email")
                    cell = field.read_cell(item.get("email"))[0]
                    if not cell:
                        note = f'property "{name}[].email" is not valid "email"'
                        yield errors.PackageError(note=note)


# Internal


def read_row_stream(resource):
    with resource:
        for row in resource.row_stream:
            yield row


def validate_sequential(resource: Resource, *, original=False) -> Report:
    return resource.validate(original=original)


# TODO: rebase on from/to_descriptor
def validate_parallel(descriptor: IDescriptor) -> IDescriptor:
    basepath = descriptor.pop("basepath")
    trusted = descriptor.pop("trusted")
    original = descriptor.pop("original")
    resource = Resource.from_descriptor(descriptor, basepath=basepath, trusted=trusted)
    report = resource.validate(original=original)
    return report.to_descriptor()
