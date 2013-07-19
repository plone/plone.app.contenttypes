from setuptools import setup, find_packages

version = '1.0rc1dev'

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
          'plone.app.dexterity>=2.0.7',  # has a fix for INameFromFilename
          'plone.app.relationfield',
          'plone.formwidget.querystring',
          'plone.namedfile [blobs]',
          'plone.app.versioningbehavior>=1.1.1',  # important bugfix
          'plone.app.referenceablebehavior',
      ],
      extras_require={
          'test': [
              'lxml',
              'plone.app.testing[robot]',
              'plone.app.robotframework',
              'Products.ATContentTypes',
              'Products.contentmigration',
          ],
          'migrate_atct': [
              'Products.ATContentTypes',
              'Products.contentmigration',
              'plone.app.collection',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
