# Erd Format

```markdown remark type=warning
This documentation page is work-in-progress
```

Frictionless supports exporting a data package as an ER-diagram `dot` file. For example:

```python
package = Package('datapackage.zip')
package.to_er_diagram(path='erd.dot')
```
