Changelog
=========

1.1.4 (unreleased)
------------------

Breaking changes:

- *add item here*

New features:

- *add item here*

Bug fixes:

- *add item here*


1.1.3 (2017-07-20)
------------------

Bug fixes:

- Fixed two failing unit tests.  [maurits]

- Made sure the text field of Collections is searchable.
  `Issue 406 <https://github.com/plone/plone.app.contenttypes/issues/406>`_.
  [maurits]


1.1.2 (2017-05-09)
------------------

Bug fixes:

- Correct the SearchableText base indexer: use mime type of RichText output
  (rather than of that of the raw) value in plaintext conversion. Fixes #357.
  [petri]

- Add condition so custom folder migration does not fail if there is not
  an 'excludeFromNav'
  [cdw9]


1.1.1 (2016-06-06)
------------------

Bug fixes:

- Fixed possible cross site scripting (XSS) attack in news item image caption.  [maurits]

- Register explicitly plone.app.event dependency on configure.zcml.
  [hvelarde]

- Check if there is an image into leadimage field for migration.
  [bsuttor]

- Various fixes while migrating custom contenttypes :

  - do not fail if source object does not have a 'excludeFromNav' field;
  - do not fail if source object field's label contains special characters;
  - do not try to migrate assigned portlets if source object is not
    portlet assignable.

  [gbastien]


1.1 (2015-12-22)
----------------

- Change all text getters on ``plone.app.textfield.value.RichTextValue``
  objects to ``output_relative_to`` with the current context. This correctly
  transforms relative links. See:
  https://github.com/plone/plone.app.textfield/issues/7 (backported)
  [thet]

- Allow to pass custom field_migrator methods with custom migrations
  (backported).
  [pbauer]

- Fix issue in migration where source or target uuid could not
  be found (backported).
  [vangheem]

- Index subject field on the catalog so that is searchable.
  Fixes https://github.com/plone/plone.app.contenttypes/issues/194
  (backported).
  [gforcada]

- Avoid AttributeError when trying to get the default_page of an item
  when migrating (backported).
  [frapell]

- Avoid AttributeError from potential acquisition issues with folder listings
  (backported).
  [vangheem]

- Fix custom migration from and to types with spaces in the type-name
  (backported).
  [pbauer]

- Add ``getRawQuery`` method to Collection content type for backward
  compatibility with Archetypes API.
  Fixes (partially) https://github.com/plone/plone.app.contenttypes/issues/283.
  [hvelarde]

- Do a ``IRichText`` text indexing on all registered SearchableText indexers by
  doing it as part of the base ``SearchableText`` function. Convert the text
  from the source mimetype to ``text/plain``.
  [thet]


1.1b6 (2015-10-17)
------------------

- Do not raise errors when IPrimaryFieldInfo(obj) fails (e.g. when the
  Schema-Cache is gone).
  Fixes https://github.com/plone/Products.CMFPlone/issues/839
  [pbauer]

- Fix an error with logging an exception on indexing SearchableText for files
  and concating utf-8 encoded strings.
  [thet]

- In ``FolderView`` based views, don't include the ``portal_types`` query, if
  ``object_provides`` is set in the ``results`` method keyword arguments. Fixes
  a case, where no Album Images were shown, when portal_state's
  ``friendly_types`` didn't include the ``Image`` type.
  [thet]

