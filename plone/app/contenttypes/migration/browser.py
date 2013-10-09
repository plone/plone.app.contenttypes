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
from zope.component import getMultiAdapter
from zope.interface import Interface

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

# time to migrate one archetype object, in milisecond
ONE_OBJECT_MIGRATION_TIME = 250

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
                 content_types="all",
                 migrate_schemaextended_content=False,
                 migrate_references=True,
                 from_form=False):

        stats_before = 'State before:\n'
        stats_before += self.stats()
        portal = self.context

        # switch linkintegrity temp off
        ptool = queryUtility(IPropertiesTool)
        site_props = getattr(ptool, 'site_properties', None)
        link_integrity = site_props.getProperty('enable_link_integrity_checks',
                                                False)
        site_props.manage_changeProperties(enable_link_integrity_checks=False)

        not_migrated = []
        for (k, v) in ATCT_LIST.items():
            if content_types != "all" and k not in content_types:
                not_migrated.append(k)
                continue
            if len(isSchemaExtended(v['iface'])) > len(v['extended_fields']) \
                    and not migrate_schemaextended_content:
                not_migrated.append(k)
                continue
            v['migrator'](portal)

        # TODO: migration.migrate_blobnewsitems(portal)
        if migrate_references:
            migration.restoreReferences(portal)
            migration.restoreReferencesOrder(portal)

        # switch linkintegrity back
        site_props.manage_changeProperties(
            enable_link_integrity_checks=link_integrity
        )

        if not from_form:
            if not_migrated:
                msg = ("The following were not migrated as they "
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
        else:
            return self.stats()

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
            vocabulary="plone.app.contenttypes.migration.atctypes",
        ),
        required=False,
    )

    migrate_references = schema.Bool(
        title=u"Migrate references?",
        description=(
            u"Select this option to migrate all "
            u"references to each content type"
        ),
        default=True
    )

    extended_content = schema.List(
        title=(
            u"Migrate content that was extended "
            u"using archetypes.schemaextender?"
        ),
        description=(
            u"Warning: You will loose all data in the extended fields!"
        ),
        value_type=schema.Choice(
            vocabulary="plone.app.contenttypes.migration.extendedtypes",
        ),
        required=False,
    )


class ATCTMigratorForm(form.Form):

    fields = field.Fields(IATCTMigratorForm)
    fields['content_types'].widgetFactory = CheckBoxFieldWidget
    fields['extended_content'].widgetFactory = CheckBoxFieldWidget
    ignoreContext = True

    @button.buttonAndHandler(u'Migrate', name='migrate')
    def handle_migrate(self, action):
        data, errors = self.extractData()

        if errors:
            return

        content_types = data['content_types']
        content_types.extend(data['extended_content'])

        migration_view = getMultiAdapter(
            (self.context, self.request),
            name=u'migrate_from_atct'
        )
        results = migration_view(
            content_types=content_types,
            migrate_schemaextended_content=True,
            migrate_references=data['migrate_references'],
            from_form=True,
        )
        return results

    def updateActions(self):
        super(ATCTMigratorForm, self).updateActions()
        self.actions['migrate'].addClass("btn-danger")


ATCTMigrator = wrap_form(
    ATCTMigratorForm,
    index=ViewPageTemplateFile('atct_migrator.pt')
)


class ATCTMigratorHelpers(BrowserView):
    
    def objects_to_be_migrated(self):
        """ Return the number of AT objects in the portal """
        catalog = getToolByName(self.context, "portal_catalog")         
        brains = catalog(portal_type = ATCT_LIST.keys())
        self._objects_to_be_migrated = len(brains)
        return self._objects_to_be_migrated

    def estimated_migration_time(self):
        """ Return the estimated migration time """
        total_time = self.objects_to_be_migrated() * ONE_OBJECT_MIGRATION_TIME
        hours, remainder = divmod(total_time / 1000, 3600)
        minutes, seconds = divmod(remainder, 6000)
        return {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds
        }


class ATCTMigratorResults(BrowserView):
    pass
