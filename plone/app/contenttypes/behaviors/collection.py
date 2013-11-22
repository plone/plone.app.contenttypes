# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.syndication.adapters import CollectionFeed \
    as BaseCollectionFeed
from Products.CMFPlone.interfaces.syndication import IFeed
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from plone.app.contentlisting.interfaces import IContentListing
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapts, getMultiAdapter, getUtility
from zope.interface import alsoProvides, implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from plone.app.contenttypes import _


class MetaDataFieldsVocabulary(object):

    implements(IVocabularyFactory)

    def __call__(self, context):
        cat = getToolByName(context, 'portal_catalog')
        items = [
            SimpleTerm(column, column, column)
            for column in cat.schema()
        ]
        return SimpleVocabulary(items)

MetaDataFieldsVocabularyFactory = MetaDataFieldsVocabulary()


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

    customViewFields = schema.List(
        title=_(u'Table Columns'),
        description=_(u"Select which fields to display when "
                      u"'Tabular view' is selected in the display menu."),
        default=['Title', 'Creator', 'Type', 'ModificationDate'],
        value_type=schema.Choice(
            vocabulary='plone.app.contenttypes.metadatafields'),
        required=False,
        )


alsoProvides(ICollection, IFormFieldProvider)
alsoProvides(ICollection, ISyndicatable)


class ISyndicatableCollection(ISyndicatable):
    """Marker interface for syndicatable collections.
    """


class Collection(object):
    implements(ICollection)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    def results(self, batch=True, b_start=0, b_size=None,
                sort_on=None, limit=None, brains=False):
        querybuilder = getMultiAdapter((self.context, self.context.REQUEST),
                                       name='querybuilderresults')
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
        portal_atct = getToolByName(self.context, 'portal_atct', None)
        image_types = getattr(portal_atct, 'image_types', ['Image'])

        filtered_results = []
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
            else:
                continue
            filtered_results.append(item)

        _mapping['total_number_of_images'] = sum(map(
            len,
            _mapping['images'].values()
        ))
        _mapping['results'] = filtered_results
        return _mapping

    def selectedViewFields(self):
        """Returns a list of all metadata fields from the catalog that were
           selected.

        The template expects a tuple/list of (id, title) of the field.

        """
        _mapping = {}
        vocab = getUtility(IVocabularyFactory,
                           name='plone.app.contenttypes.metadatafields')
        for field in vocab(self.context):
            _mapping[field.value] = (field.value, field.title)
        return [_mapping[field] for field in self.customViewFields]

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

    def _set_customViewFields(self, value):
        self.context.customViewFields = value

    def _get_customViewFields(self):
        return getattr(self.context, 'customViewFields', [])

    customViewFields = property(_get_customViewFields, _set_customViewFields)


class CollectionFeed(BaseCollectionFeed):
    implements(IFeed)

    def _brains(self):
        return ICollection(self.context).results(batch=False)[:self.limit]
