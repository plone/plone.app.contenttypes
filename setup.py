from setuptools import find_packages
from setuptools import setup

import os


version = "3.0.0a13"


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = read("README.rst") + "\n\n" + read("CHANGES.rst")


setup(
    name="plone.app.contenttypes",
    version=version,
    description="Default content types for Plone based on Dexterity",
    long_description=long_description,
    # Get more strings from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="plone content types dexterity",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://github.com/plone/plone.app.contenttypes",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "plone.app.contentmenu",
        "plone.app.event >= 2.0",
        "plone.app.dexterity >= 2.0.7",  # has a fix for INameFromFilename
        "plone.app.linkintegrity",
        "plone.app.querystring >= 1.2.2",  # custom_query support
        "plone.dexterity >= 2.2.1",  # behaviors can provide primaryfields
        "plone.app.relationfield",
        "plone.namedfile >= 4.2.0",
        "plone.app.versioningbehavior",
        "plone.app.vocabularies > 4.1.2",
        "plone.app.lockingbehavior",
        "plone.behavior >= 1.3.0",
        "pytz",
        "plone.app.z3cform>=1.1.0",
        "zope.deprecation",
    ],
    extras_require={
        "test": [
            "lxml",
            "plone.app.robotframework [debug] > 0.9.8",  # create image and file content for Image, File and News Item if not given.  # noqa
            "plone.app.testing [robot] >= 4.2.4",  # we need ROBOT_TEST_LEVEL
        ],
    },
)
