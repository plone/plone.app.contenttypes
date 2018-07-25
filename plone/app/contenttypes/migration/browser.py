# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from plone.app.contenttypes.content import Document
from plone.app.contenttypes.content import File
from plone.app.contenttypes.content import Folder
from plone.app.contenttypes.content import Image
from plone.app.contenttypes.content import Link
from plone.app.contenttypes.content import NewsItem
from plone.app.contenttypes.migration import dxmigration
from plone.app.contenttypes.migration import migration
from plone.app.contenttypes.migration.patches import patch_before_migration
from plone.app.contenttypes.migration.patches import undo_patch_after_migration
from plone.app.contenttypes.migration.utils import installTypeIfNeeded
from plone.app.contenttypes.migration.utils import isSchemaExtended
from plone.app.contenttypes.migration.utils import restore_references
from plone.app.contenttypes.migration.utils import store_references
from plone.app.contenttypes.migration.vocabularies import ATCT_LIST
from plone.app.contenttypes.upgrades import use_new_view_names
from plone.app.contenttypes.utils import DEFAULT_TYPES
from plone.browserlayer.interfaces import ILocalBrowserLayerType
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.z3cform.layout import wrap_form
from pprint import pformat
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import get_installer
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.interfaces import HIDDEN_MODE
from zExceptions import NotFound
from zope import schema
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import Interface

import logging
import pkg_resources


try:
    pkg_resources.get_distribution('collective.contentleadimage')
except pkg_resources.DistributionNotFound:
    HAS_CONTENTLEADIMAGE = False
else:
    HAS_CONTENTLEADIMAGE = True

logger = logging.getLogger(__name__)


# Average time to migrate one archetype object, in milliseconds.
# This very much depends on the size of the object and system-speed
ONE_OBJECT_MIGRATION_TIME = 500


class FixBaseClasses(BrowserView):

    def __call__(self):
        """Make sure all content objects use the proper base classes.
        Instances before version 1.0b1 had no base-class.
        To update them call @@fix_base_classes on your site-root.
        """
        out = ''
        portal_types = [
            ('Document', Document),
            ('File', File),
            ('Folder', Folder),
            ('Image', Image),
            ('Link', Link),
            ('News Item', NewsItem),
        ]
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {}
        for portal_type, portal_type_class in portal_types:
            query['portal_type'] = portal_type
            results = catalog(query)
            for brain in results:
                try:
                    obj = brain.getObject()
                except (KeyError, NotFound):
                    logger.exception('Can not resolve object from brain.')
                    continue
                if IDexterityContent.providedBy(obj):
                    object_class_name = obj.__class__.__name__
                    target_class_name = portal_type_class.__name__
                    if not object_class_name == target_class_name:
                        obj.__class__ = portal_type_class
                        out += 'Make {0} use {1}\n as base class.'.format(
                            obj.Title(),
                            portal_type_class.__name__,
                        )
        return out


