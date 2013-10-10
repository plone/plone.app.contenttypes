from setuptools import setup, find_packages

version = '1.0'

long_description = open("README.rst").read() + "\n" + \
    open("CHANGES.rst").read()

setup(name='plone.app.contenttypes',
      version=version,
      description="Default content types for Plone based on Dexterity",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Development Status :: 4 - Beta",
          "Framework :: Plone",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
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
          'plone.app.event [dexterity]',
          'plone.app.dexterity>=2.0.7',  # has a fix for INameFromFilename
          'plone.app.relationfield',
          'plone.formwidget.querystring',
          'plone.namedfile [blobs]',
          'plone.app.versioningbehavior',
      ],
      extras_require={
          'test': [
              'archetypes.schemaextender',
              'lxml',
              'plone.app.robotframework',
              'plone.app.testing[robot]',
              'Products.ATContentTypes',
              'Products.contentmigration',
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