- Add migrations from custom AT types to available DX types (fix #133).
  (backported from 1.2.x)
  [gbastien, cekk, tiazma, flohcim, pbauer]

- Add plone.app.querystring as a dependency (fixes collections migrated to p5
  and dexterity).
  (backported from 1.2.x)
  [pbauer]

- Migrate layout of portal to use the new listing-views when migrating to dx.
  (backported from 1.2.x)
  [pbauer]

- Migrate layout using the new listing-views when migrating folders,
  collections, topics.
  (backported from 1.2.x)
  [pbauer]

- Update allowed view_methods of the site-root on installing or migrating.
  Fixes #25.
  (backported from 1.2.x)
  [pbauer]

- Set default_view when updating view_methods. Fixes #250.
  (backported from 1.2.x)
  [pbauer]

- Fix bug in reference-migrations where linkintegrity-relations were turned
  into relatedItems.
  (backported from 1.2.x)
  [pbauer]

- Setup calendar and visible ids even when no default-content gets created.
  (backported from 1.2.x)
  [pbauer]

- Remove upgrade-step that resets all behaviors. Fixes #246.
  (backported from 1.2.x)
  [pbauer]

- Add convenience-view @@export_all_relations to export all relations.
  (backported from 1.2.x)
  [pbauer]

- Add method link_items that allows to link any kind of item (AT/DX) with any
  kind of relationship.
  (backported from 1.2.x)
  [pbauer]

- New implementation of reference-migrations.
  (backported from 1.2.x)
  [pbauer]

- Fix BlobNewsItemMigrator.
  (backported from 1.2.x)
  [MrTango]

- Fix ATSelectionCriterionConverter to set the right operators.
  (backported from 1.2.x)
  [MrTango]

- Fix @@custom_migraton when they type-name has a space (fixes #243).
  (backported from 1.2.x)
  [pbauer]

- Get and set linkintegrity-setting with registry.
  (backported from 1.2.x)
  [pbauer]

- Use generic field_migrators in all migrations.
  (backported from 1.2.x)
  [pbauer]

- Remove superfluous 'for'. Fixes plone/Products.CMFPlone#669.
  (backported from 1.2.x)
  [fulv]

- Added ``importlib`` as dependency on Python 2.6.
  [maurits]

- Don't use <figure> and <figcaption> html5 containers for Plone 4
  compatibility. sunburst css selectors don't support figure yet in
  for example newsitem styling.
  [fredvd]


1.1b5 (2015-05-29)
------------------

- Keep additional view_methods when migrating to new view_methods. Fixes #231.
  [pbauer]


1.1b4 (2015-05-19)
------------------

- Fix possible error setting fields for tabular_view for
  collections.  Issue #209.
  [maurits]

- Show the LeadImageViewlet only on default views.
  [thet]

- Fix ``contentFilter`` for collections.
  [thet]

- Don't batch the already batched collection results. Fixes #221.
  [thet]

- I18n fixes.
  [vincentfretin]

- Update image_view_fullscreen.pt for mobile friendliness.
  [fulv]

- In the listing view, don't repeat on the ``article`` tag, which makes it
  impossible to override this structure. Instead, repeat on a unrendered
  ``tal`` tag and move the article tag within.
  [thet]

- Don't try to show IContentLeadImage images, if theree none. Use the "mini"
  scale as default scale for IContentLeadImage.
  [thet]

- Improve handling of Link types with other URL schemes than ``http://`` and
  ``https://``.
  [thet]

- When installing the default profile, restrict uninstalling of old types to
  old FTI based ones.
  [thet]

- Reformatted all templates for 2 space indentation, 4 space for attributes.
  [thet]

- Register folder and collection views under the same name. Old registrations
  are kept for BBB compatibility.
  [thet]

- Refactor full_view and incorporate fixes from collective.fullview to
  1) display the default views of it's items, 2) be recursively callable
  and 3) have the same templates for folder and collections.
  [thet]

- Refactor folder_listing, folder_summary_view, folder_tabular_view and
  folder_album_view for folders as well as standard_view (collection_view),
  summary_view, tabular_view and thumbnail_view for collections to use the same
  templates and base view class.
  [thet]

- In the file view, render HTML5 ``<audio>`` or ``<video>`` tags for audio
  respectively video file types. Ancient browsers, which do not support that,
  just don't render these tags.
  [thet]

- Add ``event_listing`` to available view methods for the Folder and Collection
  types.
  [thet]

- Add migration for images added with collective.contentleadimage.
  [pbauer]

- Add migration for contentrules.
  [pbauer]

