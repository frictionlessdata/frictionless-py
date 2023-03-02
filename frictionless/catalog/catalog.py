from __future__ import annotations
import attrs
from typing import TYPE_CHECKING, Optional, List, Any, Union, ClassVar

from sqlalchemy.engine import base
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..platform import platform
from ..system import system
from .dataset import Dataset
from .. import settings
from .. import helpers
from .. import errors

if TYPE_CHECKING:
    from ..dialect import Control
    from ..interfaces import IDescriptor


@attrs.define(kw_only=True)
class Catalog(Metadata):
    """Catalog representation"""

    source: Optional[Any] = attrs.field(default=None, kw_only=False)
    """
    # TODO: add docs
    """

    control: Optional[Control] = None
    """
    # TODO: add docs
    """

    name: Optional[str] = None
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “.”, “_” or “-” characters.
    """

    type: ClassVar[Union[str, None]] = None
    """
    Type of the object
    """

    title: Optional[str] = None
    """
    A Catalog title according to the specs. It should be a
    human-oriented title of the resource.
    """

    description: Optional[str] = None
    """
    A Catalog description according to the specs. It should be a
    human-oriented description of the resource.
    """

    datasets: List[Dataset] = attrs.field(factory=list)
    """
    A list of datasets. Each package in the list is a Data Dataset.
    """

    basepath: Optional[str] = None
    """
    A basepath of the catalog. The normpath of the resource is joined
    `basepath` and `/path`
    """

    @classmethod
    def from_source(
        cls,
        source: Any,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
    ) -> Optional[Catalog]:
        source = helpers.normalize_source(source)

        # Adapter
        if source is not None or control is not None:
            adapter = system.create_adapter(source, control=control, basepath=basepath)
            if adapter:
                catalog = adapter.read_catalog()
                return catalog

    @classmethod
    def __create__(
        cls,
        source: Optional[Any] = None,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        **options,
    ):
        # Source/control
        if source is not None or control is not None:
            if cls is not Catalog:
                note = 'Providing "source" argument is only possible to "Catalog" class'
                raise FrictionlessException(note)
            catalog = cls.from_source(source, control=control, basepath=basepath)
            if not catalog:
                catalog = cls.from_descriptor(source, basepath=base, **options)  # type: ignore
            return catalog

    def __attrs_post_init__(self):
        for dataset in self.datasets:
            dataset.catalog = self
            dataset.package.dataset = dataset

    # Datasets

    @property
    def dataset_names(self) -> List[str]:
        """Return names of datasets"""
        return [dataset.name for dataset in self.datasets if dataset.name is not None]

    def add_dataset(self, dataset: Union[Dataset, str]) -> Dataset:
        """Add new dataset to the catalog"""
        if isinstance(dataset, str):
            dataset = Dataset.from_descriptor(dataset, basepath=self.basepath)
        self.datasets.append(dataset)
        dataset.catalog = self
        return dataset

    def has_dataset(self, name: str) -> bool:
        """Check if a dataset is present"""
        for dataset in self.datasets:
            if dataset.name == name:
                return True
        return False

    def get_dataset(self, name: str) -> Dataset:
        """Get dataset by name"""
        for dataset in self.datasets:
            if dataset.name == name:
                return dataset
        error = errors.CatalogError(note=f'dataset "{name}" does not exist')
        raise FrictionlessException(error)

    def set_dataset(self, dataset: Dataset) -> Optional[Dataset]:
        """Set dataset by name"""
        assert dataset.name
        if self.has_dataset(dataset.name):
            prev_dataset = self.get_dataset(dataset.name)
            index = self.datasets.index(prev_dataset)
            self.datasets[index] = dataset
            dataset.dataset = self
            return prev_dataset
        self.add_dataset(dataset)

    def remove_dataset(self, name: str) -> Dataset:
        """Remove dataset by name"""
        dataset = self.get_dataset(name)
        self.datasets.remove(dataset)
        return dataset

    def clear_datasets(self):
        """Remove all the datasets"""
        self.datasets = []

    def deduplicate_datasets(self):
        if len(self.dataset_names) != len(set(self.dataset_names)):
            seen_names = []
            for index, dataset in enumerate(self.datasets):
                name = dataset.name
                count = seen_names.count(name) + 1
                if count > 1:
                    self.datasets[index].name = "%s%s" % (name, count)
                seen_names.append(name)

    # Infer

    def infer(self, *, stats=False):
        """Infer catalog's metadata

        Parameters:
            stats? (bool): stream files completely and infer stats
        """
        for dataset in self.datasets:
            dataset.infer(stats=stats)

    # Dereference

    def dereference(self):
        """Dereference underlaying metadata

        If some of underlaying metadata is provided as a string
        it will replace it by the metadata object
        """
        for dataset in self.datasets:
            dataset.dereference()

    # Convert

    def to_copy(self, **options):
        """Create a copy of the catalog"""
        return super().to_copy(
            basepath=self.basepath,
            **options,
        )

    # Metadata

    metadata_type = "catalog"
    metadata_Error = errors.CatalogError
    metadata_profile = {
        "type": "object",
        "required": ["datasets"],
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "datasets": {
                "type": "array",
                "items": {"type": "object"},
            },
        },
    }

    @classmethod
    def metadata_select_property_class(cls, name):
        if name == "datasets":
            return Dataset

    @classmethod
    def metadata_import(cls, descriptor: IDescriptor, **options):
        return super().metadata_import(
            descriptor=descriptor,
            with_basepath=True,
            **options,
        )
