import os
from pathlib import Path
from typing import List, Dict, Any, Union
from .control import ZenodoControl
from ...system import Adapter
from ...catalog import Catalog
from ...exception import FrictionlessException
from ...package import Package
from ...platform import platform
from ...resource import Resource


class ZenodoAdapter(Adapter):
    """Read and write data from/to Zenodo"""

    def __init__(self, control: ZenodoControl):
        self.control = control

    # Read

    def read_catalog(self) -> Catalog:
        packages: List[Union[Package, str]] = []
        options: Dict[str, Any] = {}

        # Single record
        if self.control.record:
            packages.append(self.read_package())
            return Catalog(name=self.control.name or "catalog", packages=packages)

        # DOI
        assert self.control.formats
        client = platform.pyzenodo3.Zenodo(api_key=self.control.apikey)
        if self.control.doi:
            dataset = client.find_record_by_doi(self.control.doi)
            name = self.control.name or dataset.data["metadata"]["title"]
            package = get_package(dataset.data["files"], name, self.control.formats)
            if isinstance(package, Package) and package.resources:
                packages.append(package)
            return Catalog(name=name, packages=packages)

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
                package = get_package(dataset.data["files"], name, self.control.formats)
                if isinstance(package, Package) and package.resources:
                    packages.append(package)
        except Exception as exception:
            note = "Github API error" + repr(exception)
            raise FrictionlessException(note)
        if packages:
            return Catalog(name=self.control.name or "catalog", packages=packages)
        note = "Package/s not found"
        raise FrictionlessException(note)

    def read_package(self) -> Package:
        client = platform.pyzenodo3.Zenodo(api_key=self.control.apikey)
        if not self.control.record:
            note = "Record is required."
            raise FrictionlessException(note)
        assert self.control.formats
        package = Package()
        try:
            dataset = client.get_record(self.control.record)
            if dataset:
                name = self.control.name or dataset.data["metadata"]["title"]
                package = get_package(dataset.data["files"], name, self.control.formats)
        except Exception as exception:
            note = "Zenodo API error" + repr(exception)
            raise FrictionlessException(note)
        if isinstance(package, Package) and package.resources:
            return package
        note = "Package/s not found"
        raise FrictionlessException(note)

    # Write
    def write_package(self, package: Package) -> int:
        client = platform.pyzenodo3_upload

        assert self.control.base_url
        assert self.control.apikey
        client.BASE_URL = self.control.base_url
        if not self.control.metafn:
            note = "Metafn(metadata file) is required."
            raise FrictionlessException(note)
        try:
            deposition_id = self.control.deposition_id
            if not deposition_id:
                # Create a deposition resource
                deposition_id = client.create(
                    token=self.control.apikey, base_url=self.control.base_url
                )
            metafn = Path(self.control.metafn).expanduser()
            client.upload_meta(
                token=self.control.apikey,
                metafn=metafn,
                depid=deposition_id,
            )

            # Process resources
            resources = []
            for key, resource in enumerate(package.resources):
                if resource.data:
                    resource_file_name = f"{resource.name}.json" or f"resource{key}.json"
                    resource_path = os.path.join(
                        self.control.tmp_path or "", resource_file_name
                    )
                    resource.to_json(resource_path)
                    resources.append(Path(resource_path).expanduser())
                    continue

                resource_path = resource.path or ""
                if resource_path.startswith(("http://", "https://")):
                    continue

                if resource.basepath:
                    resource_path = os.path.join(
                        str(resource.basepath), str(resource.path)
                    )
                resources.append(Path(resource_path).expanduser())
            package_path = os.path.join(self.control.tmp_path or "", "datapackage.json")
            package.to_json(package_path)

            # Upload package and resources
            client.upload_data(
                token=self.control.apikey,
                datafn=Path(package_path).expanduser(),
                depid=deposition_id,
                base_url=self.control.base_url,
            )
            for resource_path in resources:
                resource_path = Path(resource_path).expanduser()
                client.upload_data(
                    token=self.control.apikey,
                    datafn=resource_path,
                    depid=deposition_id,
                    base_url=self.control.base_url,
                )
            return deposition_id
        except Exception as exception:
            note = "Zenodo API error" + repr(exception)
            raise FrictionlessException(note)


def get_package(files: List, title: str, formats: List[str]) -> Package:
    package = Package()
    package.title = title
    for file in files:
        path = file["links"]["self"]
        is_resource_file = any(path.endswith(ext) for ext in formats)
        if path.endswith(("datapackage.json", "datapackage.yaml")):
            return Package.from_descriptor(path, title=title)
        if path.endswith("zip") and not is_resource_file:
            try:
                package = Package(path)
                package.title = title
                return package
            except FrictionlessException as exception:
                # Skips package descriptor not found exception
                # and continues reading files.
                if not "[Errno 2] No such file or directory" in str(exception):
                    raise exception
        if is_resource_file:
            base_path = f'https://zenodo.org/api/files/{file["bucket"]}'
            resource = Resource(path=file["key"], basepath=base_path)
            resource.infer(sample=False)
            package.add_resource(resource)
    return package
