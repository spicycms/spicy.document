"""spicy.document"""
from importlib import import_module
from setuptools import setup, find_packages


version = import_module('src').__version__
LONG_DESCRIPTION = """
spicy.document package
"""


def long_description():
    """Return long description from README.rst if it's present
    because it doesn't get installed."""
    try:
        return open('README.rst').read()
    except IOError:
        return LONG_DESCRIPTION


setup(
    name='spicy.document',
    version=version,
    author='Zolotarev Alexander',
    author_email='megabogus84@gmail.com',
    description='Spicy Document',
    license='BSD',
    keywords='django, cms',
    url='',
    packages=find_packages('src'),
    package_dir={
        '': 'src'
    },
    include_package_data=True,
    zip_safe=False,
    long_description=long_description(),
    namespace_packages=['spicy', ],
    dependency_links=[
        'git+https://github.com/django-ckeditor/django-ckeditor#egg=ckeditor',
    ],
    install_requires=[
        'ckeditor',
    ],

    classifiers=[
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Topic :: Internet',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
