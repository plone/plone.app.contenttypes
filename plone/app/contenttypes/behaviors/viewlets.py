# -*- coding: utf-8 -*-
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.layout.viewlets import ViewletBase
from plone.app.contenttypes.behaviors.leadimage import ILeadImageSettings
from plone import api


class LeadImageViewlet(ViewletBase):
    """ A simple viewlet which renders leadimage """

    def update(self):
        self.context = ILeadImage(self.context)
        self.available = self.is_visible

    @property
    def is_visible(self):
        visible = False
        if self.context.image:
            is_visible = api.portal.get_registry_record(
                'is_visible',
                interface=ILeadImageSettings)
            if is_visible:
                visible = True
        return visible

    @property
    def scale_name(self):
        return api.portal.get_registry_record(
                'scale_name',
                interface=ILeadImageSettings)
