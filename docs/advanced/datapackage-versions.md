# Data Package versions

This page documents how the framework resolves and handles the Data Package
standard versions (v1 and v2).

## Declaring a version

A descriptor declares its version through `$schema`, a JSON Schema profile URL:

```python
package = Package({
    "$schema": "https://datapackage.org/profiles/2.0/datapackage.json",
    "name": "package",
    # ... v2 features are accepted from here on
})
```

The standard profiles are hosted at `https://datapackage.org/profiles/{1.0,2.0}/{datapackage,dataresource,tableschema,tabledialect}.json`.

## Resolution rules

The version of a descriptor is resolved once, top-down, at
descriptor-validation time. In accordance with the specification, only the
root object is expected to have a `$schema` property; all child objects
inherit the resolved version of the root.

The resolved version depends on the descriptor's own declaration:
   - if its `$schema` is a standard `datapackage.org` profile URL, the
     version is resolved to the version in its URL (v1 or v2);
   - if its `$schema` is a custom profile URL, the version resolves to
     `"unknown"`: validation will be lenient and accept a **superset of v1
     and v2** (instead of guessing a standard version);
   - an absent `$schema` is an explicit v1, as mandated by the spec.

| Descriptor state                     | Resolved version        |
| ---                                  | ---                     |
| Under a v1/v2/unknown ancestor       | the ancestor's version  |
| `$schema` standard profile URL       | v1 or v2 (from the URL) |
| `$schema` custom URL                 | unknown (superset)      |
| `$schema` absent                     | v1                      |

### Version gates

v2-specific features apply on explicit v2 version or when version is unknown.
These features may raise errors or be ignored however when validating with
unambiguous v1 version. See table below for examples of behavior changes.

| Feature | v1 | v2 / unknown |
| --- | --- | --- |
| `name` restricted to the v1 pattern | enforced | any string |
| `missingValues` object form `{value, label?}` | rejected | accepted |
| `exclusiveMinimum` / `exclusiveMaximum` | rejected | accepted |
| `groupChar` for `integer` fields | rejected | accepted |

## Detached children keep the inherited version

`Resource` and `Schema` store the version they resolved at import time (a
private `_datapackage_version`). This stored version is threaded top-down at
import, and seeded back into every detached validation, so that:

- `package.validate()` (which validates each resource standalone) agrees with `package.validate_descriptor()`;
- a resource extracted from a package, a `to_copy()` copy, or a transform pipeline step keeps the semantics of its tree instead of re-resolving positionally;
- a path-referenced schema lazily loaded by a resource inherits the resource's version.

Exports stay canonical: by default, exporting the descriptor of children and
reimporting them will change the behavior. The absent `$schema` property of the
children is interpreted as v1 at re-import. Exporting with `upgrade=True`
produces however a standalone descriptor of a child (see below).

## Upgrading to v2

`upgrade()` returns a new instance (the original is untouched) whose descriptor tree is transformed into the v2 form — also available as an export option: `to_descriptor(upgrade=True)`.

- the root gets `$schema` (as its first property) set to the canonical v2 profile of the class (`Package` → `datapackage.json`, `Resource` → `dataresource.json`, `Schema` → `tableschema.json`, `Dialect` → `tabledialect.json`);
- `$schema` is root-only: a child `$schema` is removed (it would be ignored by the inheritance rules anyway);
- the legacy `profile` property is migrated: a custom profile URL is retained
  in `$schema`; `"tabular-data-resource"` becomes `"type": "table"`; other
  values are dropped.

A `$schema` or `profile` pointing to a **custom profile URL is kept as-is**:
an automatic upgrade of a custom profile is currently not supported. Its
upgrade is up to its author. As a consequence, an upgraded custom profile
resolves to `"unknown"` (permissive).

```python
package = Package("package-v1.json")
v2_package = package.upgrade()  # a new, v2 instance
```
