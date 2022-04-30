from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import provider


_ = MessageFactory("plone")


@provider(IFormFieldProvider)
class ITableOfContents(model.Schema):

    model.fieldset("settings", label=_("Settings"), fields=["table_of_contents"])

    table_of_contents = schema.Bool(
        title=_("help_enable_table_of_contents", default="Table of contents"),
        description=_(
            "help_enable_table_of_contents_description",
            default="If selected, this will show a table of contents"
            " at the top of the page.",
        ),
        required=False,
    )
