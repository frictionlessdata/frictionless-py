# JsonSchema Format

```markdown remark type=warning
This documentation page is work-in-progress
```

Frictionless supports importing a JsonSchema profile as a Table Schema. For example:

```python
schema = Schema.from_jsonschema('table.jsonschema')
```

## Constraints

The constraint keywords of the JsonSchema are carried onto the fields the
mapper builds, so a table that violates one of them is reported invalid:

| JsonSchema | Carried as | Field types |
|---|---|---|
| `minLength`, `maxLength` | `minLength`, `maxLength` | string |
| `minimum`, `maximum` | `minimum`, `maximum` | integer, number |
| `minItems`, `maxItems` | `minLength`, `maxLength` | array |
| `minProperties`, `maxProperties` | `minLength`, `maxLength` | object |
| `enum` | `enum` | string, integer, number, boolean, array, object, and a typeless property whose members are strings |

The page describes JsonSchema draft-07. These draft-07 keywords are not
carried:

- `pattern`, because it is a partial match in JsonSchema and a full match in
  Frictionless: a table the JsonSchema accepts would be reported invalid.
- `exclusiveMinimum` and `exclusiveMaximum`, because the mapper builds a Data
  Package v1 schema and Frictionless rejects them there: they need v2.
- `const`, `multipleOf` and `uniqueItems`, because Frictionless has no
  counterpart for them.
- `format`, because in JsonSchema it is an annotation that says nothing about
  the value, while Frictionless's `format` rejects the values that do not
  match it. Carrying it would make the check stricter than the JsonSchema
  asks for.
- `additionalItems`, `contains`, `patternProperties` and `propertyNames`,
  because they describe a structure that a Table Schema field does not have.
- `items`, `properties`, `additionalProperties`, `allOf`, `anyOf`, `oneOf`,
  `if`, `then`, `else`, `not` and `dependencies`, for the same reason.
- `title`, `default`, `examples`, `readOnly` and `writeOnly`, because they are
  annotations rather than constraints. (`description` is carried onto the
  field, but it constrains nothing.)
- `$id`, `$schema`, `$ref` and `$comment`, because they describe the schema
  itself rather than a value.

A constraint whose value the field cannot read is not carried either. The
question is asked of the field itself, so the answer stays right as the field
types change:

- a fractional `minimum` on an integer field would raise a `TypeError` rather
  than report a violation;
- an `enum` of numbers on a string field would make every row invalid rather
  than the rows that break the rule;
- a numeric `enum` on a property with no type would make every row of a
  tabular source invalid, because a cell read from a CSV is a string.

A length or an element count has to be a whole number: a `minLength` of 2.5
is not a length, and carrying it would compare every cell against a count it
can never satisfy.
