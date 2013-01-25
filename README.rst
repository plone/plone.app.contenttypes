Introduction
============

Dexterity-based default content types for Plone. This package is a drop-in replacement for Products.ATContenttypes.

plone.app.contenttypes provides default content-types (document, news item, file, etc.) that are extendable through-the-web. They aim to mimick the old default-types - the only change is that they are based on dexterity.

TOC
- compatability-information (which Plone-versions work)
- Install-intructions
- how to use the CMFPlone-branch
- link to PLIP
- Describe types
- Describe Behaviors
- Dependencies
- Design descisions (classes/interfaces/xml)
- info for addon-developers:
  - Differences to ATContentTypes Interfaces


- How to:
  - extend the types ttw or with xml
  - export a extended CT into a package to overwrite the default
  - extend with behaviors
  - make transateable

- Addon-Products that work with p.a.c
-

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
