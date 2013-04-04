# -*- coding: utf-8 -*-
from plone.app.layout.viewlets import ViewletBase

from plone.app.contenttypes.interfaces import INewsItem
from plone.app.contenttypes.behaviors.leadimage import ILeadImage


class LeadImageViewlet(ViewletBase):
    """ A simple viewlet which renders leadimage """

    def update(self):
        self.context = ILeadImage(self.context)
        self.available = True if self.context.image else False
        if INewsItem.providedBy(self.context):
            self.available = False
