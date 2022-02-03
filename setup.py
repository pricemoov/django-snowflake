from setuptools import setup, find_packages

setup(
    name='django-snowflake',

    version='1.0.2',

    description='A backend for Django and Snowflake',

    url='',
    author='',
    author_email='',

    license='BSD',

    classifiers=[],

    keywords='django snowflake',
    packages=find_packages(exclude=['tests']),

    install_requires=['Django', 'snowflake-connector-python'],

    extras_require={},
)