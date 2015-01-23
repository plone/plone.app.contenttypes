.. contents::

.. image:: https://pypip.in/d/plone.app.contenttypes/badge.png
    :target: https://crate.io/packages/plone.app.contenttypes

.. image:: https://pypip.in/v/plone.app.contenttypes/badge.png
    :target: https://crate.io/packages/plone.app.contenttypes

.. image:: https://travis-ci.org/plone/plone.app.contenttypes.svg?branch=1.1.x
    :target: https://travis-ci.org/plone/plone.app.contenttypes


plone.app.contenttypes documentation
====================================

Introduction
------------


plone.app.contenttypes provides default content types for Plone based on Dexterity. It replaces ``Products.ATContentTypes`` and provides the default-types in Plone 5. It can be used as an add-on in Plone 4.x.

It contains the following types:

* Collection
* Document
* Event
* File
* Folder
* Image
* Link
* News Item

The main difference from a users perspective is that these types are extendable through-the-web. This means you can add or remove fields and behaviors using the control-panel "Dexterity Content Types" (``/@@dexterity-types``).

**Warning: Using plone.app.contenttypes on a site with existing Archetypes-based content requires migrating the sites content. Please see the chapter "Migration".**


Compatibility
-------------

Version 1.1b3 is tested with Plone 4.3.x. The versions of branch 1.1.x will stay compatible with Plone 4.3.x.

For support of Plone 4.1 and 4.2 please use version 1.0.x. Please note that they do not provide the full functionality.

The versions 1.2.x of the master-branch are compatible with Plone 5 and plone.app.widgets.


Installation
------------

This package is included in Plone 5 and does not need installation.

To use plone.app.contenttypes in Plone 4.x add this line in the eggs section of your ``buildout.cfg``

.. code:: ini

    eggs =
        ...
        plone.app.contenttypes

If you have a Plone site with mixed Archetypes and Dexterity content use the extra requirement ``atrefs``.

.. code:: ini

    eggs =
        ...
        plone.app.contenttypes [atrefs]

This will also install the package `plone.app.referenceablebehavior <https://pypi.python.org/pypi/plone.app.referenceablebehavior>`_ that allows you to reference dexterity-based content from archetypes-based content. You will have to enable the behavior ``plone.app.referenceablebehavior.referenceable.IReferenceable`` for all types that need to be referenced by Archetypes-content.


What happens to existing content?
---------------------------------

If you install plone.app.contenttypes in a existing site all Archetypes-based content of the default types still exists and can be viewed but can't be edited. On installation plone.app.contenttypes removes the type-definitions for the old default-types like this:

.. code:: xml

    <object name="Document" remove="True" />

They are then replaced by new Definitions:

.. code:: xml

    <object meta_type="Dexterity FTI" name="Document" />

To make the existing content editable again you need to migrate it to Dexterity (please see the section on migration) or uninstall plone.app.contenttypes (see the section on uninstalling).

Archetypes-based content provided by add-ons (e.g. Products.PloneFormGen) will still work since only the default-types are replaced.

If you install plone.app.contenttypes on a fresh site (i.e. when no content has been edited or added) the usual default-content (Events, News, Members...) will be created as dexterity-content.


Uninstalling
------------

Uninstalling the default-types is not supported in Plone 5. If you really want to switch back to Archetypes-based types you have to to the following:

* Go to the ZMI
* In portal_types delete the default-types
* In portal_setup navigate to the tab 'import', select the profile 'Archetypes Content Types for Plone' and install all step including dependencies.

Any content you created based on plone.app.contenttypes will no longer be editable until you reinstall plone.app.contenttypes.


Dependencies
------------

* ``plone.app.dexterity >= 2.0.7``. Dexterity is shipped with Plone 4.3.x. Version pinns for Dexterity are included in Plone 4.2.x. For Plone 4.1.x you need to pin the right version for Dexterity in your buildout. See `Installing Dexterity on older versions of Plone <http://docs.plone.org/external/plone.app.dexterity/docs/install.html#installing-dexterity-on-older-versions-of-plone>`_.

* ``plone.dexterity >= 2.2.1``. Olders version of plone.dexterity break the rss-views because plone.app.contenttypes uses behaviors for the richtext-fields.

* ``plone.app.event >= 1.1.4``. This provides the behaviors used for the event-type.

* ``plone.app.portlets >= 2.5a1``. In older version the event-portlet will not work with the new event-type.

These are the version-pinns for Plone 4.3.4:

.. code:: ini

    [buildout]
    versions = versions

    [versions]
    plone.app.event = 1.1.4

Plone 4.3.3 also needs ``plone.app.portlets = 2.5.2``