class MigrateFromATContentTypes(BrowserView):
    """Migrate the default-types (except event and topic).
    This view can be called directly and it will migrate all content
    provided they were not schema-extended.
    This is also called by the migration-form below with some variables.
    """

    def __call__(self,
                 migrate=False,
                 content_types='all',
                 migrate_schemaextended_content=False,
                 migrate_references=True,
                 from_form=False,
                 reindex_catalog=True,
                 patch_searchabletext=False,
                 ):

        portal = self.context

        if not from_form and migrate not in ['1', 'True', 'true', 1]:
            url1 = '{0}/@@migrate_from_atct?migrate=1'.format(
                portal.absolute_url())
            url2 = '{0}/@@atct_migrator'.format(portal.absolute_url())
            msg = u'Warning \n'
            msg += u'-------\n'
            msg += u'You are accessing "@@migrate_from_atct" directly. '
            msg += u'This will migrate all content to dexterity!\n\n'
            msg += u'Really migrate all content now: {0}\n\n'.format(url1)
            msg += u'First select what to migrate: {0}'.format(url2)
            return msg

        helpers = getMultiAdapter((portal, self.request),
                                  name='atct_migrator_helpers')
        if helpers.linguaplone_installed():
            msg = 'Warning\n'
            msg += 'Migration aborted since Products.LinguaPlone is '
            msg += 'installed. See '
            msg += 'http://github.com/plone/plone.app.contenttypes#migration '
            msg += 'for more information.'
            return msg

        stats_before = self.stats()
        starttime = datetime.now()

        self.request['plone.app.contenttypes_migration_running'] = True

        msg = 'Starting Migration\n\n'
        msg += '\n-----------------------------\n'
        msg += 'Content statictics:\n'
        msg += pformat(stats_before)
        msg += '\n-----------------------------\n'
        msg += 'Types to be migrated:\n'
        msg += pformat(content_types)
        msg += '\n-----------------------------\n'
        logger.info(msg)

        # store references on the portal
        if migrate_references:
            store_references(portal)
        catalog = portal.portal_catalog

        # Patch various things that make migration harder
        (link_integrity,
         queue_indexing,
         patch_searchabletext) = patch_before_migration(patch_searchabletext)

        not_migrated = []
        migrated_types = {}

        for (k, v) in ATCT_LIST.items():
            if content_types != 'all' and k not in content_types:
                not_migrated.append(k)
                continue
            # test if the ct is extended beyond blobimage and blobfile
            if len(isSchemaExtended(v['iface'])) > len(v['extended_fields']) \
                    and not migrate_schemaextended_content:
                not_migrated.append(k)
                continue
            query = {
                'object_provides': v['iface'].__identifier__,
                'meta_type': v['old_meta_type'],
            }
            amount_to_be_migrated = len(catalog(query))
            starttime_for_current = datetime.now()
            logger.info(
                'Start migrating {0} objects from {1} to {2}'.format(
                    amount_to_be_migrated,
                    v['old_meta_type'],
                    v['type_name'],
                )
            )
            installTypeIfNeeded(v['type_name'])

            # call the migrator
            v['migrator'](portal)

            # logging
            duration_current = datetime.now() - starttime_for_current
            duration_human = str(timedelta(seconds=duration_current.seconds))
            logger.info(
                'Finished migrating {0} objects from {1} to {2} in {3}'.format(
                    amount_to_be_migrated,
                    v['old_meta_type'],
                    v['type_name'],
                    duration_human),
            )

            # some data for the results-page
            migrated_types[k] = {}
            migrated_types[k]['amount_migrated'] = amount_to_be_migrated
            migrated_types[k]['old_meta_type'] = v['old_meta_type']
            migrated_types[k]['type_name'] = v['type_name']

        # if there are blobnewsitems we just migrate them silently.
        migration.migrate_blobnewsitems(portal)

        # make sure the view-methods on the plone site are updated
        use_new_view_names(portal, types_to_fix=['Plone Site'])

        if reindex_catalog:
            catalog.clearFindAndRebuild()

        # restore references
        if migrate_references:
            restore_references(portal)

        # Revert to the original state
        undo_patch_after_migration(
            link_integrity, queue_indexing, patch_searchabletext)

        duration = str(timedelta(seconds=(datetime.now() - starttime).seconds))
        if not_migrated:
            msg = (
                'The following types were not migrated: \n {0}'.format(
                    '\n'.join(not_migrated)
                )
            )
        else:
            msg = 'Migration successful\n\n'
        msg += '\n-----------------------------\n'
        msg += 'Migration finished in: {0}'.format(duration)
        msg += '\n-----------------------------\n'
        msg += 'Migration statictics:\n'
        msg += pformat(migrated_types)
        msg += '\n-----------------------------\n'
        msg += 'State before:\n'
        msg += pformat(stats_before)
        msg += '\n-----------------------------\n'
        msg += 'Stats after:\n'
        msg += pformat(self.stats())
        msg += '\n-----------------------------\n'
        if not from_form:
            logger.info(msg)
            return msg
        else:
            stats = {
                'duration': duration,
                'before': stats_before,
                'after': self.stats(),
                'content_types': content_types,
                'migrated_types': migrated_types,
            }
            logger.info(msg)
            return stats

    def stats(self):
        results = {}
        catalog = self.context.portal_catalog
        for brain in catalog():
            try:
                classname = brain.getObject().__class__.__name__
            except (KeyError, NotFound):
                continue
            results[classname] = results.get(classname, 0) + 1
        return results


class IATCTMigratorForm(Interface):

    content_types = schema.List(
        title=u'Existing content that can be migrated',
        description=u'Select which content types you want to migrate',
        value_type=schema.Choice(
            vocabulary='plone.app.contenttypes.migration.atctypes',
        ),
        required=False,
    )

    migrate_references = schema.Bool(
        title=u'Migrate references?',
        description=(
            u'Select this option to migrate references.'
        ),
        default=True,
        required=False,
    )

    extended_content = schema.List(
        title=(
            u'Migrate content that was extended '
            u'using archetypes.schemaextender?'
        ),
        description=(
            u'Warning: You will loose all data in the extended fields!'
        ),
        value_type=schema.Choice(
            vocabulary='plone.app.contenttypes.migration.extendedtypes',
        ),
        required=False,
    )

    reindex_catalog = schema.Bool(
        title=_(u'Rebuild the catalog after the migration.'),
        description=_(u'This operation can take a very long time.'),
        default=True,
        required=False,
    )

    patch_searchabletext = schema.Bool(
        title=_(u'Disable reindexing objects during migration?'),
        description=_(
            u'This can speed up your migration a lot if you have a lot of files with searchable text.'  # noqa: E501
        ),
        default=False,
        required=False,
    )


