from Acquisition import aq_base
from plone.app.contenttypes import _
from plone.app.dexterity.textindexer import searchable
from plone.app.textfield import RichText as RichTextField
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform.view import WidgetsView
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider


class IRichText(Interface):
    pass


@provider(IFormFieldProvider)
class IRichTextBehavior(model.Schema):

    text = RichTextField(
        title=_("Text"),
        description="",
        required=False,
    )
    form.widget("text", RichTextFieldWidget)
    model.primary("text")
    searchable("text")


@implementer(IRichTextBehavior)
@adapter(IDexterityContent)
class RichText:
    def __init__(self, context):
        self.context = context

    @property
    def text(self):
        return getattr(aq_base(self.context), "text", "")

    @text.setter
    def text(self, value):
        self.context.text = value


class WidgetView(WidgetsView):
    schema = IRichTextBehavior
