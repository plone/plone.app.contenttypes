from Acquisition import aq_inner
from Products.Five import BrowserView

from plone.app.contenttypes.behaviors.collection import ICollection


class CollectionView(BrowserView):

    def results(self, **kwargs):
        context = aq_inner(self.context)
        wrapped = ICollection(context)
        return wrapped.results(**kwargs)

    def getFoldersAndImages(self, **kwargs):
        context = aq_inner(self.context)
        wrapped = ICollection(context)
        return wrapped.getFoldersAndImages(**kwargs)

    def selectedViewFields(self):
        """Returns a list of all metadata fields from the catalog that were
           selected.

        Note: this is supported by plone.app.collection, but not yet
        in plone.app.contenttypes.  See the commented out
        customViewFields field.
        """
        return []
