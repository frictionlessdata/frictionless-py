# Get a compiler
from pybars import Compiler
compiler = Compiler()

# Compile the template
source = u""
template = compiler.compile(source)


def intlGet(this, key):
    pass

helpers = {'list': _list}

# Add partials
header = compiler.compile(u'<h1>People</h1>')
partials = {'header': header}

# Render the template
output = template(data, helpers=helpers, partials=partials)

print(output)