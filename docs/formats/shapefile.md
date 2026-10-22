---
script:
  basepath: data
---

# Shapefile Format

Frictionless supports reading ESRI Shapefiles. They are read with [GeoPandas](https://geopandas.org); geometries are exposed as [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) strings in a `string` field with the `wkt` format.

```bash tabs=CLI
pip install frictionless[shapefile]
pip install 'frictionless[shapefile]' # for zsh shell
```

## Reading Data

A shapefile can be read either from its `.shp` file (with the sidecar `.shx`, `.dbf` and `.prj` files next to it) or from a zip archive containing these files:

```bash script tabs=CLI
frictionless extract shapefile/points.zip
```

```python script tabs=Python
from frictionless import Resource

resource = Resource('shapefile/points.zip')
print(resource.read_rows())
```

A zip archive is only treated as a shapefile when it contains a `.shp` file and no `datapackage.json`. Remote archives are not inspected, use `format="shp"` for them.

## Multiple Layers

A zip archive can contain several shapefiles, each of them is a layer. Such an archive is described as a data package with one resource per layer:

```bash script tabs=CLI
frictionless describe shapefile/layers.zip
```

```python script tabs=Python
from frictionless import Package

package = Package('shapefile/layers.zip')
print(package.resource_names)
```

A single layer can be selected with the control:

```python script tabs=Python
from frictionless import Resource, formats

control = formats.ShapefileControl(layer='areas')
resource = Resource('shapefile/layers.zip', control=control)
print(resource.read_rows())
```

## Validating Data

After refining the described schema, for example by adding constraints, the data can be validated against it:

```bash script tabs=CLI
frictionless validate shapefile/points.zip --schema shapefile/points.schema.yaml
```

## Reference

```yaml reference
references:
  - frictionless.formats.ShapefileControl
```
