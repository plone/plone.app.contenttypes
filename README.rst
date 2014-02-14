.. contents::

Introduction
============

.. image:: http://jenkins.plone.org/job/plone.app.contenttypes/badge/icon

plone.app.contenttypes offers default content types for Plone based on Dexterity. This package replaces ``Products.ATContenttypes`` and will provide the default-types in Plone 5.

It contains the following types:

* Folder
* Document
* News item
* File
* Image
* Link
* Event (Using behaviors from plone.app.event)
* Collection (this already replaces plone.app.collection which is no longer needed then)

The main difference from a users perspective is that these types are extendable through-the-web. This means you can add or remove fields and behaviors using the control-panel "Dexterity Content Types" (``/@@dexterity-types``).

The aim is to mimick the default-types as closely as possible.

plone.app.contenttypes has been merged into the Plone 5.0 branch and will be shipped with the next Plone release: https://dev.plone.org/ticket/12344

**Warning: Using plone.app.contenttypes on a site with existing content requires migrating the sites content. Please see the chapter "Migration". It can be used on a new site without problems.**

Compatability
=============

plone.app.contenttypes works with Plone 4.1+


Installation
============

Add this line in the eggs section of your ``buildout.cfg``::

    eggs =
        ...
        plone.app.contenttypes

If you have a mixed Plone site with Archetypes content and dexterity content use the extra requirement::

    ``plone.app.contenttypes ['atrefs']``


Installation as a dependency from another product
-------------------------------------------------

If you want to add plone.app.contenttypes as a dependency from another products use the profile ``plone-content`` in your ``metadata.xml`` to have Plone populate a new site with DX-based default-content. ::

    <metadata>
      <version>1</version>
        <dependencies>
            <dependency>profile-plone.app.contenttypes:plone-content</dependency>
        </dependencies>
    </metadata>

If you use the profile ``default`` then the default-content in new sites will still be Archetypes-based. You'll then have to migrate that content using the migration-form ``@@atct_migrator`` or delete it by hand.


What happens to existing content?
---------------------------------

If you install plone.app.contenttypes on a fresh site (i.e. when no content has been edited or added) the existing default-content will be replaced by dexterity-content to make sure it is still editable.

If you install plone.app.contenttypes in a existing site all Archetypes-based content of the default Types still exists and can be viewed but can't be edited. On installation plone.app.contenttypes removes the type-definitions for the old default-types like this::

    <object name="Document" remove="True" />

To make this content editable egain you need to migrate it to Dexterity (please see the section on migration) or uninstall plone.app.contenttypes.

Archetypes-based content provided by add-ons like Products.PloneFormGen will still work since only the default-types are replaced.


Uninstalling
------------

To remove plone.app.contenttypes and return full functionality to old content and restore the AT-based default-types you have to install the import step "Types Tool" of the current base profile. Follow the following steps:

* in the ZMI navigate to portal_setup and the tab "import"
* in "Select Profile or Snapshot" leave "Current base profile (<Name of your Plonesite>)" selected. This is usually Products.CMFPlone
* select the Types Tool (usually Step 44)
* click "import selected steps"

Any content you created based on plone.app.contenttypes will not be editable until you reinstall plone.app.contenttypes.


Migration
=========

To migrate your existing content from Archetypes to Dexterity use the form at ``/@@atct_migrator``.

plone.app.contenttypes includes migrations for the following use-cases:

* from default Archetypes-based types to plone.app.contenttypes
* from older versions of plone.app.contenttypes to current versions
* from old plone.app.contenttypes-event to DX-plone.app.event
* from AT-plone.app.event to DX-plone.app.event
* from atct ATEvent to DX-plone.app.event
* from AT-plone.app.collection to DX-plone.app.collections

Migrations that will be will come in future version:

* from ATTopic to DX-plone.app.collections

For migrations to work you need at least ``Products.contentmigration = 2.1.3`` (part of Plone since Plone 4.2.5) and ``plone.app.intid`` (part of Plone since Plone 4.1.0).


Migrating Archetypes-based content to plone.app.contenttypes
------------------------------------------------------------

plone.app.contenttypes can migrate the following types:

* Folder
* Document
* News item
* File
* Image
* Link
* Collection


Migrating content that is translated with LinguaPlone
-----------------------------------------------------

