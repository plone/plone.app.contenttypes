# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.contenttypes.migration import migration
from plone.app.contenttypes.migration.utils import ATCT_LIST
from plone.app.contenttypes.migration.utils import isSchemaExtended
from plone.dexterity.interfaces import IDexterityContent
from plone.z3cform.layout import wrap_form
from pprint import pformat
from z3c.form import form, field, button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.component import queryUtility
from zope.interface import Interface
from plone.app.blob.interfaces import IATBlobImage
from plone.app.blob.interfaces import IATBlobFile

# Old interfaces

# Schema Extender allowed interfaces

from plone.app.contenttypes.content import (
    Document,
    File,
    Folder,
    Image,
    Link,
    NewsItem,
)


class FixBaseClasses(BrowserView):

    def __call__(self):
        """Make sure all content objects use the proper base classes.
           Instances before version 1.0b1 had no base-class.
           To update them call @@fix_base_classes on your site-root.
        """
        out = ""
        portal_types = [
            ('Document', Document),
            ('File', File),
            ('Folder', Folder),
            ('Image', Image),
            ('Link', Link),
            ('News Item', NewsItem),
        ]
        catalog = getToolByName(self.context, "portal_catalog")
        for portal_type, portal_type_class in portal_types:
            results = catalog.searchResults(portal_type=portal_type)
            for brain in results:
                obj = brain.getObject()
                if IDexterityContent.providedBy(obj):
                    object_class_name = obj.__class__.__name__
                    target_class_name = portal_type_class.__name__
                    if not object_class_name == target_class_name:
                        obj.__class__ = portal_type_class
                        out += "Make %s use %s\n as base class." % (
                            obj.Title(),
                            portal_type_class.__name__,
                        )
        return out


class MigrateFromATContentTypes(BrowserView):
    """ Migrate the default-types (except event and topic)
    """

    def __call__(self,
                 types_not_to_migrate=[],
                 migrate_schemaextended_content=True):
        stats_before = 'State before:\n'
        stats_before += self.stats()
        portal = self.context

        # switch linkintegrity temp off
        ptool = queryUtility(IPropertiesTool)
        site_props = getattr(ptool, 'site_properties', None)
        link_integrity = site_props.getProperty('enable_link_integrity_checks',
                                                False)
        site_props.manage_changeProperties(enable_link_integrity_checks=False)

        # Check whether any of the default content types have had their
        # schemas extended
        not_migrated = []
        for (k, v) in ATCT_LIST.items():
            if k in types_not_to_migrate:
                not_migrated.append(k)
                continue
            if isSchemaExtended(v['iface']) and not migrate_schemaextended_content:
                not_migrated.append(k)
                continue
            v['migrator'](portal)

        default_blob_types = {
            "BlobImage": {
                'iface': IATBlobImage,
                'migrator': migration.migrate_blobimages
            },
            "BlobFile": {
                'iface': IATBlobFile,
                'migrator': migration.migrate_blobfiles
            },
        }

        for (k, v) in default_blob_types.items():
            if len(isSchemaExtended(v['iface'])) > 1 \
                    and not migrate_schemaextended_content:
                not_migrated.append(k)
            else:
                v['migrator'](portal)

        # TODO: migration.migrate_blobnewsitems(portal)

        migration.restoreReferences(portal)
        migration.restoreReferencesOrder(portal)

        # switch linkintegrity back
        site_props.manage_changeProperties(
            enable_link_integrity_checks=link_integrity
        )

        if not_migrated:
            msg = ("The following cannot be migrated as they "
                   "have extended schemas (from "
                   "archetypes.schemaextender): \n %s"
                   % "\n".join(not_migrated))
        else:
            msg = "Default content types successfully migrated\n\n"

        msg += '\n-----------------------------\n'
        msg += stats_before
        msg += '\n-----------------------------\n'
        msg += 'Stats after:\n'
        msg += self.stats()
        msg += '\n-----------------------------\n'
        msg += 'migration done - somehow. Be careful!'
        return msg

    def stats(self):
        results = {}
        for brain in self.context.portal_catalog():
            classname = brain.getObject().__class__.__name__
            results[classname] = results.get(classname, 0) + 1
        return pformat(sorted(results.items()))


class IATCTMigratorForm(Interface):

    content_types = schema.List(
        title=u"Existing content that can be migrated",
        description=u"Select which content types you want to migrate",
        value_type=schema.Choice(
            vocabulary="plone.app.contenttypes.migration.atcttypes",
        )
    )

    migrate_references = schema.Bool(
        title=u"Migrate references?",
        description=(
            u"Select this option to migrate all "
            u"references to each content type"
        ),
        default=True
    )

    migrate_schemaextended_content = schema.Bool(
        title=(
            u"Migrate content that was extended "
            u"trough archetypes.schemaextender?"
        ),
        description=(
            u"Please, pay attention. You will lose the data "
            u"in the in the extended Fields"
        ),
        default=False
    )


class ATCTMigratorForm(form.Form):

    fields = field.Fields(IATCTMigratorForm)
    fields['content_types'].widgetFactory = CheckBoxFieldWidget
    ignoreContext = True

    @button.buttonAndHandler(u'Migrate', name='migrate')
    def handle_migrate(self, action):
        data, errors = self.extractData()

        if errors:
            return

        migrate_references = data['migrate_references']
        migrate_schemaextended_content = data['migrate_schemaextended_content']
        portal = self.context
        res = []
        for ct in data['content_types']:
            el = ATCT_LIST.get(ct)
            if not el:
                continue

            if not migrate_schemaextended_content and \
                    isSchemaExtended(el['iface']):
                continue

            res.append(el['migrator'](portal))

        if migrate_references:
            res.append(migration.restoreReferences(portal))
            res.append(migration.restoreReferencesOrder(portal))

    def updateActions(self):
        super(ATCTMigratorForm, self).updateActions()
        self.actions['migrate'].addClass("btn-danger")


ATCTMigrator = wrap_form(
    ATCTMigratorForm,
    index=ViewPageTemplateFile('atct_migrator.pt')
)


class ATCTMigratorResults(BrowserView):
    pass
