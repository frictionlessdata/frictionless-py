from datapackage import Package


# Module API

def init_datapackage(resource_paths):
    # "Create tabular data package with resources.
    dp = Package({
        'name': 'change-me',
        'schema': 'tabular-data-package',
    })

    for path in resource_paths:
        dp.infer(path)

    return dp
