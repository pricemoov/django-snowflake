from django.db.backends.base.introspection import BaseDatabaseIntrospection, TableInfo


class DatabaseIntrospection(BaseDatabaseIntrospection):
    
    def get_table_list(self, cursor):
        cursor.execute("SHOW TABLES")
        tables = [TableInfo(row[1], "t") for row in cursor.fetchall()]
        cursor.execute("SHOW VIEWS")
        views = [TableInfo(row[1], "v") for row in cursor.fetchall()]
        return tables + views