class ATCTMigratorForm(form.Form):
    template = ViewPageTemplateFile('atct_migrator.pt')
    results_template = ViewPageTemplateFile('atct_migrator_results.pt')

    fields = field.Fields(IATCTMigratorForm)
    fields['content_types'].widgetFactory = CheckBoxFieldWidget
    fields['extended_content'].widgetFactory = CheckBoxFieldWidget
    ignoreContext = True
    enableCSRFProtection = True

    results = None

    @button.buttonAndHandler(u'Migrate', name='migrate')
    def handle_migrate(self, action):
        data, errors = self.extractData()
        context = self.context

        if errors:
            return

        content_types = data['content_types'] or []
        content_types.extend(data['extended_content'] or [])

        migration_view = getMultiAdapter(
            (context, self.request),
            name=u'migrate_from_atct'
        )
        # store results where `render` can find them
        self.results = migration_view(
            content_types=content_types,
            migrate_schemaextended_content=True,
            migrate_references=data['migrate_references'],
            from_form=True,
            reindex_catalog=data['reindex_catalog'],
            patch_searchabletext=data['patch_searchabletext'],
        )

    def updateActions(self):
        super(ATCTMigratorForm, self).updateActions()
        self.actions['migrate'].addClass('btn-danger')

    def updateWidgets(self):
        """ Overload to set defaults and hide empty widgets. """
        form.Form.updateWidgets(self)
        # 1. Select all items in the checkboxwidget
        ct_widget = self.widgets['content_types']
        # Only override when rendering the form. When you unselect
        # everything the value will be [], not ())
        if ct_widget.value == ():
            ct_widget.value = list(ATCT_LIST)
            # Call update again since the list-items checked-states are
            # assigned in z3c.form.browser.checkbox.CheckBoxWidget.update
            # using the widget.value.
            ct_widget.update()
        # 2. Hide empty widget
        for title, widget in self.widgets.items():
            if title not in ('content_types', 'extended_content'):
                continue
            if not len(widget.items):
                # the vocabulary is empty, we hide the widget
                widget.mode = HIDDEN_MODE

    def render(self):
        if self.results:
            return self.results_template()
        else:
            return super(ATCTMigratorForm, self).render()


class IBaseClassMigratorForm(Interface):

    changed_base_classes = schema.List(
        title=u'Changed base classes',
        description=u'Select changed base classes you want to migrate',
        value_type=schema.Choice(
            vocabulary='plone.app.contenttypes.migration.changed_base_classes',
        ),
        required=True,
    )
    migrate_to_folderish = schema.Bool(
        title=u'Migrate to folderish type?',
        description=(
            u'Select this option if you changed a type from being '
            u'itemish to being folderish but the class of the type is still '
            u'the same.'
        ),
        default=False,
    )


class BaseClassMigratorForm(form.Form):

    fields = field.Fields(IBaseClassMigratorForm)
    fields['changed_base_classes'].widgetFactory = CheckBoxFieldWidget
    ignoreContext = True
    enableCSRFProtection = True

    @button.buttonAndHandler(u'Update', name='update')
    def handle_migrate(self, action):
        data, errors = self.extractData()

        if errors:
            return

        changed_base_classes = data.get('changed_base_classes', [])
        if not changed_base_classes:
            return

        migrate_to_folderish = data.get('changed_base_classes', False)
        catalog = getToolByName(self.context, 'portal_catalog')
        migrated = []
        not_migrated = []
        for brain in catalog():
            try:
                obj = brain.getObject()
            except (KeyError, NotFound):
                continue
            old_class_name = dxmigration.get_old_class_name_string(obj)
            if old_class_name in changed_base_classes:
                if dxmigration.migrate_base_class_to_new_class(
                        obj, migrate_to_folderish=migrate_to_folderish):
                    migrated.append(obj)
                else:
                    not_migrated.append(obj)

        messages = IStatusMessage(self.request)
        info_message_template = 'There are {0} objects migrated.'
        warn_message_template = 'There are not {0} objects migrated.'
        if migrated:
            msg = info_message_template.format(len(migrated))
            messages.addStatusMessage(msg, type='info')
        if not_migrated:
            msg = warn_message_template.format(len(not_migrated))
            messages.addStatusMessage(msg, type='warn')
        self.request.response.redirect(self.request['ACTUAL_URL'])


BaseClassMigrator = wrap_form(
    BaseClassMigratorForm,
)