Since LinguaPlone does not support Dexterity you need to migrate from LinguaPlone to plone.app.multilingual (http://pypi.python.org/pypi/plone.app.multilingual). The migration from Products.LinguaPlone to plone.app.multilingual should happen **before** the migration from Archetypes to plone.app.contenttypes. For details on the migration see http://pypi.python.org/pypi/plone.app.multilingual#linguaplone-migration


Migrating from old versions of plone.app.contenttypes
-----------------------------------------------------

Before version 1.0a2 the content-items did not implement marker-interfaces.  They will break in newer versions since the views are now registered for these interfaces (e.g. ``plone.app.contenttypes.interfaces.IDocument``). To fix this you can call the view ``/@@fix_base_classes`` on your site-root.

Since plone.app.contenttypes 1.1, the Collection type uses the new Collection behavior and the Event type utilizes behaviors from `plone.app.event <http://pypi.python.org/pypi/plone.app.event>`_. In order to upgrade:

1) First run the default profile (``plone.app.contenttypes:default``) and
2) Then run the upgrade steps.


Migrating default-content that was extended with archetypes.schemaextender
--------------------------------------------------------------------------

The migration should warn you if any of your types are extended with archetypes.schemaextender. The data contained in these fields will be lost.

You need to implement a custom migration for your types and dexterity-behaviors for the functionality provided by the schemaextenders. This is an advanced development task and beyond the scope of this documentation.


Migrating custom content
------------------------

Custom content will not be changed by plone.app.contenttypes and should continue to work as expeced. However if you'd like to migrate your content-types to Dexterity (you'll have to create these types in Dexterity first) you might want to have a look at the code of plone.app.contenttypes.migration.migration.NewsItemMigrator as a blueprint.


Dependencies
============

* ``plone.app.dexterity``. Dexterity is shipped with Plone 4.3.x. Version pins for Dexterity are included in Plone 4.2.x. For Plone 4.1.x you need to pin the correct version for Dexterity in your buildout. See `Installing Dexterity on older versions of Plone <http://developer.plone.org/reference_manuals/external/plone.app.dexterity/install.html#installing-dexterity-on-older-versions-of-plone>`.

* ``plone.dexterity >= 2.2.1``. Olders version of plone.dexterity break the RRS-functionalisty in Plone because plone.app.contenttypes 1.1a2 uses behaviors for the Richtext-Fields.

* ``plone.app.event``.

Toubleshooting
==============

ValueError on installing
------------------------

When you try to install plone.app.contenttypes in a existing site you might get the following error::

      (...)
      Module Products.GenericSetup.utils, line 509, in _importBody
      Module Products.CMFCore.exportimport.typeinfo, line 60, in _importNode
      Module Products.GenericSetup.utils, line 730, in _initProperties
    ValueError: undefined property 'schema'

Before installing plone.app.contenttypes you have to reinstall plone.app.collection to update collections to the version that uses Dexterity.


Information for Addon-Developers
================================

The schemata of the types are set in xml-files using ``plone.supermodel``. This allows the types to be editable trough the web.

If you want to extend these types with code consider using behaviors.


Differences to Products.ATContentTypes
======================================

- The image of the News Item is not a field on the contenttype but a behavior that can add a image to any contenttypes (similar to http://pypi.python.org/pypi/collective.contentleadimage)
- All richtext-fields are also provided by a reuseable behavior.
- The functionality to transform (rotate and flip) images has been removed.
- There is no more field ``Location``. If you need georeferenceable consider using ``collective.geo.behaviour``
- The link on the image of the newsitem triggers an overlay
- The link-type now allows the of the variables ``${navigation_root_url}`` and ``${portal_url}`` to construct relative urls.



License
=======

GNU General Public License, version 2


Contributors
============

* Philip Bauer <bauer@starzel.de>
* Michael Mulich <michael.mulich@gmail.com>
* Timo Stollenwerk <contact@timostollenwerk.net>
* Peter Holzer <hpeter@agitator.com>
* Patrick Gerken <gerken@starzel.de>
* Steffen Lindner <lindner@starzel.de>
* Daniel Widerin <daniel@widerin.net>
* Jens Klein <jens@bluedynamics.com>
* Joscha Krutzki <joka@jokasis.de>
* Mathias Leimgruber <m.leimgruber@4teamwork.ch>
* Matthias Broquet <mbroquet@atreal.fr>
* Wolfgang Thomas <thomas@syslab.com>
* Bo Simonsen <bo@geekworld.dk>
* Andrew Mleczko <andrew@mleczko.net>
* Roel Bruggink <roel@jaroel.nl>
* Carsten Senger <senger@rehfisch.de>
* Rafael Oliveira <rafaelbco@gmail.com>
* Martin Opstad Reistadbakk <martin@blaastolen.com>
* Nathan Van Gheem <vangheem@gmail.com>
* Johannes Raggam <raggam-nl@adm.at>
* Jamie Lentin <jm@lentin.co.uk>
* Maurits van Rees <maurits@vanrees.org>
* David Glick <david@glicksoftware.com>
* Kees Hink <keeshink@gmail.com>
