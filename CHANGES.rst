Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

3.0.0a13 (2022-05-24)
---------------------

Bug fixes:


- When using ``@@images`` view, call ``tag`` directly.
  [maurits] (#3535)


3.0.0a12 (2022-05-14)
---------------------

Breaking changes:


- Use plone.base, code style black, isort, pyupgrade, manual overhaul.
  [jensens] (#644)


Bug fixes:


- Removed unused migration and uninstall code, and rfc822 tests.
  [maurits] (#641)
- Re-register and improve @@base_class_migrator_form required to migrate to foilderish items.
  [pbauer] (#642)


3.0.0a11 (2022-04-07)
---------------------

New features:


- PLIP 2780: Move features of collective.dexteritytextindexer to core.
  [zworkb] (#2780)


Bug fixes:


- Fix Collections Standard view when showing events
  [frapell] (#634)
- listing_view and summary_view cleanup and float fix
  [petschki] (#638)
- Aftermath of PLIP 3395 + isort/black on these files.
  [jensens] (#639)


3.0.0a10 (2022-02-24)
---------------------

Bug fixes:


- A content type with the richtext behavior might not have a `text` attribute,
  handle that gracefully.
  [gforcada] (#1)


3.0.0a9 (2022-01-28)
--------------------

Bug fixes:


- Security fix: prevent cache poisoning with the Referer header.
  See `security advisory <https://github.com/plone/plone.app.contenttypes/security/advisories/GHSA-f7qw-5fgj-247x>`.
  [maurits] (#1)


3.0.0a8 (2022-01-28)
--------------------

Bug fixes:


- Depend on `plone.namedfile` core instead of its empty `[blobs]` extra.
  [maurits] (#106)


3.0.0a7 (2022-01-19)
--------------------

Breaking changes:


- Remove upgrade steps that are not relevant anymore in Plone 6 [ale-rt] (#613)


Bug fixes:


- Fix tests with ES6.
  [maurits] (#6)


3.0.0a6 (2022-01-07)
--------------------

Bug fixes:


- Fix author url in tabular listing
  [petschki] (#627)


3.0.0a5 (2021-11-23)
--------------------

Breaking changes:


- Remove atcontenttypes dependencies, migration, keep BaseClassMigratorForm.
  [agitator] (#620)
- Remove (ATCT) BBB view name registrations.
  [agitator] (#621)


Bug fixes:


- Adapt the tests to cope with the fact the since Plone 6 the Plone site root is cataloged [ale-rt] (#616)
- Fixed typo in test 'constraints' -> 'constrains'. [iham] (#619) (#619)
- Use document_view as default for dx site root.
  [agitator] (#624)


3.0.0a4 (2021-10-16)
--------------------

Bug fixes:


- Upgrade: fix icon expressions for portal_types and their view and edit actions.
  See `this PR comment <https://github.com/plone/plone.app.upgrade/pull/259#issuecomment-944213712>`_.
  [maurits] (#259)
- Add missing i18n:translate tags
  [erral] (#614)


3.0.0a3 (2021-09-15)
--------------------

Breaking changes:


- Plone Site is now a DX container. This means that the front-page object no
  longer exists.
  Refs PLIP 2454.
  [jaroel] (#475)


Bug fixes:


- Remove cyclic dependency with Products.CMFPlone
  [ericof] (#609)
- Removed autoinclude entry point.
  No longer needed, since ``Products.CMFPlone`` explicitly includes our zcml.
  [maurits] (#611)


3.0.0a2 (2021-05-11)
--------------------

New features:


- Rework contenttype views.
  [agitator] (#598)


3.0.0a1 (2021-04-20)
--------------------

Breaking changes:


- Update for Plone 6 with Bootstrap markup
  [agitator, ale-rt, ladplone, mliebischer, pbauer, petschki, santonelli] (#589)


Bug fixes:


- Various fixes for restoring references:

  - Migrate ``relatesTo`` AT relation to ``relatedItems`` DX relation.
  - In DX check the schema to see if relation field is list or item.
    Taken over from `collective.relationhelpers <https://github.com/collective/collective.relationhelpers/>`_.
  - ``restore_references``: accept ``relationship_fieldname_mapping`` argument.
    This must be a dictionary with a relationship name as key and fieldname as value, instead of always using ``relatedItems`` as fieldname.

  [maurits] (#510)
- Use python statements in templates.
  [pbauer, mliebischer, ladplone] (#579)
- Catch AttributeError for ``getNextPreviousEnabled`` during migration.
  [maurits] (#582)
- migrate_datetimefield: do nothing when old value is None.
  This fixes ``AttributeError: 'NoneType' object has no attribute 'asdatetime'``.
  [maurits] (#584)
- Fix condition in ``document.pt``
  [petschki] (#596)


2.2.1 (2020-10-12)
------------------

Bug fixes:


- Update tests to fix updated schema cache.
  See https://github.com/plone/plone.dexterity/pull/137
  [@avoinea] (#573)


2.2.0 (2020-09-28)
------------------

New features:


- Allow passing a custom catalog-query to migrateCustomAT to constrain which objects to migrate. [pbauer] (#572)


Bug fixes:


- Fix various deprecation warnings.
  [maurits] (#3130)


2.1.10 (2020-08-14)
-------------------

Bug fixes:


- Handle cases where the __parent__ of a discussion was not set to the migrated DX object.
  [pbauer] (#566)
- In the edge case where the meta_type could not be resolved assume is_folderish being false.
  [pbauer] (#567)
- Fixed problems in ``getMimeTypeIcon``.
  The contentType of the file was ignored, and icon paths could have a duplicate ``++resource++mimetype.icons/``.
  [maurits] (#569)


2.1.9 (2020-07-17)
------------------

Bug fixes:


- Display the image size rounded with 1 decimal digit [ale-rt] (#554)
- Avoid doing the search twice in listings by reusing the batch variable.
  [vincentfretin] (#560)


2.1.8 (2020-06-30)
------------------

Bug fixes:


- Internationalize selectable columns in collection and tabular view.
  This fixes https://github.com/plone/Products.CMFPlone/issues/2597
  [vincentfretin] (#559)


2.1.7 (2020-04-20)
------------------

Bug fixes:


- Minor packaging updates. (#1)


2.1.6 (2020-02-16)
------------------

Bug fixes:


- Integrate PloneHotFix20200121: add more permission checks.
  See https://plone.org/security/hotfix/20200121/privilege-escalation-for-overwriting-content
  [maurits] (#3021)
- Add a guard in the document.pt template to allow the Document type not to have the RichText
  enforce the behavior enabled.
  [sneridagh] (#3047)


2.1.5 (2019-11-25)
------------------

Bug fixes:


- for migration tests uninstall plone.app.contenttypes if previously installed
  [ericof] (#535)


2.1.4 (2019-10-22)
------------------

Bug fixes:


- Fix richtext ``getText`` view to use the correct schema interface.
  [thet]

- Robot tests: split big content listing scenario, fix deprecations.
  [maurits] (#533)


2.1.3 (2019-10-12)
------------------

Bug fixes:


- Clear schema cache after migration step ``migrate_to_pa_event``. [jensens] (#531)
- Explicitly load zcml of dependencies, instead of using ``includeDependencies``
  [maurits] (#2952)


2.1.2 (2019-07-18)
------------------

Bug fixes:


- Speedup stats during migration by not waking up all objects.
  [pbauer] (#529)


2.1.1 (2019-07-06)
------------------

Bug fixes:


- Don't test for hard coded image size in test.
  [agitator] (#527)


2.1.0 (2019-06-19)
------------------

New features:


- Support ILeadImage behavior when display collection album view.
  [rodfersou] (#524)
- Add more log-messages during migration from AT to DX.
  [pbauer] (#526)


Bug fixes:


- Use the shared 'Plone test setup' and 'Plone test teardown' keywords in Robot tests.
  [Rotonen] (#522)


2.0.5 (2019-05-04)
------------------

Bug fixes:


- Move dotted behaviors to named behaviors. [iham] (#519)


2.0.4 (2019-04-29)
------------------

Bug fixes:


- Add 'content-core' macro definition to summary_view.pt so it can be reused
  [petschki] (#514)
- Speed up traversal to main_template by markling it as a browser-view.
  [pbauer] (#517)


2.0.3 (2019-03-21)
------------------

Bug fixes:


- Detect whether a webdav request is RFC822 or pure payload and handle accordingly. (#2781)


2.0.2 (2019-03-03)
------------------

Bug fixes:


- Fix robots test after dropdownnavigation is enabled for new sites. [pbauer]
  (#511)


2.0.1 (2019-02-13)
------------------

Bug fixes:


- Following the rename of the lead image and rich text behaviors, use the new
  setting of plone.behavior to register their ``former_dotted_names``, so that
  consumers that have stored the old dotted name have a chance of recovering.
  This is especially needed for plone.app.versioningbehavior, see `issue
  <https://github.com/plone/plone.app.versioningbehavior/pull/45>` [pysailor]
  (#480)
- Fixed sorting error after Changing the base class for existing objects. see
  `issue <https://github.com/plone/plone.app.contenttypes/issues/487>`
  [jianaijun] (#497)
- Fix for folder view when there is one item more than the batch size. see
  `issue <https://github.com/plone/plone.app.contenttypes/issues/500>`
  [reinhardt] (#500)
- replace catalog_get_all(catalog) with catalog.getAllBrains() [pbauer] (#503)


2.0.0 (2018-10-30)
------------------

Breaking changes:

- ILeadImage and IRichText behaviors now have proper "Marker"-Interfaces.
  As this was only possible by renaming the schema adapter to *Behavior* to
  not break with implementations inside the collective, the FTI-behavior-definition
  has changed:

  - ``plone.app.contenttypes.behaviors.leadimage.ILeadImage``
    becomes
    ``plone.app.contenttypes.behaviors.leadimage.ILeadImageBehavior``
    and
  - ``plone.app.contenttypes.behaviors.richtext.IRichText``
    becomes
    ``plone.app.contenttypes.behaviors.richtext.IRichTextBehavior``

  [iham]

New features:

- By using correct (Marker-)Interfaces for the ILeadImage and IRichText,
  the factories are now working properly and can be reconfigured
  wherever you might need them. ZCA FTW!
  [iham]
- Use human_readable_size from Products.CMFPlone.utils to replace getObjSize
  script. #1801
  [reinhardt]

Bug fixes:

- The ``Format`` accessor should actually return the ``format`` attribute
  (see plone/Products.CMFPlone#2540)
  [ale-rt]

- Fix resource warnings.
  [davisagli]

1.4.12 (2018-09-23)
-------------------

Breaking changes:

- ILeadImage and IRichText behaviors now have proper "Marker"-Interfaces.
  As this was only possible by renaming the schema adapter to *Behavior* to
  not break with implementations inside the collective, the FTI-behavior-definition
  has changed:

  - ``plone.app.contenttypes.behaviors.leadimage.ILeadImage``
    becomes
    ``plone.app.contenttypes.behaviors.leadimage.ILeadImageBehavior``
    and
  - ``plone.app.contenttypes.behaviors.richtext.IRichText``
    becomes
    ``plone.app.contenttypes.behaviors.richtext.IRichTextBehavior``

  [iham]

New features:

- By using correct (Marker-)Interfaces for the ILeadImage and IRichText,
  the factories are now working properly and can be reconfigured
  wherever you might need them. ZCA FTW!
  [iham]

Bug fixes:

- Fix folder layout property migration. The default listing_view layout was
  always set if a folder didn't have a layout property.
  Also a default_page property could be inherited from parent folders or
  the Plone Siteroot, causing 'front-page' default_pages on many folders.
  Now only a direct layout property is copied and in that case on the local
  default_page if set is copied again.
  see `issue 444 <https://github.com/plone/plone.app.contenttypes/issues/444>`
  [fredvd]

- Fixed false implemented Factories and Markers for ILeadImage and IRichText.
  see `issue 457 <https://github.com/plone/plone.app.contenttypes/issues/476>`
  [iham]

- Fixed Tests for collection and migration.
  see `issue <https://github.com/plone/plone.app.contenttypes/issues/477>`
  [iham]

- Pinned pydocstyle as it broke buildout.
  [iham]

- pep8 cleanup.
  [iham]

- Fix various issues in py3
  [pbauer]


1.4.11 (2018-06-18)
-------------------

Bug fixes:

- Fix SearchableText in Python 3
  [pbauer]

- Skip migration tests if ATContentTypes is not installed.
  [davisagli]

- check if a contentrule exists before assignment on migration
  [MrTango]


1.4.10 (2018-04-03)
-------------------

New features:

- Set the ``plone.app.contenttypes_migration_running`` key while running a migration.
  Other addons can check for that and handle accordingly.
  [thet]

Bug fixes:

- Implement better human readable file size logic.
  [hvelarde]

- Do not encode query strings on internal link redirections;
  fixes `issue 457 <https://github.com/plone/plone.app.contenttypes/issues/457>`_.
  [hvelarde]

- Migrations:

  - Handle ignore catalog errors where a brain can't find it's object.
  - Try to delete the layout attribute before setting the layout.
    Rework parts where the layout is set by always setting the layout.

  [thet]

- In folder listings, when a content object has no title show it's id instead of an empty title.
  [thet]

- Fix upgrades steps when the catalog is inconsistent
  [ale-rt]


1.4.9 (2018-02-11)
------------------

New features:

- Members folder made permanently private. Fixes https://github.com/plone/Products.CMFPlone/issues/2259
  [mrsaicharan1]


1.4.8 (2018-02-05)
------------------

Bug fixes:

- Do not use ``portal_quickinstaller`` in the migration form.
  Use ``get_installer`` to check if ``plone.app.contenttypes`` is
  installed or installable.  Use ``portal_setup`` directly for
  blacklisting the ``type_info`` step when installing our profile.
  [maurits]

- Add Python 2 / 3 compatibility
  [pbauer]


1.4.7 (2017-12-14)
------------------

Bug fixes:

- Rename post_handlers. Fixes https://github.com/plone/Products.CMFPlone/issues/2238
  [pbauer]


1.4.6 (2017-11-26)
------------------

New features:

- Allow to patch searchableText index during migrations.
  [pbauer]

- Expose option to skip catalog-reindex after migration in form.
  [pbauer]

Bug fixes:

- Remove last use of ``atcontenttypes`` translation domain.
  Fixes `issue 37 <https://github.com/plone/plone.app.contenttypes/issues/37>`_.
  [maurits]

- Don't overwrite existing settings for Plone Site.
  [roel]

1.4.5 (2017-10-06)
------------------

Bug fixes:

- Do not install plone.app.discussion when installing plone.app.contenttypes.
  [timo]


1.4.4 (2017-10-02)
------------------

New features:

- Test SVG handling
  [tomgross]

- Use post_handler instead of import_steps.
  [pbauer]

Bug fixes:

- Do not use a default value in the form of ``http://`` for the link.
  The new link widget resolves that to the portal root object.
  Also, it's not a valid URL.
  Fixes: https://github.com/plone/Products.CMFPlone/issues/2163
  [thet]

- Remove obsolete HAS_MULTILINGUAL from utils.
  [pbauer]

- Clean up all ``__init__`` methods of the browser views to avoid unnecessary code execution.
  [thet]

- Make sure the effects of the robotframework REMOTE_LIBRARY_BUNDLE_FIXTURE
  fixture are not accidentally removed as part of tearing down the
  PLONE_APP_CONTENTTYPES_ROBOT_FIXTURE.
  [davisagli]


1.4.3 (2017-08-30)
------------------

Bug fixes:

- Disable queuing of indexing-operations (PLIP https://github.com/plone/Products.CMFPlone/issues/1343)
  during migration to Dexterity to prevent catalog-errors.
  [pbauer]


1.4.2 (2017-08-27)
------------------

New features:

- Index default values when indexing the file fails due to a missing binary.
  [pbauer]

- Allow to skip rebuilding the catalog when migrating at to dx in code.
  [pbauer]

Bug fixes:

- Add translation namesspace and i18n:translate to the dexterity schema
  definitions for the content types that have extra field defined on top of the
  behavior composition. Otherwise no translations can be picked up.
  [fredvd]

- Use original raw text and mimetype when indexing rich text.
  This avoids a double transform (raw source to output mimetype to plain text).
  Includes a reindex of the SearchableText index for Collections, Documents and News Items.
  `Issue 2066 <https://github.com/plone/Products.CMFPlone/issues/2066>`_.
  [maurits]

- Migrate the richtext-field 'text' when migrating ATTopics to Collections.
  [pbauer]

- Remove Language='all' from migration-query since it was removed from p.a.multilingual
  [pbauer]

- Actually migrate all migratable types when passing 'all' to at-dx migration.
  [pbauer]

- Remove plone.app.robotframework 'reload' extra.
  This allows to remove quite some other external dependencies that are not Python 3 compatible.
  [gforcada]

1.4.1 (2017-07-03)
------------------

New features:

- Integrate new link widget from plone.app.z3cform.
  [tomgross]

Bug fixes:

- Made sure the text field of Collections is searchable.
  `Issue 406 <https://github.com/plone/plone.app.contenttypes/issues/406>`_.
  [maurits]

- Fix issue preventing disabling icons and/or thumbs globally.
  [fgrcon]

1.4 (2017-06-03)
----------------


New features:

- New metadata catalog column MimeType
  https://github.com/plone/Products.CMFPlone/issues/1995
  [fgrcon]

- new behavior: IThumbIconHandling, supress thumbs /icons, adjust thumb size, templates adapted
  https://github.com/plone/Products.CMFPlone/issues/1734 (PLIP)

Bug fixes:

- fixed css-classes for thumb scales ...
  https://github.com/plone/Products.CMFPlone/issues/2077
  [fgrcon]

- Fix test for checking if TinyMCE is loaded which broke after https://github.com/plone/Products.CMFPlone/pull/2059
  [thet]

- Fix flaky test in test_indexes.
  [thet]

- removed unittest2 dependency
  [kakshay21]

- Fix issue where contentFilter could not be read from request
  [datakurre]


1.3.0 (2017-03-27)
------------------

New features:

- Make use of plone.namedfile's tag() function to generate img tags. Part of plip 1483.
  [didrix]

Bug fixes:

- Avoid failure during migration if relation is broken.
  [cedricmessiant]

- Fix import location for Products.ATContentTypes.interfaces.
  [thet]

1.2.22 (2017-02-20)
-------------------

Bug fixes:

- Add condition so custom folder migration does not fail if there is not
  an 'excludeFromNav'
  [cdw9]


1.2.21 (2017-02-05)
-------------------

New features:

- Remove browserlayer from listing views to allow overrides from other packages
  [agitator]

Bug fixes:

- Use helper method to retrieve all catalog brains in migration code, because Products.ZCatalog removed the ability to get all brains by calling the catalog without arguments.
  [thet, gogobd]

- Fix use of add_file in testbrowser tests. [davisagli]

- Render migration results without using Zope session. [davisagli]


1.2.20 (2017-01-20)
-------------------

Bug fixes:

- Use unicode string when .format() parameter is unicode for the field migrator
  [frapell]


1.2.19 (2016-12-02)
-------------------

Bug fixes:

- Fix SearchableText indexer, using textvalue.mimeType
  [agitator]

- Fix Mimetype icon path. With the removal of the skins folder in
  https://github.com/plone/Products.MimetypesRegistry/pull/8/commits/61acf8327e5c844bff9e5c5676170aaf0ee2c323
  we need the full resourcepath now
  [agitator]

- Show message for editors when viewing Link.
  Fixes `issue 375 <https://github.com/plone/plone.app.contenttypes/issues/375>`_.
  [maurits]

- Update code to follow Plone styleguide.
  [gforcada]

- Update File.xml view action url_expr to append /view
  Fixes 'issue 378' <https://github.com/plone/plone.app.contenttypes/issues/378>`_.
  [lbrannon]


1.2.18 (2016-09-14)
-------------------

Bug fixes:

- Correct the SearchableText base indexer: use mime type of RichText output
  (rather than raw) value in plaintext conversion. Fixes #357.
  [petri]


1.2.17 (2016-08-18)
-------------------

New features:

- Configure edit urls for locking support, where locking support is enabled.
  [thet]

- Add ``i18n:attribute`` properies to all action nodes for FTI types.
  [thet]

- added few pypi links in 'Migration' section
  [kkhan]

Bug fixes:

- Marked relative location criterion robot test as unstable.
  This needs further investigation, but must not block Plone development.
  See issue https://github.com/plone/plone.app.contenttypes/issues/362
  [maurits]

- Remove ``path`` index injection in "plone.collection" behaviors ``results`` method.
  It is a duplicate.
  Exactly the same is done already in the ``plone.app.querybuilder.querybuilder._makequery``,
  which is called by above ``results`` method.
  [jensens]

- Select all migratable types in migration-form by default. Fixes #193.
  [pbauer]

- Use zope.interface decorator.
  [gforcada]

- Mark robot test ``plone.app.contenttypes.tests.test_robot.RobotTestCase.Scenario Test Absolute Location Criterion`` as unstable.
  This needs further investigation, but must not block Plone development.
  [jensens]

- corrected typos in the documentation
  [kkhan]


1.2.16 (2016-06-12)
-------------------

Bug fixes:

- Wait longer to fix unstable robot tests.  [maurits]


1.2.15 (2016-06-06)
-------------------

Bug fixes:

- Fixed possible cross site scripting (XSS) attack in lead image caption.  [maurits]


1.2.14 (2016-05-25)
-------------------

Bug fixes:

- Encode the linked url for the Link type to allow for non ascii characters in the url.
  [martior]


1.2.13 (2016-05-12)
-------------------

Fixes:

- Deferred adapter lookup in collection view.
  This was looked up for contentmenu/toolbar at every authenticated request.
  It also had side effects if custom collection behaviors are used.
  [jensens]

- Fixed unstable robot test for location criterion.  [maurits]

- Don't fail for ``utils.replace_link_variables_by_paths``, if value is ``None``.
  The value can be ``None`` when creating a ``Link`` type with ``invokeFactory`` without ``remoteUrl`` set and calling the indexer before setting the URL.
  [thet]


1.2.12 (2016-04-13)
-------------------


New:

- assign shortnames to behaviors as supported by plone.behavior
  [thet]


1.2.11 (2016-03-31)
-------------------

New:

- WebDAV support for File and Image
  [ebrehault]

Fixes:

- Made xpath expression in test less restrictive.
  [maurits]

- Register explicitly plone.app.event dependency on configure.zcml.
  [hvelarde]


1.2.10 (2016-02-27)
-------------------

New:

- Added *listing* macro as found in ``listing.pt`` to
  ``listing_album.pt`` and ``listing_tabular.pt`` for
  a coherent customization.
  [tomgross]

Fixes:

- Check if there is a non-empty leadimage field for migration.
  [bsuttor]

- Make sure to have image scale before generating tag for album view.
  [vangheem]

- Also remove collections upon uninstalling.
  [pbauer]

- Various fixes while migrating custom contenttypes:

  - do not fail if source object does not have a 'excludeFromNav' field;
  - do not fail if source object field's label contains special characters;
  - do not try to migrate assigned portlets if source object is not
    portlet assignable.
    [gbastien]

- No longer try to install ATContentTypes-types on uninstalling.
  [pbauer]

- Enhancement: Split up migration test for modification date and references
  in two functions for easier debugging.
  [jensens]

- Simplify test in robot framework which fails in its newer version.
  [jensens]


1.2.9 (2016-01-08)
------------------

Fixes:

- Change all text getters on ``plone.app.textfield.value.RichTextValue``
  objects to ``output_relative_to`` with the current context. This correctly
  transforms relative links. See:
  https://github.com/plone/plone.app.textfield/issues/7
  [thet]


1.2.8 (2015-12-15)
------------------

Fixes:

- fix issue in migration where source or target uuid could not
  be found
  [vangheem]


1.2.7 (2015-11-28)
------------------

Fixes:

- Index subject field on the catalog so that is searchable.
  Fixes https://github.com/plone/plone.app.contenttypes/issues/194
  [gforcada]


1.2.6 (2015-11-25)
------------------

New:

- Allow to pass custom field_migrator methods with custom migrations.
  [pbauer]

Fixes:

- Create standard news/events collections with ``selection.any``.
  Issue https://github.com/plone/Products.CMFPlone/issues/1040
  [maurits]

- Avoid AttributeError from potential acquisition issues with folder listings
  [vangheem]

- Avoid AttributeError when trying to get the default_page of an item
  when migrating
  [frapell]

- Used html5 doctype in image_view_fullscreen.  Now it can be parsed
  correctly by for example i18ndude.
  [maurits]

- Use plone i18n domain in zcml.
  [vincentfretin]

- Do a ``IRichText`` text indexing on all registered SearchableText indexers by
  doing it as part of the base ``SearchableText`` function. Convert the text
  from the source mimetype to ``text/plain``.
  [thet]

- Add ``getRawQuery`` method to Collection content type for backward compatibility with Archetypes API.
  Fixes (partially) https://github.com/plone/plone.app.contenttypes/issues/283.
  [hvelarde]


1.2.5 (2015-10-28)
------------------

Fixes:

- Fix custom migration from and to types with spaces in the type-name.
  [pbauer]

- Fixed full_view when content is not IUUIDAware (like the portal).

- Cleanup and rework: contenttype-icons
  and showing thumbnails for images/leadimages in listings ...
  https://github.com/plone/Products.CMFPlone/issues/1226
  [fgrcon]

- Fix full_view when content is not IUUIDAware (like the portal).
  Fixes https://github.com/plone/Products.CMFPlone/issues/1109.
  [pbauer]

- Added plone.app.linkintegrity to dependencies due to test-issues.
  [pbauer]


1.2.4 (2015-09-27)
------------------

- Fixed full_view error when collection contains itself.
  [vangheem]

- test_content_profile: do not appy Products.CMFPlone:plone.
  [maurits]


1.2.3 (2015-09-20)
------------------

- Do not raise an exception for items where @@full_view_item throws an
  exception. Instead hide the object.
  [pbauer]

- Do not raise errors when IPrimaryFieldInfo(obj) fails (e.g. when the
  Schema-Cache is gone).
  Fixes https://github.com/plone/Products.CMFPlone/issues/839
  [pbauer]

- Fix an error with logging an exception on indexing SearchableText for files
  and concating utf-8 encoded strings.
  [thet]

- Make consistent use of LeadImage behavior everywhere. Related to
  plone/plone.app.contenttypes#1012. Contentleadimages no longer show up in
  full_view since they are a viewlet.
  [sneridagh, pbauer]

- Fixed the summary_view styling
  [sneridagh]
- redirect_links property has moved to the configuration registry.
- redirect_links, types_view_action_in_listings properies have moved to the
  configuration registry.
  [esteele]


1.2.2 (2015-09-15)
------------------

- Prevent negative ints and zero when limiting collection-results.
  [pbauer]


1.2.1 (2015-09-12)
------------------

- Migrate next-previous-navigation.
  Fix https://github.com/plone/plone.app.contenttypes/issues/267
  [pbauer]


1.2.0 (2015-09-07)
------------------

- Handle languages better for content that is create when site is generated
  [vangheem]

- In ``FolderView`` based views, don't include the ``portal_types`` query, if
  ``object_provides`` is set in the ``results`` method keyword arguments. Fixes
  a case, where no Album Images were shown, when portal_state's
  ``friendly_types`` didn't include the ``Image`` type.
  [thet]


1.2b4 (2015-08-22)
------------------

- Test Creator criterion with Any selection.
  [mvanrees]

- Selection criterion converter: allow selection.is alternative operation.
  [mvanrees]

- Fixed corner case in topic migration.
  [mvanrees]

- Use event_listung for /events/aggregator in new sites.
  [pbauer]

- Remove obsolete collections.css
  [pbauer]

- Add plone.app.querystring as a dependency (fixes collections migrated to p5
  and dexterity).
  [pbauer]

- Migrate layout of portal to use the new listing-views when migrating to dx.
  [pbauer]

- Migrate layout using the new listing-views when migrating folders,
  collections, topics.
  [pbauer]

- Update allowed view_methods of the site-root on installing or migrating.
  Fixes #25.
  [pbauer]

- Set default_view when updating view_methods. Fixes #250.
  [pbauer]

- Fix bug in reference-migrations where linkintegrity-relations were turned
  into relatedItems.
  [pbauer]

- Setup calendar and visible ids even when no default-content gets created.
  [pbauer]

- Remove upgrade-step that resets all behaviors. Fixes #246.
  [pbauer]

- Add convenience-view @@export_all_relations to export all relations.
  [pbauer]

- Add method link_items that allows to link any kind of item (AT/DX) with any
  kind of relationship.
  [pbauer]

- New implementation of reference-migrations.
  [pbauer]

- Fix i18n on custom_migration view.
  [vincentfretin]


1.2b3 (2015-07-18)
------------------

- Fix BlobNewsItemMigrator.
  [MrTango]

- Fix ATSelectionCriterionConverter to set the right operators.
  [MrTango]

- Fix @@custom_migraton when they type-name has a space (fixes #243).
  [pbauer]

- Get and set linkintegrity-setting with registry.
  [pbauer]

- Use generic field_migrators in all migrations.
  [pbauer]

- Remove superfluous 'for'. Fixes plone/Products.CMFPlone#669.
  [fulv]


1.2b2 (2015-06-05)
------------------

- Use modal pattern for news item image instead of jquery tools.
  [vangheem]


1.2b1 (2015-05-30)
------------------

- Keep additional view_methods when migrating to new view_methods. Fixes #231.
  [pbauer]

- Fix upgrade-step to use new view_methods.
  [pbauer]

- Fix possible error setting fields for tabular_view for
  collections.  Issue #209.
  [maurits]


1.2a9 (2015-05-13)
------------------

- Provide table of contents for document view.
  [vangheem]

- Default to using locking support on Page, Collection, Event and News Item types.
  [vangheem]

- Show the LeadImageViewlet only on default views.
  [thet]


1.2a8 (2015-05-04)
------------------

- Follow best practice for CHANGES.rst.
  [timo]

- Add migrations from custom AT types to available DX types (fix #133).
  [gbastien, cekk, tiazma, flohcim, pbauer]

- Fix ``contentFilter`` for collections.
  [thet]

- Don't batch the already batched collection results. Fixes #221.
  [thet]

- I18n fixes.
  [vincentfretin]

- Fix ``test_warning_for_uneditable_content`` to work with recent browser layer
  changes in ``plone.app.z3cform``.
  [thet]

- Update image_view_fullscreen.pt for mobile friendliness.
  [fulv]

- Removed dependency on CMFDefault
  [tomgross]


1.2a7 (2015-03-27)
------------------

- Re-relase 1.2a6. See https://github.com/plone/plone.app.contenttypes/commit/7cb74a2fcbf108acd43fe4ae3713f007db2073bf for details.
  [timo]


1.2a6 (2015-03-26)
------------------

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

- Define ``default_page_types`` in the ``propertiestool.xml`` profile.
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


1.2a5 (2014-10-23)
------------------

- Code modernization: sorted imports, use decorators, utf8 headers.
  [jensens]

- Fix: Added missing types to CMFDiffTool configuraion.
  [jensens]

- Integration of the new markup update and CSS for both Plone and Barceloneta
  theme. This is the work done in the GSOC Barceloneta theme project. Fix
  several templates.
  [albertcasado, sneridagh]


1.2a4 (2014-09-17)
------------------

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


1.2a3 (2014-04-19)
------------------

- Adapt to changes of plone.app.event 2.0.
  [thet]

- Fix issue when mimetype can be None.
  [pbauer]


1.2a2 (2014-04-13)
------------------

- Enable IShortName for all default-types.
  [pbauer, mikejmets]

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


1.2a1 (2014-02-22)
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
