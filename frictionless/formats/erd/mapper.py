from __future__ import annotations
import os
from typing import TYPE_CHECKING
from ...platform import platform
from ...system import Mapper

if TYPE_CHECKING:
    from ...package import Package


class ErdMapper(Mapper):
    """ERD Mapper"""

    # Write

    def write_package(self, package: Package) -> str:
        package.infer()
        template_dir = os.path.join(
            os.path.dirname(__file__), "../../assets/templates/erd"
        )
        environ = platform.jinja2.Environment(
            loader=platform.jinja2.FileSystemLoader(template_dir),
            lstrip_blocks=True,
            trim_blocks=True,
        )
        table_template = environ.get_template("table.html")
        field_template = environ.get_template("field.html")
        primary_key_template = environ.get_template("primary_key_field.html")
        graph = environ.get_template("graph.html")
        edges = []
        nodes = []
        for t_name in package.resource_names:
            resource = package.get_resource(t_name)  # type: ignore
            templates = {k: primary_key_template for k in resource.schema.primary_key}
            t_fields = [
                templates.get(f.name, field_template).render(name=f.name, type=f.type)  # type: ignore
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
        return graph.render(
            name=package.name,
            tables="\n\t".join(nodes),
            edges="\n\t".join(edges),
        )
