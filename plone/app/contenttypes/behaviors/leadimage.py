# -*- coding: utf-8 -*-
from plone.app.contenttypes import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from zope.interface import Interface


class ILeadImage(Interface):
    pass


@provider(IFormFieldProvider)
class ILeadImageBehavior(model.Schema):

    image = namedfile.NamedBlobImage(
        title=_(u'label_leadimage', default=u'Lead Image'),
        description=u'',
        required=False,
    )

    image_caption = schema.TextLine(
        title=_(u'label_leadimage_caption', default=u'Lead Image Caption'),
        description=u'',
        required=False,
    )


@implementer(ILeadImageBehavior)
@adapter(IDexterityContent)
class LeadImage(object):

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
