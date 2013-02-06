.. contents::

Introduction
============

.. image:: https://jenkins.plone.org/job/plone-4.3-plone-app-contenttypes/badge/icon

plone.app.contenttypes offers default content types for Plone based on Dexterity. This package is a replacement for the types in Products.ATContenttypes.

**Warning: plone.app.contenttypes is best used when creating a new site from scratch. Using it on a site with existing content is not recommended if you don't know exactly what you're doing!**

It contains the same types as default Plone does:

* Folder
* Document
* News item
* File
* Image
* Link
* Event (this will be replaced by plone.app.event in the future)
* Collection (this is provided by plone.app.collection)

The main difference from a users perspective is that these types are extendable through-the-web. This means you can go to the control-panel (``.../@@dexterity-types``) and add or remove fields and behaviors for the existing types.

The aim is to mimick the old default-types as closely as possible, not to change or improve the content-creation experience for editors.


Compatability
=============

plone.app.contenttypes works with Plone 4.1+


Installation
============

Add this line in the eggs section of your ``buildout.cfg``::

    eggs =
        ...
        plone.app.contenttypes


You also have to pin the 2.x version of ``plone.app.collection`` to get the deterity-based collections instead of the Archetypes-based collection shipped since Plone 4.2. The latest version at the time of writing is 2.0b4 but you might want to check http://pypi.python.org/pypi/plone.app.collection if there is a new version::

    [versions]
    plone.app.collection = 2.0b4

Installing plone.app.contenttypes in an existing Plone-site
-----------------------------------------------------------

When you try to install plone.app.contenttypes in a existing site you will get the following error::

      (...)
      Module Products.GenericSetup.utils, line 509, in _importBody
      Module Products.CMFCore.exportimport.typeinfo, line 60, in _importNode
      Module Products.GenericSetup.utils, line 730, in _initProperties
    ValueError: undefined property 'schema'

Before installing plone.app.contenttypes you have to reinstall plone.app.collection to update collections to the version that uses Dexterity.


What happens to old content?
----------------------------

The old content still exists and can be visited but can't be edited any more. On installation plone.app.contenttypes removes the type-definitions for the old default-types like this::

    <object name="Document" remove="True" />

You can migrate the old items to the types provided by plone.app.contenttypes (see the section about migrations).

Uninstalling
------------

To remove plone.app.contenttypes and return full functionality to old content you have to restore the AT-based default-types.


Migration
=========

**Warning: Migrations are still in an very early stage and might break your site! plone.app.contenttypes is best used when creating a new site from scratch. Please proceed at your own risk!**

For migrations to work you need at least ``Products.contentmigration = 2.1.3`` which was not released at the time of writing.

This version plone.app.contenttypes comes with migrations for the following use-cases:

* from default Archetypes-based types to plone.app.contenttypes
* from older versions of plone.app.contenttypes to current versions

Migrations that will be will come in the future:

* from old p.a.c.-event to plone.app.event
* from default ATEvent to plone.app.event
* from ATTopic to DX-plone.app.collections
* from AT-plone.app.collection to DX-plone.app.collections


Migrating Archetypes-based content to plone.app.contenttypes
------------------------------------------------------------

plone.app.contenttypes can migrate the following types:

* Folder
* Document
* News item
* File
* Image
* Link

To migrate existing content go to ``/@@migrate_from_atct``.

TODO:

* disable linkintegrity
* LP
* Plone-Version older tan 4.1.x need ``plone.app.intid``


Migrating content that is translated with LinguaPlone
-----------------------------------------------------

**Warning: This use-case has not yet been thoroughly tested!***

Since LinguaPlone does not support Dexterity you need to migrate from LinguaPlone to plone.app.multilingual (http://pypi.python.org/pypi/plone.app.multilingual). The migration from Products.LinguaPlone to plone.app.multilingual should happen **before** the migration from Archetypes to plone.app.contenttypes. For details on the migration see http://pypi.python.org/pypi/plone.app.multilingual#linguaplone-migration


Migrating from old versions of plone.app.contenttypes
-----------------------------------------------------

Before version 1.0a2 the content-items did not implement marker-interfaces. They will break in newer versions since the views are now registered for these interfaces (e.g. ``plone.app.contenttypes.interfaces.IDocument`). To fix this you can call the view ``/@@fix_base_classes`` on your site-root.



Migrating content that was extended with archetypes.schemaextender
------------------------------------------------------------------

The migration should warn you if your typs are extended with archetypes.schemaextender. The data contained in these fields will be lost.


How to create a new page with only Dexterity
============================================

You have two options:

**1. By hand**

Installing plone.app.contenttypes remove the types automatically, you only have to remove the existing content (front-page, events, news, members).


**2. Automatically**

If you start from scratch you can want to try using a special branch of Products.CMFPlone that gives you the choice between Dexterity and Archetypes when creating a new site. This way you get a brand new site with

Modify your buildout to automatically pull the branch using mr.developer (http://pypi.python.org/pypi/mr.developer)::

    [buildout]
    extensions = mr.developer
    auto-checkout =
        Products.CMFPlone
        Products.ATContentTypes

    [sources]
    Products.CMFPlone = git https://github.com/plone/Products.CMFPlone.git branch=plip-12344-plone.app.contenttypes
    Products.ATContentTypes = git https://github.com/plone/Products.ATContentTypes.git branch=davisagli-optional-archetypes


Differences to Products.ATContentTypes
======================================

The image of the News Item is not a field on the contenttype but a behavior that can add a image to any contenttypes (similar to http://pypi.python.org/pypi/collective.contentleadimage)


Dependencies
============

* ``plone.app.dexterity``. Dexterity is shipped with Plone 4.3.x. Version pinns for Dexterity are included in Plone 4.2.x. For Plone 4.1.x you need to pinn the correct version for Dexterity in your buildout. See "Installing Dexterity on older versions of Plone" on http://plone.org/products/dexterity/documentation/how-to/install.

* ``plone.app.collection``.


Design descisions
-----------------

TODO


Information for Addon-Developers
--------------------------------

Differences to ATContentTypes Interfaces

How to:

* extend the types ttw or with xml ()
* export a extended CT into a package to overwrite the default
* extend with behaviors
* make types transateable

- Addon-Products that are known to work with p.a.c


.. note::

  For background information see the `initial discussion on the Plone developer
  mailinglist <http://plone.293351.n2.nabble.com/atcontenttypes-replacement-with-dexterity-td6751909.html>`_
  and the `Plone-Conference 2011 sprint documentation <http://piratepad.net/OkuEys2lgS>`_.

License
-------

GNU General Public License, version 2


Roadmap
-------


Contributors
------------

* Philip Bauer <bauer@starzel.de>
* Michael Mulich <michael.mulich@gmail.com>
* Timo Stollenwerk <contact@timostollenwerk.net>
* Peter Holzer <hpeter@agitator.com>
* Patrick Gerken
* Steffen Lindner

TODO: add all contributors


Thanks to
---------

* The organizers of the Plone-Conference 2011 in San Francisco for a great conference!
* The organizers of the Wine-and-Beer-Sprint in Munich and Capetown in January 2013
* The creators of Dexterity
