from django.db.backends.base.introspection import BaseDatabaseIntrospection, TableInfo


class DatabaseIntrospection(BaseDatabaseIntrospection):
    
    def get_table_list(self, cursor):
        cursor.execute("SHOW TABLES")
        return [TableInfo(row[1], row[2]) for row in cursor.fetchall()]