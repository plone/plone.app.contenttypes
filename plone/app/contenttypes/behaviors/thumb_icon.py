# -*- coding: utf-8 -*-
from plone.app.contenttypes import _
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IThumbIconHandling(model.Schema):

    model.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=[
            'thumb_scale_list',
            'thumb_scale_table',
            'thumb_scale_summary',
            'suppress_icons',
            'suppress_thumbs'
        ]
    )

    thumb_scale_list = schema.TextLine(
        title=_(u'Override thumb scale for list view'),
        description=_(
            u"Enter a valid scale name"
            u" (see 'Image Handling' control panel) to override"
            u" (e.g. icon, tile, thumb, mini, preview, ... )."
            u" Leave empty to use default (see 'Site' control panel)."
        ),
        required=False,
        default=u'')

    thumb_scale_table = schema.TextLine(
        title=_(u'Override thumb scale for table view'),
        description=_(
            u"Enter a valid scale name"
            u" (see 'Image Handling' control panel) to override"
            u" (e.g. icon, tile, thumb, mini, preview, ... )."
            u" Leave empty to use default (see 'Site' control panel)."
        ),
        required=False,
        default=u'')

    thumb_scale_summary = schema.TextLine(
        title=_(u'Override thumb scale for summary view'),
        description=_(
            u"Enter a valid scale name"
            u" (see 'Image Handling' control panel) to override"
            u" (e.g. icon, tile, thumb, mini, preview, ... )."
            u" Leave empty to use default (see 'Site' control panel)."
        ),
        required=False,
        default=u'')

    suppress_icons = schema.Bool(
        title=_(u'Suppress icons in list, table or summary view'),
        description=_(u''),
        required=False,
        default=False,
    )

    suppress_thumbs = schema.Bool(
        title=_(u'Suppress thumbs in list, table or summary view'),
        required=False,
        default=False,
    )

    directives.omitted(
        'thumb_scale_list',
        'thumb_scale_table',
        'thumb_scale_summary',
        'suppress_icons',
        'suppress_thumbs'
    )
    directives.no_omit(
        IEditForm,
        'thumb_scale_list',
        'thumb_scale_table',
        'thumb_scale_summary',
        'suppress_icons',
        'suppress_thumbs'
    )
    directives.no_omit(
        IAddForm,
        'thumb_scale_list',
        'thumb_scale_table',
        'thumb_scale_summary',
        'suppress_icons',
        'suppress_thumbs'
    )
