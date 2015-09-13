# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.syndication.adapters import CollectionFeed \
    as BaseCollectionFeed
from Products.CMFPlone.interfaces.syndication import IFeed
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from plone.app.contenttypes import _
from plone.app.z3cform.widget import QueryStringFieldWidget
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class MetaDataFieldsVocabulary(object):

    def __call__(self, context):
        cat = getToolByName(context, 'portal_catalog')
        items = [
            SimpleTerm(column, column, column)
            for column in cat.schema()
        ]
        return SimpleVocabulary(items)

MetaDataFieldsVocabularyFactory = MetaDataFieldsVocabulary()


@provider(IFormFieldProvider, ISyndicatable)
class ICollection(model.Schema):

    query = schema.List(
        title=_(u'Search terms'),
        description=_(u"Define the search terms for the items you want "
                      u"to list by choosing what to match on. "
                      u"The list of results will be dynamically updated"),
        value_type=schema.Dict(value_type=schema.Field(),
                               key_type=schema.TextLine()),
        required=False,
        missing_value=''
    )
    form.widget('query', QueryStringFieldWidget)

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
        min=1,
    )

    item_count = schema.Int(
        title=_(u'label_item_count', default=u'Item count'),
        description=_(u'Number of items that will show up in one batch.'),
        required=False,
        default=30,
        min=1,
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


class ISyndicatableCollection(ISyndicatable):
    """Marker interface for syndicatable collections.
    """


@implementer(ICollection)
@adapter(IDexterityContent)
class Collection(object):

    def __init__(self, context):
        self.context = context

    def results(self, batch=True, b_start=0, b_size=None,
                sort_on=None, limit=None, brains=False,
                custom_query=None):
        if custom_query is None:
            custom_query = {}
        querybuilder = getMultiAdapter((self.context, self.context.REQUEST),
                                       name='querybuilderresults')
        sort_order = 'reverse' if self.sort_reversed else 'ascending'
        if not b_size:
            b_size = self.item_count
        if not sort_on:
            sort_on = self.sort_on
        if not limit:
            limit = self.limit

        query = self.query

        # Handle INavigationRoot awareness as follows:
        # - If query is None or empty then do nothing.
        # - If query already contains a criteria for the index "path", then do
        #   nothing, since plone.app.querybuilder takes care of this
        #   already. (See the code of _path and _relativePath inside
        #   p.a.querystring.queryparser to understand).
        # - If query does not contain any criteria using the index "path", then
        #   add a criteria to match everything under the path "/" (which will
        #   be converted to the actual navigation root path by
        #   p.a.querystring).
        if query:
            has_path_criteria = any(
                (criteria['i'] == 'path')
                for criteria in query
            )
            if not has_path_criteria:
                # Make a copy of the query to avoid modifying it
                query = list(self.query)
                query.append({
                    'i': 'path',
                    'o': 'plone.app.querystring.operation.string.path',
                    'v': '/',
                })

        return querybuilder(
            query=query, batch=batch, b_start=b_start, b_size=b_size,
            sort_on=sort_on, sort_order=sort_order,
            limit=limit, brains=brains, custom_query=custom_query
        )

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
        ret = [_mapping[field] for field in self.customViewFields]
        return ret

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
        # Note: in corner cases customViewFields might be None, but we
        # always want a list.
        return getattr(self.context, 'customViewFields', []) or []

    customViewFields = property(_get_customViewFields, _set_customViewFields)


@implementer(IFeed)
class CollectionFeed(BaseCollectionFeed):

    def _brains(self):
        return ICollection(self.context).results(batch=False)[:self.limit]
