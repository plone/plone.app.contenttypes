# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Products.CMFCore.permissions import ManagePortal
from plone.app.layout.viewlets import ViewletBase
from plone.dexterity.interfaces import IDexterityFTI

import pkg_resources

try:
    pkg_resources.get_distribution('Products.Archetypes')
except pkg_resources.DistributionNotFound:
    HAS_ARCHETYPES = False
else:
    from Products.Archetypes.interfaces.base import IBaseObject
    HAS_ARCHETYPES = True


class ATWarningViewlet(ViewletBase):

    def update(self):
        self.available = False
        self.context = aq_inner(self.context)
        if not HAS_ARCHETYPES:
            return
        if not IBaseObject.providedBy(self.context):
            return
        context_fti = self.context.getTypeInfo()
        if IDexterityFTI.providedBy(context_fti):
            self.available = True

    def can_migrate(self):
        sm = getSecurityManager()
        if sm.checkPermission(ManagePortal, self.context):
            return True
