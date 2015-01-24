# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.contenttypes import _
from Products.CMFPlone.PloneBatch import Batch


class CollectionView(FolderView):

    def results(self, **kwargs):
        context = aq_inner(self.context)
        wrapped = ICollection(context)
        return wrapped.results(self.b_start, **kwargs)

    def batch(self):
        batch = Batch(self.results(), self.b_start)
        return batch

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
