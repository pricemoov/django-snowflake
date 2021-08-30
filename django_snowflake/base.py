from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError as WrappedDatabaseError, connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.utils.asyncio import async_unsafe

import snowflake.connector as Database

from .client import DatabaseClient                          # NOQA isort:skip
from .creation import DatabaseCreation                      # NOQA isort:skip
from .features import DatabaseFeatures                      # NOQA isort:skip
from .introspection import DatabaseIntrospection            # NOQA isort:skip
from .operations import DatabaseOperations                  # NOQA isort:skip
from .schema import DatabaseSchemaEditor                    # NOQA isort:skip


class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'snowflake'
    display_name = 'Snowflake'
    data_types = {
        'AutoField': 'INTEGER',
        'BigAutoField': 'BIGINT',
        'BinaryField': 'BINARY',
        'BooleanField': 'BOOLEAN',
        'CharField': 'VARCHAR(%(max_length)s)',
        'DateField': 'DATE',
        'DateTimeField': 'TIMESTAMP_TZ',
        'DecimalField': 'FLOAT',
        'DurationField': 'BIGINT',
        'FileField': 'VARCHAR(%(max_length)s)',
        'FilePathField': 'VARCHAR(%(max_length)s)',
        'FloatField': 'FLOAT',
        'IntegerField': 'INTEGER',
        'BigIntegerField': 'BIGINT',
        'IPAddressField': 'VARCHAR(15)',
        'GenericIPAddressField': 'VARCHAR(15)',
        'JSONField': 'VARCHAR',
        'NullBooleanField': 'BOOLEAN',
        'OneToOneField': 'INTEGER',
        'PositiveBigIntegerField': 'BIGINT',
        'PositiveIntegerField': 'INTEGER',
        'PositiveSmallIntegerField': 'INTEGER',
        'SlugField': 'VARCHAR(%(max_length)s)',
        'SmallAutoField': 'VARCHAR',
        'SmallIntegerField': 'VARCHAR',
        'TextField': 'VARCHAR',
        'TimeField': 'TIME',
        'UUIDField': 'VARCHAR(32)',
    }
    data_type_check_constraints = {
        'PositiveBigIntegerField': '"%(column)s" >= 0',
        'PositiveIntegerField': '"%(column)s" >= 0',
        'PositiveSmallIntegerField': '"%(column)s" >= 0',
    }
    operators = {
        'exact': '= %s',
        'iexact': '= UPPER %s',
        'contains': 'LIKE %s',
        'icontains': 'ILIKE %s',
        'regex': 'REGEXP %s',
        'iregex': 'REGEXP_LIKE(%s, i)',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': 'LIKE %s',
        'endswith': 'LIKE %s',
        'istartswith': 'LIKE UPPER(%s)',
        'iendswith': 'LIKE UPPER(%s)',
    }

    # The patterns below are used to generate SQL pattern lookup clauses when
    # the right-hand side of the lookup isn't a raw string (it might be an expression
    # or the result of a bilateral transformation).
    # In those cases, special characters for LIKE operators (e.g. \, *, _) should be
    # escaped on database side.
    #
    # Note: we use str.format() here for readability as '%' is used as a wildcard for
    # the LIKE operator.
    pattern_esc = r"REPLACE(REPLACE(REPLACE({}, '\', '\\'), '%%', '\%%'), '_', '\_')"
    pattern_ops = {
        'contains': "LIKE '%%' || {} || '%%'",
        'icontains': "LIKE '%%' || UPPER({}) || '%%'",
        'startswith': "LIKE {} || '%%'",
        'istartswith': "LIKE UPPER({}) || '%%'",
        'endswith': "LIKE '%%' || {}",
        'iendswith': "LIKE '%%' || UPPER({})",
    }

    Database = Database
    SchemaEditorClass = DatabaseSchemaEditor
    # Classes instantiated in __init__().
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations

    def get_connection_params(self):
        settings_dict = self.settings_dict

        conn_params = {'session_parameters': {}}
        if settings_dict['USER']:
            conn_params['user'] = settings_dict['USER']
        if settings_dict['PASSWORD']:
            conn_params['password'] = settings_dict['PASSWORD']
        if settings_dict['ACCOUNT']:
            conn_params['account'] = settings_dict['ACCOUNT']
        if settings_dict['WAREHOUSE']:
            conn_params['warehouse'] = settings_dict['WAREHOUSE']
        if settings_dict['DATABASE']:
            conn_params['database'] = settings_dict['DATABASE']
        if settings_dict['SCHEMA']:
            conn_params['schema'] = settings_dict['SCHEMA']
        if settings_dict['ROLE']:
            conn_params['session_parameters']['role'] = settings_dict['ROLE']

        return conn_params

    @async_unsafe
    def get_new_connection(self, conn_params):
        connection = Database.connect(**conn_params)
        return connection

    def init_connection_state(self):
        pass

    @async_unsafe
    def create_cursor(self, name=None):
        cursor = self.connection.cursor()
        return cursor

    def _rollback(self):
        try:
            BaseDatabaseWrapper._rollback(self)
        except Database.NotSupportedError:
            pass

    def _set_autocommit(self, autocommit):
        with self.wrap_database_errors:
            self.connection.autocommit(autocommit)

    def is_usable(self):
        return False # TODO: We should be able to reuse connections somehow
