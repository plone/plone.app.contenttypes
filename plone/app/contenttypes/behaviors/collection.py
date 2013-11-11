# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.querystring.querybuilder import QueryBuilder
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides, implements

from plone.app.contenttypes import _


class ICollection(model.Schema):

    query = schema.List(
        title=_(u'Search terms'),
        description=_(u"Define the search terms for the items you want "
                      u"to list by choosing what to match on. "
                      u"The list of results will be dynamically updated"),
        value_type=schema.Dict(value_type=schema.Field(),
                               key_type=schema.TextLine()),
        required=False
    )

    sort_on = schema.TextLine(
        title=_(u'label_sort_on', default=u'Sort on'),
        description=_(u"Sort the collection on this index"),
        required=False,
    )

    sort_reversed = schema.Bool(
        title=_(u'label_sort_reversed', default=u'Reversed order'),
        description=_(u'Sort the results in reversed order'),
        required=False,
    )

    limit = schema.Int(
        title=_(u'Limit'),
        description=_(u'Limit Search Results'),
        required=False,
        default=1000,
    )

    item_count = schema.Int(
        title=_(u'label_item_count', default=u'Item count'),
        description=_(u'Number of items that will show up in one batch.'),
        required=False,
        default=30,
    )

    #customViewFields = schema.Choice(
    #    title=_(u'label_sort_on', default=u'sortable_title'),
    #    description=_(u"Sort the collection on this index"),
    #    required=False,
    #    )


alsoProvides(ICollection, IFormFieldProvider)


class Collection(object):
    implements(ICollection)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def results(self, batch=True, b_start=0, b_size=None,
                sort_on=None, limit=None, brains=False):
        querybuilder = QueryBuilder(self.context, self.context.REQUEST)
        sort_order = 'reverse' if self.sort_reversed else 'ascending'
        if not b_size:
            b_size = self.item_count
        if not sort_on:
            sort_on = self.sort_on
        if not limit:
            limit = self.limit
        return querybuilder(
            query=self.query, batch=batch, b_start=b_start, b_size=b_size,
            sort_on=sort_on, sort_order=sort_order,
            limit=limit, brains=brains
        )

    def getFoldersAndImages(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = self.results(batch=False)

        _mapping = {'results': results, 'images': {}}
        portal_atct = getToolByName(self.context, 'portal_atct')
        image_types = getattr(portal_atct, 'image_types', [])

        for item in results:
            item_path = item.getPath()
            if item.isPrincipiaFolderish:
                query = {
                    'portal_type': image_types,
                    'path': item_path,
                }
                _mapping['images'][item_path] = IContentListing(catalog(query))
            elif item.portal_type in image_types:
                _mapping['images'][item_path] = [item, ]

        _mapping['total_number_of_images'] = sum(map(
            len,
            _mapping['images'].values()
        ))
        return _mapping

    # Getters and setters for our fields.

    def _set_sort_reversed(self, value):
        self.context.sort_reversed = value

    def _get_sort_reversed(self):
        return getattr(self.context, 'sort_reversed', None)

    sort_reversed = property(_get_sort_reversed, _set_sort_reversed)

    def _set_item_count(self, value):
        self.context.item_count = value

    def _get_item_count(self):
        return getattr(self.context, 'item_count', 30)

    item_count = property(_get_item_count, _set_item_count)

    def _set_sort_on(self, value):
        self.context.sort_on = value

    def _get_sort_on(self):
        return getattr(self.context, 'sort_on', None)

    sort_on = property(_get_sort_on, _set_sort_on)

    def _set_limit(self, value):
        self.context.limit = value

    def _get_limit(self):
        return getattr(self.context, 'limit', 1000)

    limit = property(_get_limit, _set_limit)

    def _set_query(self, value):
        self.context.query = value

    def _get_query(self):
        return getattr(self.context, 'query', None)

    query = property(_get_query, _set_query)
