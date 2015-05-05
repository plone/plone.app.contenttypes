# -*- coding: utf-8 -*-
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.contenttypes.interfaces import INewsItem
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets import ViewletBase


class LeadImageViewlet(ViewletBase):
    """ A simple viewlet which renders leadimage """

    def update(self):
        self.context = ILeadImage(self.context)
        self.available = True if self.context.image else False
        if INewsItem.providedBy(self.context)\
                or not IViewView.providedBy(self.view):
            self.available = False
