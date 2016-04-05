# -*- coding: utf-8 -*-
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


@provider(IFormFieldProvider)
class ILeadImage(model.Schema):

    image = namedfile.NamedBlobImage(
        title=_(u'label_leadimage', default=u'Lead Image'),
        description=_(u'help_leadimage', default=u''),
        required=False,
    )

    image_caption = schema.TextLine(
        title=_(u'label_leadimage_caption', default=u'Lead Image Caption'),
        description=_(u'help_leadimage_caption', default=u''),
        required=False,
    )


@implementer(ILeadImage)
@adapter(IDexterityContent)
class LeadImage(object):

    def __init__(self, context):
        self.context = context


class ILeadImageSettings(Interface):

    scale_name = schema.Choice(
        title=_(u"Image scale"),
        description=_(u'Please select scale which will be used.'),
        required=True,
        default='mini',
        vocabulary=u"plone.app.vocabularies.ImagesScales",
    )

    is_visible = schema.Bool(
        title=_(u'Show image in content'),
        default=True,
    )
