Introduction
============

plone.app.contenttypes offers default content types for Plone based on Dexterity. This package is a replacement for Products.ATContenttypes.

It contains the same types as default Plone does:

 * Folder
 * Document
 * News item
 * File
 * Image
 * Link
 * Event (this will be replaced by plone.app.event in the future)
 * Collection (this is provided by plone.app.collection)

The main difference from a users perspective is that these types are extendable through-the-web. This means you can go to the control-panel (/@@dexterity-types) and add or remove fields and behaviors for the existing types.

The aim is to mimick the old default-types as closely as possible.


Compatability
-------------

plone.app.contenttypes works with Plone 4.2+


Installation
------------

Add this line in the eggs section of your ``buildout.cfg``::

    eggs=
        ...
        plone.app.contenttypes


You also have to pin the 2.x version of ``plone.app.collection`` to get the deterity-based collections instead of the Archetypes-based collection shipped since Plone 4.2. The lates version at the time of writing is 2.0b4 but you might want to check http://pypi.python.org/pypi/plone.app.collection if there is a new version::

    [versions]
    plone.app.collection = 2.0b4


Migration
---------

TODO

 * from default AT to p.a.c
 * from old p.a.c. to new p.a.c (add interfaces)
 * from ATEvent to plone.app.event
 * from old p.a.c.-event to plone.app.event
 * from ATTopic to DX-plone.app.collections
 * from AT-plone.app.collection to DX-plone.app.collections
 * pointers how to migrate content with schemaextenders yourself


How to create a new page with only Dexterity
--------------------------------------------

If you start from scratch you might want to use a special branch of Products.CMFPlone that is prepared to make use of plone.app.contenttypes. This way you get a brand new site with

Modify your buildout to automatically pull the branch::

    [buildout]
    extensions =
        mr.developer

    auto-checkout =
        Products.CMFPlone

    [sources]
    Products.CMFPlone = git https://github.com/plone/Products.CMFPlone.git branch=plip-12344-plone.app.contenttypes


Differences to Products.ATContentTypes
--------------------------------------

The image of the ```News Item``` is not a field on the contenttype but a behavior that can add a image to any contenttypes (similar to http://pypi.python.org/pypi/collective.contentleadimage)


Dependencies
------------

TODO


Design descisions
-----------------

TODO: classes/interfaces/xml


Information for Addon-Developers
--------------------------------

TODO
Differences to ATContentTypes Interfaces

How to:

  * extend the types ttw or with xml
  * export a extended CT into a package to overwrite the default
  * extend with behaviors
  * make types transateable

- Addon-Products that are known to work with p.a.c


.. note::

  For background information see the `initial discussion on the Plone developer
  mailinglist <http://plone.293351.n2.nabble.com/atcontenttypes-replacement-with-dexterity-td6751909.html>`_
  and the `Plone-Conference 2011 sprint documentation <http://piratepad.net/OkuEys2lgS>`_.

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

  * The organizers of the Plone-Conference 2011 in San Francisco for a great
    conference!
  * The organizers of the Wine-and-Beer-Sprint in Munich ans Capetown in January 2013
  * The creators of Dexterity