- Fix folder_full_view_item and allow overriding with jbot (fix #162).
  [pbauer]

- Migrate comments created with plone.app.discussion.
  [gbastien, pbauer]

- Allow migrating Topics and Subtopics to folderish Collections.
  [pbauer]

- Add migration from Topics to Collections (fixes #131).
  [maurits, pbauer]

- Add helpers and a form to update object with changed base class. Also
  allows migrating from itemish to folderish.
  [bogdangi, pbauer]

- Keep portlets when migrating AT to DX (fixes #161)
  [frisi, gbastien, petschki]

- Code modernization: sorted imports, use decorators, utf8 headers.
  [jensens]

- Fix: Added missing types to CMFDiffTool configuraion.
  [jensens]

- Integration of the new markup update and CSS for both Plone and Barceloneta
  theme. This is the work done in the GSOC Barceloneta theme project. Fix
  several templates.
  [albertcasado, sneridagh]

- Include translated content into migration-information (see #170)
  [pbauer]

- Add simple confirmation to prevent unintentional migration.
  [pbauer]

- Don't remove custom behaviors on reinstalling.
  [pbauer]

- Add bbb getText view for content with IRichText-behavior
  [datakurre]

- Support ``custom_query`` parameter in the ``result`` method of the
  ``Collection`` behavior. This allows for run time customization of the
  stored query, e.g. by request parameters.
  [thet]

- Fix 'AttributeError: image' when NewsItem unused the lead image behavior.
  [jianaijun]

- Restore Plone 4.3 compatibility by depending on ``plone.app.event >= 2.0a4``.
  The previous release of p.a.c got an implicit Plone 5 dependency through a
  previous version of plone.app.event.
  [thet]

- Replace AT-fti with DX-fti when migrating a type.
  [esteele, pbauer]

- Only show migrateable types (fixes #155)
  [pbauer]

- Add logging during and after migration (fixes #156)
  [pbauer]

- When replacing the default news and events collections, reverse the
  sort order correctly.
  [maurits]

- Adapt to changes of plone.app.event 2.0.
  [thet]

- Fix issue when mimetype can be None.
  [pbauer]

- Add form to install pac and forward to dx_migration
  after a successful migration to Plone 5
  [pbauer]

- Rename atct_album_view to folder_album_view.
  [pbauer]

- Do a better check, if LinguaPlone is installed, based on the presence of the
  "LinguaPlone" browser layer. Asking the quick installer tool might claim it's
  installed, where it's not.
  [thet]

- Register folderish views not for plone.app.contenttypes' IFolder but for
  plone.dexterity's IDexterityContainer. Now, these views can be used on any
  folderish Dexterity content.
  [thet]

- Add a ICustomMigrator interface to the migration framework, which can be used
  to register custom migrator adapters. This can be useful to add custom
  migrators to more than one or all content types. For example for
  schemaextenders, which are registered on a interface, which is provided by
  several content types.
  [thet]

- In the migration framework, fix queries for Archetype objects, where only
  interfaces are used to skip brains with no or Dexterity meta_type. In some
  cases Dexterity and Archetype objects might provide the same marker
  interfaces.
  [thet]

- Add logging messages to content migrator for more verbosity on what's
  happening while running the migration.
  [thet]

- Use Plone 4 based @@atct_migrator and @@atct_migrator_results template
  structure.
  [thet]

- Fix viewlet warning about ineditable content (fixes #130)
  [pbauer]

- Reintroduce the removed schema-files and add upgrade-step to migrate to
  behavior-driven richtext-fields (fixes #127)
  [pbauer]

- Delete Archetypes Member-folder before creating new default-content
  (fixes #128)
  [pbauer]

- Remove outdated summary-behavior from event (fixes #129)
  [pbauer]


1.1b3 (2014-09-07)
------------------

- Include translated content into migration-information (see #170)
  [pbauer]

- Add simple confirmation to prevent unintentional migration.
  [pbauer]

- Don't remove custom behaviors on reinstalling.
  [pbauer]

- Remove enabling simple_publication_workflow from testing fixture.
  [timo]

- Only show migrateable types (fixes #155)
  [pbauer]

- Add logging during and after migration (fixes #156)
  [pbauer]

- Remove 'robot-test-folder' from p.a.contenttypes test setup. It is bad to
  add content to test layers, especially if those test layers are used by
  other packages.
  [timo]

- When replacing the default news and events collections, reverse the
  sort order correctly.
  [maurits]

- For plone.app.contenttypes 1.1.x, depend on plone.app.event < 1.1.999.
  Closes/Fixes #149.
  [khink, thet]


1.1b2 (2014-02-21)
------------------

- Fix viewlet warning about ineditable content (fixes #130)
  [pbauer]

- Reintroduce the removed schema-files and add upgrade-step to migrate to
  behavior-driven richtext-fields (fixes #127)
  [pbauer]

- Delete Archetypes Member-folder before creating new default-content
  (fixes #128)
  [pbauer]

- Remove outdated summary-behavior from event (fixes #129)
  [pbauer]


1.1b1 (2014-02-19)
------------------

- Add tests for collections and collection-migrations.
  [pbauer]

- Removed Plone 4.2 compatibility.
  [pbauer]

- Add migration of at-collections to the new collection-behavior.
  [pbauer]

- Display richtext in collection-views.
  [pbauer]

- Reorganize and improve documentation.
  [pbauer]

- Add a richtext-behavior and use it in for all types.
  [amleczko, pysailor]

- Improve the migration-results page (Fix #67).
  [pbauer]

- For uneditable content show a warning and hide the edit-link.
  [pbauer]

- Keep all modification-date during migration (Fix #62).
  [pbauer]

- Only attempt transforming files if valid content type.
  [vangheem]

- Make the collection behavior aware of INavigationRoot. Fixes #98
  [rafaelbco]

- Use unique URL provided by ``plone.app.imaging`` to show the large version
  of a news item's lead image. This allows use of a stronger caching policy.
  [rafaelbco]

- Fix URL for Link object on the navigation portlet if it
  contains variables (Fix #110).
  [rafaelbco]


1.1a1 (2013-11-22)
------------------

- Event content migration for Products.ATContentTypes ATEvent,
  plone.app.event's ATEvent and Dexterity example type and
  plone.app.contenttypes 1.0 Event to plone.app.contenttypes 1.1
  Event based on plone.app.event's Dexterity behaviors.
  [lentinj]

- Remove DL's from portal message templates.
  https://github.com/plone/Products.CMFPlone/issues/153
  [khink]

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

- Initial implementation.
  [pbauer, timo, pumazi, agitator]
