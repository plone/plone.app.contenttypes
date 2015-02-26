from setuptools import setup, find_packages

import os

version = '1.1b4.dev0'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('docs', 'README.rst') + \
    read('docs', 'CHANGES.rst')

setup(name='plone.app.contenttypes',
      version=version,
      description="Default content types for Plone based on Dexterity",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Development Status :: 4 - Beta",
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
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
          'plone.app.event [dexterity]',  # You have to pin this to the desired version
          'plone.app.dexterity < 2.1.0',  # before Plone 5
          'plone.app.querystring >= 1.2.2',  # custom_query support
          'plone.dexterity >= 2.2.1',  # behaviors can provide primaryfields
          'plone.formwidget.querystring',
          'plone.app.relationfield',
          'plone.namedfile [blobs]',
          'plone.app.versioningbehavior',
          'pytz',
          'Products.CMFQuickInstallerTool >= 3.0.7',  # allow blacklisting steps
          'Products.GenericSetup >= 1.7.5',  # allow blacklisting steps
      ],
      extras_require={
          'test': [
              'archetypes.schemaextender',
              'lxml',
              'plone.app.robotframework [debug, reload] > 0.9.8',  # create image and file content for Image, File and News Item if not given.  # noqa
              'plone.app.testing [robot] >= 4.2.4',  # we need ROBOT_TEST_LEVEL
              # 'plone.dexterity >= 2.3.0',  # fixes setting default values # NOT RELEASED YET. # noqa
              'Products.ATContentTypes',
              'Products.contentmigration >= 2.1.8.dev0',
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
