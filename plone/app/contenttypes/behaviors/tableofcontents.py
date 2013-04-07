# -*- coding: utf-8 -*-
from zope.interface import alsoProvides, implements
from zope.component import adapts
from zope import schema
from plone.supermodel import model
from plone.dexterity.interfaces import IDexterityContent
from plone.autoform.interfaces import IFormFieldProvider

from plone.app.contenttypes import _


class ITableOfContents(model.Schema):

    table_of_contents = schema.Bool(
        title=_(
            u'help_enable_table_of_contents',
            default=u'Table of contents'),
        description=_(
            u'help_enable_table_of_contents_description',
            default=u'If selected, this will show a table of contents at the top of the page.'),
        required=False,
    )

alsoProvides(ITableOfContents, IFormFieldProvider)
