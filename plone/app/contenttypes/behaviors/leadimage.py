from zope.interface import alsoProvides, implements
from zope.component import adapts
from zope import schema
from plone.supermodel import model
from plone.dexterity.interfaces import IDexterityContent
from plone.autoform.interfaces import IFormFieldProvider

from plone.namedfile import field as namedfile

from plone.app.contenttypes import MessageFactory as _


class ILeadImage(model.Schema):

    image = namedfile.NamedBlobImage(
        title=_(u"Lead Image"),
        description=u"",
        required=False,
    )

    image_caption = schema.TextLine(
        title=_(u"Lead Image Caption"),
        description=u"",
        required=False,
    )

alsoProvides(ILeadImage, IFormFieldProvider)


class LeadImage(object):
    implements(ILeadImage)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context
