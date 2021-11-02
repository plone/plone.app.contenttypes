.. contents::

.. image:: https://api.travis-ci.org/plone/plone.app.contenttypes.png?branch=master
    :target: http://travis-ci.org/plone/plone.app.contenttypes

.. image:: https://img.shields.io/pypi/dm/plone.app.contenttypes.svg
    :target: https://crate.io/packages/plone.app.contenttypes

.. image:: https://img.shields.io/pypi/v/plone.app.contenttypes.svg
    :target: https://crate.io/packages/plone.app.contenttypes

.. image:: https://img.shields.io/coveralls/plone/plone.app.contenttypes/master.svg
    :target: https://coveralls.io/github/plone/plone.app.contenttypes?branch=master


plone.app.contenttypes documentation
====================================


Introduction
------------

plone.app.contenttypes provides default content types for Plone based on Dexterity.

It contains the following types:

* Collection
* Document
* Event
* File
* Folder
* Image
* Link
* News Item

These types are editable and extendable through-the-web and you can add or remove fields and behaviors using the control-panel "Dexterity Content Types" (``/@@dexterity-types``).


Installation
------------

This package is included in Plone 6 and does not need installation.


Information for Addon-Developers
--------------------------------

Design decisions
^^^^^^^^^^^^^^^^

Schemata that are defined in XML-files using ``plone.supermodel`` allow editing those types' schemata through the web.
This is the case for the default File, Image and Link content types.
Schemata coming from behaviors, on the other hand, are not editable through the web.
The Document, News Item, Folder and Event default types, for example, have no schemata of their own at all, all their fields are provided by behaviors.


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

You could alternatively override the peroperty ``model_file`` of the type-definition with a empty string and use the property ``schema`` to provide your custom python-schema.

For more complex features you should always consider create custom behaviors and/or write your own content-types since that will most likely give you more flexibility and less problem when you want to upgrade to a newer version in the future.

For more information on custom dexterity-types and custom behaviors please read the `dexterity documentation <http://docs.plone.org/external/plone.app.dexterity/docs/>`_.


Changing the base class for existing objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you changed the base-class of existing types (e.g. because you changed them to be folderish) you also need to upgrade the base-class of existing objects. You can use the following form for this: ``@@base_class_migrator_form``.

This form lets you select classes to be updated and shows the number of objects for each class. This form can be used to change the base-class of any dexterity-types instances. The migration will also transform itemish content to folderish content if the new class is folderish. You might want to use the method ``plone.app.contenttypes.migration.dxmigration.migrate_base_class_to_new_class`` in your own upgrade-steps.


Source Code
===========

Contributors please read the document `Process for Plone core's development <https://docs.plone.org/develop/coredev/docs/index.html>`_

Sources are at the `Plone code repository hosted at Github <https://github.com/plone/plone.app.contenttypes>`_.


License
-------

GNU General Public License, version 2


Contributors
------------

* Philip Bauer <bauer@starzel.de>
* Michael Mulich <michael.mulich@gmail.com>
* Timo Stollenwerk <contact@timostollenwerk.net>
* Peter Holzer <peter.holzer@agitator.com>
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
* Gauthier Bastien <gauthier.bastien@imio.be>
* Andrea Cecchi <andrea.cecchi@redturtle.it>
* Bogdan Girman <bogdan.girman@gmail.com>
* Martin Opstad Reistadbakk <martin@blaastolen.com>
* Florent Michon <fmichon@atreal.fr>
* Hector Velarde <hector.velarde@gmail.com>
