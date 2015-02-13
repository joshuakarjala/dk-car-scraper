#!/usr/bin/env python
from setuptools import setup, find_packages

DESCRIPTION = "A python module which returns details about a Danish car from its license plate number"

LONG_DESCRIPTION = open('README.rst').read()

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

INSTALL_REQUIRES = ['requests', 'beautifulsoup4']
try:
    import importlib
except ImportError:
    INSTALL_REQUIRES.append('importlib')

tests_require = [
    'requests>=1.2',
    'beautifulsoup4'
]

setup(
    name='dk-car-scraper',
    version='1.0.8',
    packages=find_packages(exclude=[]),
    author='Joshua Karjala-Svenden',
    author_email='joshua@fluxuries.com',
    url='https://github.com/joshuakarjala/dk-car-scraper/',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    # tests_require=tests_require,
    # extras_require={'test': tests_require},
    # test_suite='runtests.runtests',
    #include_package_data=True,
)
