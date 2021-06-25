# django-snowflake

Read-only Snowflake database backend for django

## Usage

Add an entry to your `DATABASES` setting that uses `django_snowflake` as engine:

```python
DATABASES = {
    'snowflake_analytics': {
        'ENGINE': 'django_snowflake',
        'USER': 'my_db_user',
        'PASSWORD': 'my_password',
        'ACCOUNT': 'my_snowflake_Acc.eu-west1',
        'DATABASE': 'SNOWFLAKE_SAMPLE_DATA',
        'WAREHOUSE': 'WAREHOUSE_BACKEND',
    }
}
```

Modify wanted models `Meta` class with:

```python
class Customer(models.Model):
    C_CUSTKEY = models.IntegerField(primary_key=True)
    C_NAME = models.CharField(max_length=25)

    class Meta:
        managed = False
        db_table = 'SNOWFLAKE_SAMPLE_DATA.SCHEMA_1.CUSTOMER_TABLE'
```

Working operations:

```python
Customer.objects.all()
Customer.objects.all()[:100]
Customer.objects.all().count()

Customer.objects.get(C_CUSTKEY=1)
Customer.objects.filter(C_CUSTKEY__lte=10)
Customer.objects.filter(C_NAME__startwith='Custo')

Customer.objects.all().aggregate(Avg('C_CUSTKEY'))
#TODO Need more testing
```

## Next steps

Implements missing operations in operations.py using other SQL dialect as a base.
[Postgres operations can be found here] (https://github.com/django/django/blob/ca9872905559026af82000e46cde6f7dedc897b6/django/db/backends/postgresql/operations.py)
