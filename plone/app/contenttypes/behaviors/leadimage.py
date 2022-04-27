from plone.app.contenttypes import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider


class ILeadImage(Interface):
    pass


@provider(IFormFieldProvider)
class ILeadImageBehavior(model.Schema):

    image = namedfile.NamedBlobImage(
        title=_("label_leadimage", default="Lead Image"),
        description="",
        required=False,
    )

    image_caption = schema.TextLine(
        title=_("label_leadimage_caption", default="Lead Image Caption"),
        description="",
        required=False,
    )


@implementer(ILeadImageBehavior)
@adapter(IDexterityContent)
class LeadImage:
    def __init__(self, context):
        self.context = context

    @property
    def image(self):
        return self.context.image

    @image.setter
    def image(self, value):
        self.context.image = value

    @property
    def image_caption(self):
        return self.context.image_caption

    @image_caption.setter
    def image_caption(self, value):
        self.context.image_caption = value
