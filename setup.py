# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


version = '1.4.12'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = \
    read('README.rst') + '\n\n' + \
    read('CHANGES.rst')


setup(name='plone.app.contenttypes',
      version=version,
      description="Default content types for Plone based on Dexterity",
      long_description=long_description,
      # Get more strings from
      # https://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Development Status :: 6 - Mature",
          "Framework :: Plone",
          "Framework :: Plone :: 5.1",
          "Framework :: Plone :: 5.2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
      ],
      keywords='plone content types dexterity',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://github.com/plone/plone.app.contenttypes',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'plone.app.contentmenu',
          'plone.app.event >= 2.0a4',
          'plone.app.dexterity >= 2.0.7',  # has a fix for INameFromFilename
          'plone.app.linkintegrity',
          'plone.app.querystring >= 1.2.2',  # custom_query support
          'plone.dexterity >= 2.2.1',  # behaviors can provide primaryfields
          'plone.app.relationfield',
          'plone.namedfile [blobs] >= 4.2.0',
          'plone.app.versioningbehavior',
          'plone.app.lockingbehavior',
          'pytz',
          'plone.app.z3cform>=1.1.0.dev0',
          'six',
          'zope.deprecation',
      ],
      extras_require={
          'test': [
              'lxml',
              'plone.app.robotframework [debug] > 0.9.8',  # create image and file content for Image, File and News Item if not given.  # noqa
              'plone.app.testing [robot] >= 4.2.4',  # we need ROBOT_TEST_LEVEL
          ],
          'archetypes': [
              'archetypes.schemaextender',
              'Products.ATContentTypes',
              'Products.contentmigration >= 2.1.8.dev0',
              'plone.app.referenceablebehavior',
          ],
          'atrefs': [
              'plone.app.referenceablebehavior',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
