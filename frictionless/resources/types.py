from .json import PackageResource, ResourceResource
from .table import TableResource

Convertible = (TableResource,)
Extractable = (TableResource, PackageResource, ResourceResource)
Indexable = (TableResource, PackageResource)
Transformable = (TableResource, PackageResource)
