from plone.app.contenttypes.content import Document
from plone.app.contenttypes.content import File
from plone.app.contenttypes.content import Folder
from plone.app.contenttypes.content import Image
from plone.app.contenttypes.content import Link
from plone.app.contenttypes.content import NewsItem
from plone.app.contenttypes.utils import changed_base_classes
from plone.app.contenttypes.utils import DEFAULT_TYPES
from plone.app.contenttypes.utils import get_old_class_name_string
from plone.app.contenttypes.utils import migrate_base_class_to_new_class
from plone.base import PloneMessageFactory as _
from plone.base.utils import get_installer
from plone.browserlayer.interfaces import ILocalBrowserLayerType
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.z3cform.layout import wrap_form
from Products.CMFCore.utils import getToolByName
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
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

import logging
import pkg_resources


logger = logging.getLogger(__name__)


@implementer(IVocabularyFactory)
class ChangedBaseClasses:
    def __call__(self, context):
        """Return a vocabulary with all changed base classes."""
        terms = []
        for class_name, data in changed_base_classes(context).items():
            title = "{} (➡ {}) - ({} items)".format(
                data["old"], data["new"], data["amount"]
            )
            term = SimpleVocabulary.createTerm(class_name, class_name, title)
            terms.append(term)
        return SimpleVocabulary(terms)


class IBaseClassMigratorForm(Interface):

    changed_base_classes = schema.List(
        title="Changed base classes (old class, new class and number of items)",
        description="Select changed base classes you want to migrate. "
        "If the new types are folderish that change is also applied.",
        value_type=schema.Choice(
            vocabulary="plone.app.contenttypes.migration.changed_base_classes",
        ),
        default=[],
        required=True,
    )


class BaseClassMigratorForm(form.Form):

    label = _(
        "heading_class_migrator",
        default="Update base-classes for content with changed classes",
    )

    fields = field.Fields(IBaseClassMigratorForm)
    fields["changed_base_classes"].widgetFactory = CheckBoxFieldWidget
    ignoreContext = True
    enableCSRFProtection = True

    def updateWidgets(self):
        super().updateWidgets()
        changed_base_classes = self.widgets["changed_base_classes"]
        if not changed_base_classes.terms.terms.by_value:
            IStatusMessage(self.request).addStatusMessage(
                "No types with changed classes to migrate!", type="warning"
            )
            return

    @button.buttonAndHandler("Update", name="update")
    def handle_migrate(self, action):
        data, errors = self.extractData()

        if errors:
            return

        changed_base_classes = data.get("changed_base_classes", [])
        messages = IStatusMessage(self.request)
        if not changed_base_classes:
            messages.addStatusMessage("No types were selected", type="warning")
            return

        catalog = getToolByName(self.context, "portal_catalog")
        migrated = []
        not_migrated = []
        for brain in catalog():
            try:
                obj = brain.getObject()
            except (KeyError, NotFound):
                continue
            old_class_name = get_old_class_name_string(obj)
            if old_class_name in changed_base_classes:
                if migrate_base_class_to_new_class(obj, migrate_to_folderish=True):
                    migrated.append(obj)
                else:
                    not_migrated.append(obj)

        info_message_template = "{0} objects were migrated."
        warn_message_template = "{0} objects were not migrated."
        if migrated:
            msg = info_message_template.format(len(migrated))
            messages.addStatusMessage(msg, type="info")
        if not_migrated:
            msg = warn_message_template.format(len(not_migrated))
            messages.addStatusMessage(msg, type="warning")
        self.request.response.redirect(self.request["ACTUAL_URL"])


BaseClassMigrator = wrap_form(
    BaseClassMigratorForm,
)
