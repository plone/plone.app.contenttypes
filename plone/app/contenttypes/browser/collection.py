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
