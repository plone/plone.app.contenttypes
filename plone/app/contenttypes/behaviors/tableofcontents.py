# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import provider


_ = MessageFactory('plone')


@provider(IFormFieldProvider)
class ITableOfContents(model.Schema):

    model.fieldset('settings', label=_(u'Settings'),
                   fields=['table_of_contents'])

    table_of_contents = schema.Bool(
        title=_(
            u'help_enable_table_of_contents',
            default=u'Table of contents'),
        description=_(
            u'help_enable_table_of_contents_description',
            default=u'If selected, this will show a table of contents'
                    u' at the top of the page.'),
        required=False,
    )
