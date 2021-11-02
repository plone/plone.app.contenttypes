from plone.app.contenttypes.content import Document
from plone.app.contenttypes.content import File
from plone.app.contenttypes.content import Folder
from plone.app.contenttypes.content import Image
from plone.app.contenttypes.content import Link
from plone.app.contenttypes.content import NewsItem
from plone.app.contenttypes.utils import DEFAULT_TYPES
from plone.app.contenttypes.utils import get_old_class_name_string
from plone.app.contenttypes.utils import migrate_base_class_to_new_class
from plone.app.contenttypes.utils import list_of_changed_base_class_names
from plone.browserlayer.interfaces import ILocalBrowserLayerType
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.z3cform.layout import wrap_form
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
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implementer

import logging
import pkg_resources


logger = logging.getLogger(__name__)



@implementer(IVocabularyFactory)
class ChangedBaseClasses(object):

    def __call__(self, context):
        """Return a vocabulary with all changed base classes."""
        list_of_class_names = list_of_changed_base_class_names(context) or {}
        return SimpleVocabulary(
            [SimpleVocabulary.createTerm(
                class_name, class_name,
                '{0} ({1})'.format(
                    class_name, list_of_class_names[class_name]))
             for class_name in list_of_class_names.keys()]
        )


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
            old_class_name = get_old_class_name_string(obj)
            if old_class_name in changed_base_classes:
                if migrate_base_class_to_new_class(
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
