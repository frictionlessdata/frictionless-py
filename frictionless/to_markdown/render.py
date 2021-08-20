# Get a compiler
from pybars import Compiler
import json
import glom
import os
from helpers import helpers

compiler = Compiler()

def getText(loc):
    with open(loc, "r") as file:
        data = file.read()
    return data

# Compile the template
source = getText("./templates/index.hbs")
template = compiler.compile(source)

lang = "en"
langLoc = "./i18n/" + lang + ".json"
print(langLoc)
intlData = json.loads(getText(langLoc))


def intlGet(this, key):
    return glom(intlData, key)


# helpers = {'intlGet': intlGet}

partials = {}


def loadPartial(location):
    data = getText(location)
    p = compiler.compile(data)
    name = os.path.splitext(location)[0]
    print(f"loading partial {name}")
    partials[name] = p


ps = [
    "./templates/partials/fields-as-headings/constraintHeadingProperties.hbs",
    "./templates/partials/fields-as-table/constraintTableProperties.hbs",
    "./templates/partials/default/properties.hbs",
    "./templates/partials/default/property.hbs",
    "./templates/partials/default/propertyListItemArrayIfValue.hbs",
    "./templates/partials/default/propertyListItemIfValue.hbs",
    "./templates/partials/default/titleNamePath.hbs",
    "./templates/partials/fields-as-headings/schemaField.hbs",
    "./templates/partials/fields-as-headings/schemaFields.hbs",
]

for p in ps:
    loadPartial(p)

data = json.loads("./datapackage.json")

# Render the template
output = template(data, helpers={**helpers, **{"intlGet": intlGet}}, partials=partials)

print(output)
