from pathlib import Path

from setuptools import find_packages, setup

setup(
    name='bustawin-sqlalchemy-tutorial',
    version='0.2',
    url='https://github.com/bustawin/sqlalchemy-tutorial',
    project_urls={
        'Documentation': 'http://bustawin.com',
        'Code': 'https://github.com/bustawin/sqlalchemy-tutorial',
        'Issue tracker': 'https://github.com/bustawin/sqlalchemy-tutorial/issues'
    },
    license='GPL-3.0',
    author='Xavier Bustamante Talavera',
    author_email='xavier@bustawin.com',
    description='A SQLAlchemy tutorial, by example',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    long_description=Path('README.rst').read_text('utf8'),
    install_requires=[
        'flask==1.1',
        'sqlalchemy-citext',
        'sqlalchemy-utils[password, color, phone]',
        'Flask-SQLAlchemy',
        'psycopg2-binary==2.8.3',
        'sqlalchemy',
        'sqla-psql-search'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
