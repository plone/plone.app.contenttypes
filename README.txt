Introduction
============

Dexterity-based default content types for Plone. This package is a drop-in
replacement for Products.ATContenttypes.  

.. note::

  This package will probably never become a part of Plone core. The archetypes
  content types in Plone will most likely be replaced by a generic Deco type in 
  the future. Deco is the new page composition tool that will probably become
  part of Plone 5. 

plone.app.contenttypes provides some default content-types that are extendable
through-the-web. They aim to mimick the old default-types - the only change is 
that they are based on dexterity. 

It provides neither marker-interfaces nor python-classes for the content-types 
because this ensures that they are editable through-the-web. The views are 
equally boring and only use skin-templates based on the original templates.  

.. note::

  For background information see the `initial discussion on the Plone developer 
  mailinglist <http://plone.293351.n2.nabble.com/atcontenttypes-replacement-with-dexterity-td6751909.html>`_
  and the `Plone-Conference 2011 sprint documentation <http://piratepad.net/OkuEys2lgS>`_.
  
Credits::

  * Philip Bauer <bauer@starzel.de>
  * Michael Mulich <michael.mulich@gmail.com>
  * Timo Stollenwerk <contact@timostollenwerk.net>
  * Peter Holzer <hpeter@agitator.com>

Thanks to::

  * The organizers of the Plone-Conference 2011 in San Francisco for a great 
    conference!  
