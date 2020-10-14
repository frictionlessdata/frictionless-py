import re
import sys
import uuid
import logging
import datetime
import itertools
import collections
from copy import copy
from ..plugin import Plugin
from .. import helpers

tracer = logging.getLogger("elasticsearch")
tracer.setLevel(logging.CRITICAL)
tracer.addHandler(logging.StreamHandler(sys.stderr))


# Plugin


class ElasticPlugin(Plugin):
    """Plugin for ElasticSearch

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.elastic import ElasticPlugin`
    """

    def create_dialect(self, resource, *, descriptor):
        pass

    def create_parser(self, resource):
        pass

    def create_storage(self, name, **options):
        pass


# TODO: implement Dialect
# TODO: implement Parser


# Storage


class Storage(object):
    """Elastic storage implementation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.elastic import ElasticStorage`
    """

    def __init__(self, es=None):
        es_core = helpers.import_from_plugin("elasticsearch", plugin="elasticsearch")

        # Attributes
        self.__es = es if es is not None else es_core.Elasticsearch()
        self.__no_mapping_types = self.__es.info()["version"]["number"] >= "7"

    # Read

    def read_table_names(self):
        indexes = self.__es.indices.get_alias("*")
        for index_name, index in indexes.items():
            for alias_name in index.get("aliases", {}).keys():
                yield alias_name

    def read_table_row_stream(self, bucket, doc_type=None):
        from_ = 0
        size = 100
        done = False
        while not done:
            body = None
            if doc_type is not None:
                body = dict(
                    query=dict(bool=dict(filter=dict(match=dict(_type=doc_type))))
                )
            results = self.__es.search(index=bucket, body=body, from_=from_, size=size)
            hits = results.get("hits", {}).get("hits", [])
            for source in hits:
                yield source.get("_source")
            done = len(hits) == 0
            from_ += size

    # Write

    def write_table(
        self,
        bucket,
        doc_types,
        reindex=False,
        always_recreate=False,
        mapping_generator_cls=None,
        index_settings=None,
    ):
        """Create index with mapping by schema.

        # Arguments
            bucket(str):
                Name of index to be created
            doc_types(list<(doc_type, descriptor)>):
                List of tuples of doc_types and matching descriptors
            always_recreate:
                Delete index if already exists (otherwise just update mapping)
            reindex:
                On mapping mismath, automatically create
                new index and migrate existing indexes to it
            mapping_generator_cls:
                subclass of MappingGenerator
            index_settings:
                settings which will be used in index creation

        """
        es_exceptions = helpers.import_from_plugin(
            "elasticsearch.exceptions", plugin="elasticsearch"
        )

        existing_index_names = []
        if self.__es.indices.exists_alias(name=bucket):
            existing_index_names = self.__es.indices.get_alias(bucket)
            existing_index_names = sorted(existing_index_names.keys())

        if len(existing_index_names) == 0 or always_recreate:
            index_name = self.create_index(bucket, index_settings=index_settings)
            self.put_mapping(bucket, doc_types, index_name, mapping_generator_cls)

        else:
            index_name = existing_index_names[-1]
            try:
                self.put_mapping(bucket, doc_types, index_name, mapping_generator_cls)
                existing_index_names.pop(-1)

            except es_exceptions.RequestError:
                if reindex:
                    index_name = self.create_index(bucket, index_settings=index_settings)
                    self.put_mapping(bucket, doc_types, index_name, mapping_generator_cls)
                else:
                    raise

        if reindex and len(existing_index_names) > 0:
            reindex_body = dict(
                source=dict(index=existing_index_names),
                dest=dict(index=index_name, version_type="external"),
            )
            self.__es.reindex(reindex_body)
            self.__es.indices.flush()

            for existing_index_name in existing_index_names:
                self.__es.indices.delete(existing_index_name)

    def write_table_put(self, bucket, doc_types, index_name, mapping_generator_cls):
        for doc_type, descriptor in doc_types:
            mapping = self.write_table_convert(
                descriptor, mapping_generator_cls=mapping_generator_cls
            )
            params = dict()
            if doc_type is not None and self.__no_mapping_types:
                params = dict(include_type_name="true")
            self.__es.indices.put_mapping(
                mapping, doc_type=doc_type, index=index_name, params=params
            )

    def write_table_convert(self, descriptor, mapping_generator_cls=None):
        """Convert descriptor to ElasticSearch Mapping."""

        if mapping_generator_cls is None:
            mapping_generator_cls = MappingGenerator
        mapping_gen = mapping_generator_cls()
        mapping_gen.generate_from_schema(descriptor)
        return mapping_gen.get_mapping()

    def write_table_remove(self, bucket=None):
        """Delete index with mapping by schema.

        # Arguments
            bucket(str): Name of index to delete

        """

        def internal_delete(bucket):
            if self.__es.indices.exists_alias(name=bucket):
                existing_index_names = self.__es.indices.get_alias(bucket)
                existing_index_names = list(existing_index_names.keys())
                for existing_index_name in existing_index_names:
                    self.__es.indices.delete(existing_index_name)

        if bucket is None:
            for bucket in self.buckets:
                internal_delete(bucket)
        else:
            internal_delete(bucket)

    def write_table_row_stream(
        self, bucket, doc_type, rows, primary_key, update=False, as_generator=False
    ):
        es_helpers = helpers.import_from_plugin(
            "elasticsearch.helpers", plugin="elasticsearch"
        )

        if primary_key is None or len(primary_key) == 0:
            raise ValueError("primary_key cannot be an empty list")

        def actions(rows_, doc_type_, primary_key_, update_):
            if update_:
                for row_ in rows_:
                    yield {
                        "_op_type": "update",
                        "_index": bucket,
                        "_type": doc_type_,
                        "_id": self.generate_doc_id(row_, primary_key_),
                        "_source": {"doc": row_, "doc_as_upsert": True},
                    }
            else:
                for row_ in rows_:
                    yield {
                        "_op_type": "index",
                        "_index": bucket,
                        "_type": doc_type_,
                        "_id": self.generate_doc_id(row_, primary_key_),
                        "_source": row_,
                    }

        iterables = itertools.tee(rows)
        actions_iterable = actions(iterables[0], doc_type, primary_key, update)

        iter = zip(
            es_helpers.streaming_bulk(self.__es, actions=actions_iterable), iterables[1]
        )

        if as_generator:
            for result, row in iter:
                yield row
        else:
            collections.deque(iter, maxlen=0)

        self.__es.indices.flush(bucket)

    # Private

    def generate_doc_id(self, row, primary_key):
        return "/".join([str(row.get(k)) for k in primary_key])

    def get_index_name(self, bucket):
        uid = str(uuid.uuid4())[:8]
        today = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        return "{}_{}_{}".format(bucket, today, uid)

    def create_index(self, bucket, index_settings=None):
        index_name = self.get_index_name(bucket)
        body = None
        if index_settings is not None:
            body = dict(settings=index_settings)
        self.__es.indices.create(index_name, body=body)
        self.__es.indices.put_alias(index_name, bucket)
        return index_name