Plone-versions before 4.3.3 need to pinn more packages:

.. code:: ini

    [buildout]
    versions = versions

    [versions]
    plone.dexterity = 2.2.1
    plone.app.dexterity = 2.0.11
    plone.schemaeditor = 1.3.5
    plone.app.event = 1.1b1
    plone.app.portlets = 2.5.1

For migrations to work you need at least ``Products.contentmigration = 2.1.9`` and ``plone.app.intid`` (part of Plone since Plone 4.1.0).


Migration
---------

To migrate your existing content from Archetypes to Dexterity use the form at ``/@@atct_migrator``.


Migrating Archetypes-based content to plone.app.contenttypes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

plone.app.contenttypes can migrate the following archetypes-based default types:

* Document
* Event
* File
* Folder
* Image
* Link
* News Item
* Collection
* Topic (old Collections)

The following non-default types will also be migrated:

* The AT-based Event-type provided by plone.app.event
* The DX-based Event-type provided by plone.app.event
* The Event-type provided by plone.app.contenttypes until version 1.0
* News Items with blobs (provoded by https://github.com/plone/plone.app.blob/pull/2)
* Files and Images without blobs

The migration tries to keep most features (including portlets, comments, contentrules, local roles and local workflows).

**Warning:** Versions of content are not migrated. During migration you will lose all old revisions.


Migrating only certain types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is also a view ``/@@pac_installer`` that allows you to install plone.app.contenttypes without replacing those archetypes-types with the dexterity-types of which there are existing objects in the site. Afterwards it redirects to the migration-form and only the types that you chose to migrate are installed. This allows you to keep certain types as archetypes while migrating others to dexterity (for example if you did heavy customizations of these types and do not have the time to reimplement these features in dexterity.


Migrating Topics
^^^^^^^^^^^^^^^^

Topics are migrated to Collections. However, the old type Topic had support for Subtopics, a feature that does not exit in Collections. Subtopics are nested Topics that inherited search terms from their parents. Since Collections are not folderish (i.e. they cannot contain content) Subtopics cannot be migrated unless Collections are made folderish (i.e. that they can contain content). Also the feature that search terms can be inherited from parents does not exist for Collections.

The migration-form will warn you if you have subtopics in your site and your Collections are not folderish. You then have several options:

1. You can delete all Subtopics before migrating and achieve their functionality in another way (e.g. using eea.facetednavigation).
2. You can choose to not migrate Topics by not selecting them. This will keep your old Topics functional. You can still add new Collections.
3. You can modify Collections to be folderish or create your own folderish content-type.   That type would need a base-class that inherits from ``plone.dexterity.content.Container`` instead of ``plone.dexterity.content.Item``:

   .. code-block:: python

      from plone.app.contenttypes.behaviors.collection import ICollection
      from plone.dexterity.content import Container
      from zope.interface import implementer

      @implementer(ICollection)
      class FolderishCollection(Container):
          pass

   You can either use a new Collection type or simply modify the default type to use this new base-class by overriding the klass-attribute of the default Collection. To override add a ``Collection.xml`` in your own package:

   .. code-block:: xml

      <?xml version="1.0"?>
      <object name="Collection" meta_type="Dexterity FTI">
       <property name="klass">my.package.content.FolderishCollection</property>
      </object>

   If you really need it you could add the functionality to inherit search terms to your own folderish Collections by extending the behavior like in the example at https://github.com/plone/plone.app.contenttypes/commit/366cc1a911c81954645ec6aabce925df4a297c63


Migrating content that is translated with LinguaPlone
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since LinguaPlone does not support Dexterity you need to migrate from LinguaPlone to plone.app.multilingual (http://pypi.python.org/pypi/plone.app.multilingual). The migration from Products.LinguaPlone to plone.app.multilingual should happen **before** the migration from Archetypes to plone.app.contenttypes. For details on the migration see http://pypi.python.org/pypi/plone.app.multilingual#linguaplone-migration


Migrating from old versions of plone.app.contenttypes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before version 1.0a2 the content-items did not implement marker-interfaces. They will break in newer versions since the views are now registered for these interfaces (e.g. ``plone.app.contenttypes.interfaces.IDocument``). To fix this you can call the view ``/@@fix_base_classes`` on your site-root.

Since plone.app.contenttypes 1.1a1, the Collection type uses the new Collection behavior and the Event type utilizes behaviors from `plone.app.event <http://pypi.python.org/pypi/plone.app.event>`_. In order to upgrade:

1) First run the default profile (``plone.app.contenttypes:default``) or reinstall plone.app.contenttypes
2) Then run the upgrade steps.


Migrating default-content that was extended with archetypes.schemaextender
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The migration-form warns you if any of your old types were extended with aditional fields using archetypes.schemaextender. The data contained in these fields will be lost during migration (with the exception of images added with collective.contentleadimage).

To keep the data you would need to write a custom migration for your types dexterity-behaviors for the functionality provided by the schemaextenders. This is an advanced development task and beyond the scope of this documentation.


Migrating images created with collective.contentleadimage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`collective.contentleadimage <https://pypi.python.org/pypi/collective.contentleadimage/>`_ was a popular addon that allows you to add images to any content in your site by extending the default types. To make sure these images are kept during migration you have to enable the behavior "Lead Image" on all those types where you want to migrate images added using collective.contentleadimage.

The old types that use leadimages are listed in the navigation-form with the comment *"extended fields: 'leadImage', 'leadImage_caption'"*. The migration-form informs you which new types have the behavior enabled and which do not. Depending on the way you installed plone.app.contenttypes you might have to first install these types by (re-)installing plone.app.contenttypes.


Migrating custom content
^^^^^^^^^^^^^^^^^^^^^^^^

Custom content-types will not be touched by the migration plone.app.contenttypes and will continue to work as expected.

Future versions of plone.app.contenttypes will have with a form that allows you to migrate old custom Archetypes-content to Dexterity (you'll still have to create the Dexterity-types before migrating).

If you want to migrate your custom types to Dexterity before this feature is completed you might want to have a look at the code of plone.app.contenttypes.migration.migration.NewsItemMigrator as a blueprint for a migration.


Widgets
-------

When used in Plone 4.x plone.app.contenttypes uses the default z3c.form widgets. All widgets work as they used to with Archetypes except for the keywords-widget for which a simple linesfield is used.

It is recommended to use ``plone.app.widgets`` to switch to the widgets that will be used in Plone 5.


How to use with plone.app.widgets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO


How to override widgets
^^^^^^^^^^^^^^^^^^^^^^^^

To override the default keywords-widgets with a nicer widget you can use the package `collective.z3cform.widgets <https://pypi.python.org/pypi/collective.z3cform.widgets>`_.

Add ``collective.z3cform.widgets`` to your ``buildout`` and in your own package register the override in your ``configure.zcml``:

.. code:: xml

    <adapter factory=".subjects.SubjectsFieldWidget" />

Then add a file ``subjects.py``

.. code:: python

    # -*- coding: UTF-8 -*-
    from collective.z3cform.widgets.token_input_widget import TokenInputFieldWidget
    from plone.app.dexterity.behaviors.metadata import ICategorization
    from plone.app.z3cform.interfaces import IPloneFormLayer
    from z3c.form.interfaces import IFieldWidget
    from z3c.form.util import getSpecification
    from z3c.form.widget import FieldWidget
    from zope.component import adapter
    from zope.interface import implementer


    @adapter(getSpecification(ICategorization['subjects']), IPloneFormLayer)
    @implementer(IFieldWidget)
    def SubjectsFieldWidget(field, request):
        widget = FieldWidget(field, TokenInputFieldWidget(field, request))
        return widget

Once you install ``collective.z3cform.widgets`` in the quickinstaller, the new widget will then be used for all types.


Information for Addon-Developers
--------------------------------

Design decisions
^^^^^^^^^^^^^^^^

The schemata for the types File, Image and Link are defined in xml-files using ``plone.supermodel``. This allows the types to be editable trough the web. The types Document, News Item, Folder and Event have no schemata at all but only use behaviors to provide their fields.


Installation as a dependency from another product
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to add plone.app.contenttypes as a dependency from another products use the profile ``plone-content`` in your ``metadata.xml`` to have Plone populate a new site with DX-based default-content.

.. code:: xml

    <metadata>
      <version>1</version>
        <dependencies>
            <dependency>profile-plone.app.contenttypes:plone-content</dependency>
        </dependencies>
    </metadata>

If you use the profile ``default`` then the default-content in new sites will still be Archetypes-based. You'll then have to migrate that content using the migration-form ``@@atct_migrator`` or delete it by hand.


Using folderish types
^^^^^^^^^^^^^^^^^^^^^

At some point all default types will probably be folderish. If you want the default types to be folderish before that happens please look at https://pypi.python.org/pypi/collective.folderishtypes.


Changing the base class for existing objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you changed the base-class of existing types (e.g. because you changed them to be folderish) you also need to upgrade the base-class of existing objects. You can use the following form for this: ``@@base_class_migrator_form``.

This form lets you select classes to be updated and shows the number of objects for each class. This form can be used to change the base-class of any dexterity-types instances. The migration will also transform itemish content to folderish content if the new class is folderish. You might want to use the method ``plone.app.contenttypes.migration.dxmigration.migrate_base_class_to_new_class`` in your own upgrade-steps.


Extending the types
^^^^^^^^^^^^^^^^^^^

You have several options:

1. Extend the types through-the-web by adding new fields or behaviors in the types-controlpanel ``/@@dexterity-types``.

2. Extend the types with a custom type-profile that extends the existing profile with behaviors, or fields.

   You will first have to add the type to your ``[yourpackage]/profiles/default/types.xml``.

   .. code:: xml

    <?xml version="1.0"?>
    <object name="portal_types" meta_type="Plone Types Tool">
      <object name="Folder" meta_type="Dexterity FTI" />
    </object>

   Here is an example that enables the image-behavior for Folders in ``[yourpackage]/profiles/default/types/Folder.xml``:

   .. code:: xml

    <?xml version="1.0"?>
    <object name="Folder" meta_type="Dexterity FTI">
     <property name="behaviors" purge="False">
      <element value="plone.app.contenttypes.behaviors.leadimage.ILeadImage"/>
     </property>
    </object>

   By adding a schema-definition to the profile you can add fields.

   .. code:: xml

    <?xml version="1.0"?>
    <object name="Folder" meta_type="Dexterity FTI">
     <property name="model_file">your.package.content:folder.xml</property>
     <property name="behaviors" purge="False">
      <element value="plone.app.contenttypes.behaviors.leadimage.ILeadImage"/>
     </property>
    </object>

   Put the schema-xml in ``your/package/content/folder.xml`` (the folder ``content`` needs a ``__init__.py``)

   .. code:: xml

    <model xmlns:security="http://namespaces.plone.org/supermodel/security"
           xmlns:marshal="http://namespaces.plone.org/supermodel/marshal"
           xmlns:form="http://namespaces.plone.org/supermodel/form"
           xmlns="http://namespaces.plone.org/supermodel/schema">
      <schema>
        <field name="teaser_title" type="zope.schema.TextLine">
          <description/>
          <required>False</required>
          <title>Teaser title</title>
        </field>
        <field name="teaser_subtitle" type="zope.schema.Text">
          <description/>
          <required>False</required>
          <title>Teaser subtitle</title>
        </field>
        <field name="teaser_details" type="plone.app.textfield.RichText">
          <description/>
          <required>False</required>
          <title>Teaser details</title>
        </field>
      </schema>
    </model>

For more complex features you should create custom behaviors and/or write your own content-types. For more information on creating custom dexterity-types or custom behaviors to extend these types with read the `dexterity documentation <http://docs.plone.org/external/plone.app.dexterity/docs/>`_.


Reordering fields provided by behaviors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO


Differences to Products.ATContentTypes
--------------------------------------

- The image of the News Item is not a field on the contenttype but a behavior that can add a image to any contenttypes (similar to http://pypi.python.org/pypi/collective.contentleadimage)
- All richtext-fields are also provided by a reuseable behavior.
- The functionality to transform (rotate and flip) images has been removed.
- There is no more field ``Location``. If you need georeferenceable consider using ``collective.geo.behaviour``
- The link on the image of the newsitem triggers an overlay
- The link-type now allows the of the variables ``${navigation_root_url}`` and ``${portal_url}`` to construct relative urls.
- The keywords-widget is not implemented and is replaced by a simple lines-widget unless you override it or use plone.app.widgets. Please see the section on widgets.


Toubleshooting
--------------

Please report issues in the bugtracker at https://github.com/plone/plone.app.contenttypes/issues.

ValueError on installing
^^^^^^^^^^^^^^^^^^^^^^^^^

When you try to install plone.app.contenttypes < 1.1a1 in a existing site you might get the following error::

      (...)
      Module Products.GenericSetup.utils, line 509, in _importBody
      Module Products.CMFCore.exportimport.typeinfo, line 60, in _importNode
      Module Products.GenericSetup.utils, line 730, in _initProperties
    ValueError: undefined property 'schema'

Before installing plone.app.contenttypes you have to reinstall plone.app.collection to update collections to the version that uses Dexterity.


Branches
--------

The master-branch supports Plone 5 only. From this 1.2.x-releases will be cut.

The 1.1.x-branch supports Plone 4.3.x. From this 1.1.x-releases will be cut.


License
-------

GNU General Public License, version 2


Contributors
------------

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
* Roman Kozlovskyi <krzroman@gmail.com>
* Bogdan Girman <bogdan.girman@gmail.com>
* Martin Opstad Reistadbakk <martin@blaastolen.com>
