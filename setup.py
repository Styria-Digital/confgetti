"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

try:
    # Gitlab-ci will have defined $STYRIA_EXTRA_INDEX_URL ENV variable.
    STYRIA_EXTRA_INDEX_URL = '{}/packages/'.format(
        os.environ['STYRIA_EXTRA_INDEX_URL'])
except KeyError:
    # Locally we have stored information about our pypi server in pip.conf,
    # and tox will read it.
    STYRIA_EXTRA_INDEX_URL = ''

setup(
    name="confgetti",

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version="0.1.0",

    description="Package for getting configuration variables from remote configuration server and/or environment",
    long_description=long_description,

    # The project's main homepage.
    url='https://gl.sds.rocks/gdni/confgetti',

    # Author details
    author='Styria Digital',
    author_email='cms@styria.hr',

    # Choose your license
    license='Proprietary',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Content publishers',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Web',

        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: Other/Proprietary License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3'
    ],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'demos']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'python-consul',
        'voluptuous'
    ],

    dependency_links=[
        STYRIA_EXTRA_INDEX_URL
    ],

    setup_requires=[
        'pytest-runner',
    ],

    tests_require=[
        'pytest', 'pytest-cov', 'pytest-cache', 'pytest-sugar'
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': [
            'bumpversion'
        ],
        'test': [
            'responses',
            'faker',
            'testfixtures',
            'mock',
            'pytest>=3.0',
            'pytest-cov',
            'pytest-cache',
            'pytest-sugar',
            'pytest-runner',
            'tox'
        ],
        'docs': [
            'sphinx',
            'sphinx_rtd_theme'
        ]
    }
)
