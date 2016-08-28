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
        label=_(u"Settings"),
        fields=['ov_thumbsize_list',
                'ov_thumbsize_table',
                'ov_thumbsize_summary',
                'suppress_icons',
                'suppress_thumbs'
               ]    
    )
    
    ov_thumbsize_list = schema.TextLine(
        title=_(u"Override thumb size for list view"),
        description=_(u"<br><ul><li>  valid size (see 'Image Handling' control panel)"
                      u" e.g. icon, tile, thumb, mini, preview, ... ,  </li>"
                      u"<li>leave empty to use default (see 'Site' control panel)</li></ul>"),
        required=False,
        default=u'')

    
    ov_thumbsize_table = schema.TextLine(
        title=_(u"Override thumb size for table view"),
        description=_(u"<br><ul><li>   valid size (see 'Image Handling' control panel)"
                      u" e.g. icon, tile, thumb, mini, preview, ... ,  </li>"
                      u"<li>leave empty to use default (see 'Site' control panel)</li></ul>"),
        required=False,
        default=u'')
            
    ov_thumbsize_summary = schema.TextLine(
        title=_(u"Override thumb size for summary view"),
        description=_(u"<br><ul><li>  valid size (see 'Image Handling' control panel)"
                      u" e.g. icon, tile, thumb, mini, preview, ... ,  </li>"
                      u"<li>leave empty to use default (see 'Site' control panel)</li></ul>"),
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
        description=_(u''),
        required=False,
        default=False,
    )

    directives.omitted('ov_thumbsize_list',
                       'ov_thumbsize_table',
                       'ov_thumbsize_summary',
                       'suppress_icons',
                       'suppress_thumbs'
                       )
    directives.no_omit(IEditForm,'ov_thumbsize_list',
                                 'ov_thumbsize_table',
                                 'ov_thumbsize_summary',
                                 'suppress_icons',
                                 'suppress_thumbs'
                                 )
    directives.no_omit(IAddForm,'ov_thumbsize_list',
                                 'ov_thumbsize_table',
                                 'ov_thumbsize_summary',
                                 'suppress_icons',
                                 'suppress_thumbs'
                                 )

