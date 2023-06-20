from .package import PackageResource
from .resource import ResourceResource
from .table import TableResource

Convertible = (TableResource,)
Extractable = (TableResource, PackageResource, ResourceResource)
Indexable = (TableResource, PackageResource)
Transformable = (TableResource, PackageResource)
