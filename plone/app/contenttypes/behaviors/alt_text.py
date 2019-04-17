# -*- coding: utf-8 -*-
from plone.app.contenttypes import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from zope.interface import Interface


class IAltText(Interface):
    pass


@provider(IFormFieldProvider)
class IAltTextBehavior(model.Schema):

    alt_text = schema.TextLine(
        title=_('label_alt_text', default=u'Alt Text'),
        description=_(
            'label_alt_text_help',
            default=u'Briefly describe the meaning of the image for people'
                    u'using assistive technology like screen readers.'
                    u'This will be used when the image is viewed by itself.'
                    u'Do not duplicate the Title or Description fields, '
                    u'since they will also be read by screen readers.'
                    u'Alt text should describe what a sighted user sees '
                    u'when looking at the image.'
                    u'This might include text the image contains, or even '
                    u'a description of an abstract pattern.'
                    u'This field should never be left blank on sites that '
                    u'want to be compliant with accessibility standards.'
            ),
        required=False,
    )


@implementer(IAltTextBehavior)
@adapter(IDexterityContent)
class AltText(object):

    def __init__(self, context):
        self.context = context

    @property
    def alt_text(self):
        return self.context.alt_text

    @alt_text.setter
    def alt_text(self, value):
        self.context.alt_text = value
