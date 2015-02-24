# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.contenttypes import _


class CollectionView(FolderView):

    def __init__(self, *args, **kwargs):
        super(CollectionView, self).__init__(*args, **kwargs)
        context = aq_inner(self.context)
        self.collection_behavior = ICollection(context)
        self.b_size = self.collection_behavior.item_count

    def results(self, **kwargs):
        """Return a content listing based result set with results from the
        collection query.

        :param **kwargs: Any keyword argument, which can be used for catalog
                         queries.
        :type  **kwargs: keyword argument

        :returns: plone.app.contentlisting based result set.
        :rtype: ``plone.app.contentlisting.interfaces.IContentListing`` based
                sequence.
        """
        # Extra filter
        kwargs.update(dict(getattr(self.request, 'contentFilter', {})))
        kwargs.setdefault('batch', True)
        kwargs.setdefault('b_size', self.b_size)
        kwargs.setdefault('b_start', self.b_start)

        return self.collection_behavior.results(**kwargs)

    def getFoldersAndImages(self, **kwargs):
        context = aq_inner(self.context)
        wrapped = ICollection(context)
        return wrapped.getFoldersAndImages(**kwargs)

    def tabular_fields(self):
        """Returns a list of all metadata fields from the catalog that were
           selected.
        """
        context = aq_inner(self.context)
        wrapped = ICollection(context)
        fields = wrapped.selectedViewFields()
        fields = [field[0] for field in fields]
        return fields

    def no_items_message(self):
        return _(
            'description_no_results_found',
            default=u"No results were found."
        )