class ATCTMigratorHelpers(BrowserView):

    def objects_to_be_migrated(self):
        """ Return the number of AT objects in the portal """
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {'meta_type': [i['old_meta_type'] for i in ATCT_LIST.values()]}
        brains = catalog(query)
        self._objects_to_be_migrated = len(brains)
        return self._objects_to_be_migrated

    def estimated_migration_time(self):
        """ Return the estimated migration time """
        total_time = self.objects_to_be_migrated() * ONE_OBJECT_MIGRATION_TIME
        hours, remainder = divmod(total_time // 1000, 3600)
        minutes, seconds = divmod(remainder, 60)
        return {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds
        }

    def linguaplone_installed(self):
        """Is Products.LinguaPlone installed?
        """
        existing = queryUtility(ILocalBrowserLayerType, name='LinguaPlone')
        return bool(existing)

    def site_has_subtopics(self):
        """Check if there are subtopics. Since Collections are itemish by
        default the migration of subtopics would fail Collections are changed
        to be folderish.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {'meta_type': 'ATTopic'}
        results = []
        brains = catalog(query)
        for brain in brains:
            for item in catalog(path={'query': brain.getPath(), 'depth': 1}):
                results.append(item.getURL())
        if results:
            results = set(results)
            paths = '\n'.join(results)
            logger.info('Found {0} subtopics at: \n{1}'.format(
                len(results), paths))
            return results

    def collections_are_folderish(self):
        """Since Collections are itemish by default the migration would fail
        if there are any subtopics. As a workaround we allow to migrate to
        custom folderish Collections. The custom Collections have to fulfill
        the following criteria:
        1. The id if the type has to be Collection (not collection). You can
           change a type's id in portal_types
        2. The type has to have the collection-behavior.

        This much can even be done ttw. For the views of collections
        to work the base-class of the Collections also has to implement the
        interface `plone.app.contenttypes.interfaces.ICollection`.

        This is what such a class would look like:

            from plone.app.contenttypes.behaviors.collection import ICollection
            from plone.dexterity.content import Container
            from zope.interface import implementer

            @implementer(ICollection)
            class FolderishCollection(Container):
                pass

        You can either use a completely new fti or overwrite the default fti
        like this:

            <?xml version="1.0"?>
            <object name="Collection" meta_type="Dexterity FTI">
             <property name="klass">my.package.content.FolderishCollection
             </property>
            </object>

        """
        fti = queryUtility(IDexterityFTI, name='Collection')
        if fti and fti.content_meta_type == 'Dexterity Container':
            return True
        # test for lowercase ttw-type
        fti = queryUtility(IDexterityFTI, name='collection')
        behavior = 'plone.app.contenttypes.behaviors.collection.ICollection'
        if fti and behavior in fti.behaviors:
            logger.warn("You are trying to migrate topic to collection. "
                        "Instead you need a type 'Collection'.")

    def has_contentleadimage(self):
        return HAS_CONTENTLEADIMAGE

    def installed_types(self):
        """Which types are already Dexterity and which are not."""
        results = {}
        results['installed_with_behavior'] = []
        results['installed_without_behavior'] = []
        results['not_installed'] = []
        behavior = 'plone.app.contenttypes.behaviors.leadimage.ILeadImage'
        for type_name in DEFAULT_TYPES:
            fti = queryUtility(IDexterityFTI, name=type_name)
            if fti:
                if behavior in fti.behaviors:
                    results['installed_with_behavior'].append(type_name)
                else:
                    results['installed_without_behavior'].append(type_name)
            else:
                results['not_installed'].append(type_name)
        return results


class PACInstaller(form.Form):
    """Install p.a.c and redirect to migration-form."""

    fields = field.Fields()
    template = ViewPageTemplateFile('pac_installer.pt')
    enableCSRFProtection = True

    @property
    def pac_installable(self):
        qi = get_installer(self.context)
        pac_installed = qi.is_product_installed('plone.app.contenttypes')
        pac_installable = qi.is_product_installable('plone.app.contenttypes')
        return pac_installable and not pac_installed

    @property
    def pac_installed(self):
        qi = get_installer(self.context)
        return qi.is_product_installed('plone.app.contenttypes')

    @button.buttonAndHandler(_(u'Install'), name='install')
    def handle_install(self, action):
        """ install p.a.c
        """
        url = self.context.absolute_url()
        portal_setup = getToolByName(self.context, 'portal_setup')
        portal_setup.runAllImportStepsFromProfile(
            'profile-plone.app.contenttypes:default',
            blacklisted_steps=['typeinfo'],
        )

        # For types without any instances we want to instantly
        # replace the AT-FTI's with DX-FTI's.
        self.installTypesWithoutItems()

        url = url + '/@@atct_migrator'
        self.request.response.redirect(url)

    def installTypesWithoutItems(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        for types_name in DEFAULT_TYPES:
            if not catalog.unrestrictedSearchResults(portal_type=types_name):
                installTypeIfNeeded(types_name)

    @button.buttonAndHandler(
        _(u'label_cancel', default=u'Cancel'), name='cancel')
    def handle_cancel(self, action):
        self.request.response.redirect(self.context.absolute_url())