# Internal


class MappingGenerator(object):

    DATE_CONVERSION = {
        "d": "dd",
        "m": "MM",
        "y": "yy",
        "Y": "yyyy",
        "H": "HH",
        "M": "mm",
        "S": "ss",
        "f": "SSS",
    }

    def __init__(self, base={}):
        self._mapping = base

    @classmethod
    def _quote_literals(cls, s):
        return re.sub("[a-zA-Z]+", lambda x: "'" + x.group(0) + "'", s)

    @classmethod
    def _convert_date_format(cls, fmt):
        if fmt not in [None, "default", "any"]:
            parts = fmt.split("%")
            fmt = ""
            for i, part in enumerate(parts):
                if len(part) == 0:
                    continue
                if i > 0:
                    modifier = part[0]
                    part = part[1:]
                    fmt += cls.DATE_CONVERSION[modifier]
                fmt += cls._quote_literals(part)
            assert "%" not in fmt
            return fmt
        else:
            return "strict_date_optional_time"

    @classmethod
    def _convert_type(cls, schema_type, field, prefix):
        enabled = field.get("es:index", True)
        if enabled and schema_type == "object":
            try:
                subschema = field["es:schema"]
            except KeyError:
                raise ValueError(
                    "Must define es:schema for object fields"
                    " (or disable them using es:index=False)"
                )

        else:
            subschema = {"fields": []}

        prop = {
            "integer": {"type": "long", "ignore_malformed": True, "index": False},
            "year": {"type": "long", "ignore_malformed": True, "index": False},
            "number": {
                "type": "scaled_float",
                "scaling_factor": 100,
                "ignore_malformed": True,
                "index": False,
            },
            "string": {"type": "text"},
            "boolean": {"type": "boolean"},
            "date": {
                "type": "date",
                "ignore_malformed": True,
                "format": cls._convert_date_format(field.get("format")),
            },
            "datetime": {
                "type": "date",
                "ignore_malformed": True,
                "format": cls._convert_date_format(field.get("format")),
            },
            "time": {
                "type": "date",
                "ignore_malformed": True,
                "format": cls._convert_date_format(field.get("format")),
            },
            "object": {
                "properties": cls._update_properties(
                    {}, subschema, prefix + field["name"] + "."
                )
                if enabled
                else {},
                "enabled": enabled,
                "dynamic": False,
            },
        }[schema_type]
        return prop

    @classmethod
    def _convert_field(cls, field, prefix):
        schema_type = field["type"]
        if schema_type == "array":
            field = copy(field)
            try:
                field["type"] = field["es:itemType"]
            except KeyError:
                raise ValueError("Must define es:itemType for array fields")
            return cls._convert_field(field, prefix)

        prop = cls._convert_type(schema_type, field, prefix)
        return field["name"], prop

    @classmethod
    def _update_properties(cls, properties, schema, prefix=""):
        fields = schema["fields"]
        properties.update(dict(cls._convert_field(f, prefix) for f in fields))
        return properties

    def generate_from_schema(self, schema):
        properties = {}
        self._mapping["properties"] = properties
        self._update_properties(properties, schema)

    def get_mapping(self):
        return self._mapping
