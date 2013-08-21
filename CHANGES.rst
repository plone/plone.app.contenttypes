Changelog
=========

1.0rc1 (unreleased)
-------------------

- Remove dependency on plone.app.referenceablebehavior, as it depends on
  Products.Archetypes which installs the uid_catalog.
  [thet]

- make collection syndicatable
  [vangheem]

- Include the migration module not only when Products.ATContentTypes is
  installed but also archetypes.schemaextender. The schemaextender might not
  always be available.
  [thet]

- Add fulltext search of file objects.
  [do3cc]

- Fix link_redirect_view: Use index instead of template class var to
  let customization by ZCML of the template
  [toutpt]

1.0b2 (2013-05-31)
------------------

- Fix translations to the plone domain, and some translations match existing
  translations in the plone domain. (ported from plone.app.collection)
  [bosim]

- Fix atct_album_view and don't use atctListAlbum.py
  [pbauer]

- Add constrains for content create with the Content profile
  [ericof]

- Add SearchableText indexer to Folder content type
  [ericof]

- Fix atct_album_view
  [pbauer]

- Removed dependency for collective.dexteritydiff since its features were
  merged into Products.CMFDiffTool
  [pbauer]

- Add test for behavior table_of_contents
  [pbauer]

- Add migration for blobnewsitems as proposed in
  https://github.com/plone/plone.app.blob/pull/2
  [pbauer]

- Require cmf.ManagePortal for migration
  [pbauer]

- Always migrate files and images to blob (fixes #26)
  [pbauer]

- Add table of contents-behavior for documents
  [pbauer]

- Add versioning-behavior and it's dependencies
  [pbauer]

- Remove image_view_fullscreen from the display-dropdown
  [pbauer]

- Enable selecting addable types on folders by default
  [pbauer]

- Fix reference-migrations if some objects were not migrated
  [pbauer]

- Keep the order references when migrating
  [pabo3000]

- Move templates into their own folder
  [pbauer]

- Moved migration related code to specific module
  [gborelli]

- Added migration Collection from app.collection to app.contenttypes
  [kroman0]

- Add missing ``i18n:attributes`` to 'Edit' and 'View' actions of File type.
  [saily]

- Bind 'View' action to ``${object_url}/view`` instead of
  ``${object_url}`` as in ATCT for File and Image type.
  [saily]

- Fixed installation of p.a.relationfield together with p.a.contenttypes.
  [kroman0]

- Fixed creating aggregator of events on creating Plone site.
  [kroman0]

- Added titles for menuitems.
  [kroman0]

- Hide uninstall profile from @@plone-addsite.
  [kroman0]

- Fix 'ImportError: cannot import name Counter' for Python 2.6.
  http://github.com/plone/plone.app.contenttypes/issues/19
  [timo]

- Move XML schema definitions to schema folder.
  [timo]

- Prevent the importContent step from being run over and over again.
  [pysailor]

- Add build status image.
  [saily]

- Merge plone.app.collection (Tag: 2.0b5) into plone.app.contenttypes.
  [timo]

- Refactor p.a.collection robot framework tests
  [timo]


1.0b1 (2013-01-27)
------------------

- Added mime type icon for file.
  [loechel]

- Lead image behavior added.
  [timo]

- Make NewsItem use the lead image behavior.
  [timo]

- SearchableText indexes added.
  [reinhardt]

- Set the text of front-page when creating a new Plone
  [pbauer]

- Robot framework test added.
  [Gomez]


1.0a2 (unreleased)
------------------

- Move all templates from skins to browser views.
  [timo]

- User custom base classes for all content types.
  [timo]

- Migration view (@@fix_base_classes) added to migrate content objects that
  were created with version 1.0a1.
  [timo]

- Mime Type Icon added for File View [loechel]


1.0a1 (unreleased)
------------------

- Initial release
