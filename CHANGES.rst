Changelog
=========

1.1a2 (unreleased)
------------------

- Only attempt transforming files if valid content type
  [vangheem]

- Make the collection behavior aware of INavigationRoot. Fixes #98
  [rafaelbco]


1.1a1 (2013-11-22)
------------------

- Event content migration for Products.ATContentTypes ATEvent,
  plone.app.event's ATEvent and Dexterity example type and
  plone.app.contenttypes 1.0 Event to plone.app.contenttypes 1.1
  Event based on plone.app.event's Dexterity behaviors.
  [lentinj]

- Collection: get ``querybuilderresults`` view instead of using the
  ``QueryBuilder`` class directly.
  [maurits]

- Fix migration restoreReferencesOrder removes references
  [joka]

- Enable summary_view and all_content views for content types that
  have the collection behavior enabled.  Define collection_view for
  those types so you can view the results.  These simply show the
  results.  The normal view of such a type will just show all fields
  in the usual dexterity way.
  [maurits, kaselis]

- Add customViewFields to the Collection behavior.  This was available
  on old collections too.
  [maurits, kaselis]

- Change Collection to use a behavior.  Issue #65.
  [maurits, kaselis]

- Improved test coverage for test_migration
  [joka]

- Add tests for vocabularies used for the migration
  [maethu]

- Add migration-form /@@atct_migrate based on initial work by gborelli
  [pbauer, tiazma]

- Add ATBlob tests and use migration layer for test_migration
  [joka]

- Integrate plone.app.event.
  [thet]


1.0 (2013-10-08)
----------------

- Remove AT content and create DX-content when installing in a fresh site.
  [pbauer]

- Remove obsolete extra 'migrate_atct'.
  [pbauer]

- Add link and popup to the image of News Items.
  [pbauer]

- Use the default profile title for the example content profile.
  [timo]

- Unicode is expected, but ``obj.title`` and/or ``obj.description`` can be
  still be None in SearchableText indexer.
  [saily]


1.0rc1 (2013-09-24)
-------------------

- Implement a tearDownPloneSite method in testing.py to prevent test
  isolation problems.
  [timo]

- Its possible to upload non-image data into a newsitem. The view was broken
  then. Now it shows the uploaded file for download below the content. Its no
  longer broken.
  [jensens]

- Add contributor role as default for all add permissions in order to
  work together with the different plone worklfows, which assume it is
  set this way.
  [jensens]

- fix #60: File Type has no mimetype specific icon in catalog metadata.
  Also fixed for Image.
  [jensens]

- fix #58: Migration ignores "Exclude from Navigation".
  [jensens]

- disable LinkIntegrityNotifications during migrations, closes #40.
  [jensens]

- Fix Bug on SearchableText_file indexer when input stream contains
  characters not convertable in ASCII. Assumes now utf-8 and replaces
  all unknown. Even if search can not find the words with special
  characters in, indexer does not break completely on those items.
  [jensens]

- Remove dependency on plone.app.referenceablebehavior, as it depends on
  Products.Archetypes which installs the uid_catalog.
  [thet]

- Make collection syndicatable.
  [vangheem]

- Include the migration module not only when Products.ATContentTypes is
  installed but also archetypes.schemaextender. The schemaextender might not
  always be available.
  [thet]

- Add fulltext search of file objects.
  [do3cc]

- Fix link_redirect_view: Use index instead of template class var to
  let customization by ZCML of the template.
  [toutpt]

- Add a permission for each content types.
  [toutpt]


1.0b2 (2013-05-31)
------------------

- Fix translations to the plone domain, and some translations match existing
  translations in the plone domain. (ported from plone.app.collection)
  [bosim]

- Fix atct_album_view and don't use atctListAlbum.py.
  [pbauer]

- Add constrains for content create with the Content profile.
  [ericof]

- Add SearchableText indexer to Folder content type.
  [ericof]

- Fix atct_album_view.
  [pbauer]

- Removed dependency for collective.dexteritydiff since its features were
  merged into Products.CMFDiffTool.
  [pbauer]

- Add test for behavior table_of_contents.
  [pbauer]

- Add migration for blobnewsitems as proposed in
  https://github.com/plone/plone.app.blob/pull/2.
  [pbauer]

- Require cmf.ManagePortal for migration.
  [pbauer]

- Always migrate files and images to blob (fixes #26).
  [pbauer]

- Add table of contents-behavior for documents.
  [pbauer]

- Add versioning-behavior and it's dependencies.
  [pbauer]

- Remove image_view_fullscreen from the display-dropdown.
  [pbauer]

- Enable selecting addable types on folders by default.
  [pbauer]

- Fix reference-migrations if some objects were not migrated.
  [pbauer]

- Keep the order references when migrating.
  [pabo3000]

- Move templates into their own folder.
  [pbauer]

- Moved migration related code to specific module.
  [gborelli]

- Added migration Collection from app.collection to app.contenttypes.
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

- Refactor p.a.collection robot framework tests.
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

- Set the text of front-page when creating a new Plone.
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

- Mime Type Icon added for File View.
  [loechel]


1.0a1 (unreleased)
------------------

- Initial release.
