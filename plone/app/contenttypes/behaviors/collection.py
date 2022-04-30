from plone.app.contenttypes import _
from plone.app.z3cform.widget import QueryStringFieldWidget
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.base.interfaces.syndication import IFeed
from plone.base.interfaces.syndication import ISyndicatable
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.syndication.adapters import (
    CollectionFeed as BaseCollectionFeed,
)
from zope import schema
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.deferredimport import deprecated
from zope.interface import implementer
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory


deprecated(
    "Import from plone.app.vocabularies.metadatafields instead (this compatibility layer will be removed in Plone 6)",
    MetaDataFieldsVocabulary="plone.app.vocabularies.metadatafields:MetaDataFieldsVocabulary",
)


deprecated(
    "Import from plone.app.vocabularies.metadatafields instead (this compatibility layer will be removed in Plone 6)",
    MetaDataFieldsVocabularyFactory="plone.app.vocabularies.metadatafields:MetaDataFieldsVocabularyFactory",
)


@provider(IFormFieldProvider, ISyndicatable)
class ICollection(model.Schema):

    query = schema.List(
        title=_("Search terms"),
        description=_(
            "Define the search terms for the items you want "
            "to list by choosing what to match on. "
            "The list of results will be dynamically updated"
        ),
        value_type=schema.Dict(value_type=schema.Field(), key_type=schema.TextLine()),
        required=False,
        missing_value="",
    )
    form.widget("query", QueryStringFieldWidget)

    sort_on = schema.TextLine(
        title=_("label_sort_on", default="Sort on"),
        description=_("Sort the collection on this index"),
        required=False,
    )

    sort_reversed = schema.Bool(
        title=_("label_sort_reversed", default="Reversed order"),
        description=_("Sort the results in reversed order"),
        required=False,
    )

    limit = schema.Int(
        title=_("Limit"),
        description=_("Limit Search Results"),
        required=False,
        default=1000,
        min=1,
    )

    item_count = schema.Int(
        title=_("label_item_count", default="Item count"),
        description=_("Number of items that will show up in one batch."),
        required=False,
        default=30,
        min=1,
    )

    customViewFields = schema.List(
        title=_("Table Columns"),
        description=_(
            "Select which fields to display when "
            "'Tabular view' is selected in the display menu."
        ),
        default=["Title", "Creator", "Type", "ModificationDate"],
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.MetadataFields"),
        required=False,
    )


class ISyndicatableCollection(ISyndicatable):
    """Marker interface for syndicatable collections."""


@implementer(ICollection)
@adapter(IDexterityContent)
class Collection:
    def __init__(self, context):
        self.context = context

    def results(
        self,
        batch=True,
        b_start=0,
        b_size=None,
        sort_on=None,
        limit=None,
        brains=False,
        custom_query=None,
    ):
        if custom_query is None:
            custom_query = {}
        querybuilder = getMultiAdapter(
            (self.context, self.context.REQUEST), name="querybuilderresults"
        )
        sort_order = "reverse" if self.sort_reversed else "ascending"
        if not b_size:
            b_size = self.item_count
        if not sort_on:
            sort_on = self.sort_on
        if not limit:
            limit = self.limit
        return querybuilder(
            query=self.query,
            batch=batch,
            b_start=b_start,
            b_size=b_size,
            sort_on=sort_on,
            sort_order=sort_order,
            limit=limit,
            brains=brains,
            custom_query=custom_query,
        )

    def selectedViewFields(self):
        """Returns a list of all metadata fields from the catalog that were
           selected.

        The template expects a tuple/list of (id, title) of the field.

        """
        _mapping = {}
        vocab = getUtility(
            IVocabularyFactory, name="plone.app.vocabularies.MetadataFields"
        )
        for field in vocab(self.context):
            _mapping[field.value] = (field.value, field.title)
        ret = [_mapping[field] for field in self.customViewFields]
        return ret

    # Getters and setters for our fields.

    @property
    def sort_reversed(self):
        return getattr(self.context, "sort_reversed", None)

    @sort_reversed.setter
    def sort_reversed(self, value):
        self.context.sort_reversed = value

    @property
    def item_count(self):
        return getattr(self.context, "item_count", 30)

    @item_count.setter
    def item_count(self, value):
        self.context.item_count = value

    @property
    def sort_on(self):
        return getattr(self.context, "sort_on", None)

    @sort_on.setter
    def sort_on(self, value):
        self.context.sort_on = value

    @property
    def limit(self):
        return getattr(self.context, "limit", 1000)

    @limit.setter
    def limit(self, value):
        self.context.limit = value

    @property
    def query(self):
        return getattr(self.context, "query", None)

    @query.setter
    def query(self, value):
        self.context.query = value

    @property
    def customViewFields(self):
        # Note: in corner cases customViewFields might be None, but we
        # always want a list.
        return getattr(self.context, "customViewFields", []) or []

    @customViewFields.setter
    def customViewFields(self, value):
        self.context.customViewFields = value


@implementer(IFeed)
class CollectionFeed(BaseCollectionFeed):
    def _brains(self):
        return ICollection(self.context).results(batch=False)[: self.limit]
