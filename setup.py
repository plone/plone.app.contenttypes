from setuptools import setup, find_packages

version = '1.0b2-thorn1'

setup(name='plone.app.contenttypes',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
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
          'plone.app.dexterity',
          'plone.app.relationfield',
          'plone.formwidget.querystring',
          'plone.namedfile [blobs]',
          'plone.app.versioningbehavior',
          # -*- Extra requirements: -*-
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
