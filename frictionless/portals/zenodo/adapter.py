from __future__ import annotations

import datetime
import json
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Union, cast

from ... import models
from ...catalog import Catalog, Dataset
from ...exception import FrictionlessException
from ...package import Package
from ...platform import platform
from ...resource import Resource
from ...system import Adapter
from .control import ZenodoControl
from .models import ZenodoCreator, ZenodoMetadata

if TYPE_CHECKING:
    from pyzenodo3 import Record  # type: ignore


class ZenodoAdapter(Adapter):
    """Read and write data from/to Zenodo"""

    def __init__(self, control: ZenodoControl):
        self.control = control

    # Read

    def read_package(self) -> Package:
        client = platform.pyzenodo3.Zenodo(api_key=self.control.apikey)  # type: ignore
        if not self.control.record:
            note = "Record is required."
            raise FrictionlessException(note)
        assert self.control.formats
        package = Package()
        try:
            dataset = client.get_record(self.control.record)
            if dataset:
                name = self.control.name or dataset.data["metadata"]["title"]
                package = get_package(dataset, name, self.control.formats)
        except Exception as exception:
            note = "Zenodo API error" + repr(exception)
            raise FrictionlessException(note)
        if isinstance(package, Package) and package.resources:  # type: ignore
            return package
        note = "Package/s not found"
        raise FrictionlessException(note)

    # Write

    def write_package(self, package: Package):
        client = platform.pyzenodo3_upload
        client.BASE_URL = self.control.base_url

        # Ensure api key
        if not self.control.apikey:
            raise FrictionlessException("Api key is required for zenodo publishing")

        try:
            # Ensure deposition
            deposition_id = self.control.deposition_id
            if not deposition_id:
                deposition_id = cast(
                    int,
                    client.create(
                        token=self.control.apikey,
                        base_url=self.control.base_url,
                    ),
                )

            # Generate metadata
            if self.control.metafn:
                descriptor = json.loads(Path(self.control.metafn).read_text())
                meta = descriptor.get("metadata", {})
                meta.setdefault("publication_date", str(datetime.date.today()))
                meta.setdefault("access_right", "open")
                metadata = ZenodoMetadata(**meta)
            else:
                description = self.control.description or package.description or "About"
                license = "CC-BY-4.0"
                if package.licenses:
                    license = package.licenses[0].get("name", license)
                metadata = ZenodoMetadata(
                    title=self.control.title or package.title or "Title",
                    description=description,
                    license=license,
                    publication_date=str(datetime.date.today()),
                )
                if self.control.author:
                    metadata.creators.append(
                        ZenodoCreator(
                            name=self.control.author,
                            affiliation=self.control.company,
                        )
                    )
                for contributor in package.contributors:
                    metadata.creators.append(
                        ZenodoCreator(
                            name=contributor.get("title", "Title"),
                            affiliation=contributor.get("organization"),
                        )
                    )

            # Upload metadata
            with tempfile.NamedTemporaryFile("wt") as file:
                data = dict(metadata=metadata.model_dump(exclude_none=True))
                json.dump(data, file, indent=2)
                file.flush()
                client.upload_meta(
                    token=self.control.apikey,
                    metafn=file.name,
                    depid=deposition_id,
                )

            # Upload package
            with tempfile.TemporaryDirectory() as dir:
                path = Path(dir) / "datapackage.json"
                package.to_json(str(path))
                client.upload_data(
                    token=self.control.apikey,
                    datafn=path,
                    depid=deposition_id,
                    base_url=self.control.base_url,
                )

            # Upload resource
            for resource in package.resources:
                if resource.normpath and not resource.remote:
                    client.upload_data(
                        token=self.control.apikey,
                        datafn=Path(resource.normpath),
                        depid=deposition_id,
                        base_url=self.control.base_url,
                    )

            # Return result
            return models.PublishResult(
                url=f"https://zenodo.org/deposit/{deposition_id}",
                context=dict(deposition_id=deposition_id),
            )

        except Exception as exception:
            note = "Zenodo API error" + repr(exception)
            raise FrictionlessException(note)

    # Experimental

    def read_catalog(self) -> Catalog:
        packages: List[Union[Package, str]] = []
        options: Dict[str, Any] = {}

        # Single record
        if self.control.record:
            packages.append(self.read_package())
            return Catalog(
                datasets=[
                    Dataset(name=package.name, package=package)  # type: ignore
                    for package in packages
                ]
            )

        # DOI
        assert self.control.formats
        client = platform.pyzenodo3.Zenodo(api_key=self.control.apikey)  # type: ignore
        if self.control.doi:
            dataset = client.find_record_by_doi(self.control.doi)
            name = self.control.name or dataset.data["metadata"]["title"]
            package = get_package(dataset, name, self.control.formats)
            if isinstance(package, Package) and package.resources:  # type: ignore
                packages.append(package)
            return Catalog(
                datasets=[
                    Dataset(name=package.name, package=package)  # type: ignore
                    for package in packages
                ]
            )

        # Search
        if self.control.search:
            search = self.control.search.replace(
                "/", " "
            )  # zenodo can't handle '/' in search query
            options["q"] = search
        options["status"] = self.control.status
        options["sort"] = self.control.sort
        options["page"] = self.control.page
        options["size"] = self.control.size
        options["all_versions"] = self.control.all_versions
        options["communities"] = self.control.communities
        options["type"] = self.control.rtype
        options["subtype"] = self.control.subtype
        options["bounds"] = self.control.bounds
        options["custom"] = self.control.rcustom
        options = {key: value for key, value in options.items() if value}
        try:
            records = client._get_records(options)
            for dataset in records:
                name = self.control.name or dataset.data["metadata"]["title"]
                package = get_package(dataset, name, self.control.formats)
                if isinstance(package, Package) and package.resources:  # type: ignore
                    packages.append(package)
        except Exception as exception:
            note = "Zenodo API error" + repr(exception)
            raise FrictionlessException(note)
        if packages:
            return Catalog(
                datasets=[
                    Dataset(name=package.name, package=package)  # type: ignore
                    for package in packages
                ]
            )
        note = "Package/s not found"
        raise FrictionlessException(note)


def get_package(record: Record, title: str, formats: List[str]) -> Package:  # type: ignore
    package = Package(title=title)
    package.title = title
    for file in record.data["files"]:  # type: ignore
        path = file["links"]["self"]  # type: ignore
        is_resource_file = any(path.endswith(ext) for ext in formats)  # type: ignore
        if path.endswith(("datapackage.json")):  # type: ignore
            return Package.from_descriptor(path, title=title)  # type: ignore
        if path.endswith("zip") and not is_resource_file:  # type: ignore
            try:
                package = Package(path)  # type: ignore
                package.title = title
                return package
            except FrictionlessException as exception:
                # Skips package descriptor not found exception
                # and continues reading files.
                if "[Errno 2] No such file or directory" not in str(exception):
                    raise exception
        if is_resource_file:
            package.basepath = f'https://zenodo.org/api/files/{file["bucket"]}'
            resource = Resource(path=file["key"])  # type: ignore
            package.add_resource(resource)
    return package
