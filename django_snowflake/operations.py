from django.conf import settings
from django.db.backends.base.operations import BaseDatabaseOperations


class DatabaseOperations(BaseDatabaseOperations):
    def quote_name(self, name):
        return '"%s"' % name.replace('.', '"."')

    def _convert_field_to_tz(self, field_name, tzname):
        if settings.USE_TZ:
            field_name = "CONVERT_TIMEZONE('UTC', '%s', %s)" % (tzname, field_name)
        return field_name

    def datetime_extract_sql(self, lookup_type, field_name, tzname):
        field_name = self._convert_field_to_tz(field_name, tzname)
        return self.date_extract_sql(lookup_type, field_name)

    def date_extract_sql(self, lookup_type, field_name):
        return "EXTRACT(%s FROM %s)" % (lookup_type.upper(), field_name)
