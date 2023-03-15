# Explore

```markdown remark type=info
If you started an exploration session and can't get out: press "q" on your keyboard.
```

With the `explore` command you can open your dataset in [Visidata](https://www.visidata.org/) which is an amazing visual tool for working with tabular data in Console. For example try "Shift+F" for creating data histograms!

## Installation

```bash tabs=CLI
pip install frictionless[visidata]
pip install frictionless[visidata,zenodo] # for examples in this tutorial
```

## Example

For example, let's expore this interesing dataset:

```bash tabs=CLI
frictionless explore https://zenodo.org/record/3977957
```

```yaml image
path: ../../assets/explore.png
width: unset
height: unset
```

## Documentation

Before entering Visidata, it's highly recommended to read its documentation:
- https://www.visidata.org/docs/

You can get it in Console as well:

```bash script tabs=CLI
vd --help
```
