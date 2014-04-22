# -*- coding: UTF-8 -*-
from Products.Five.browser import BrowserView
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class CustomMigrationForm(BrowserView):

    template = ViewPageTemplateFile('custom_migration.pt')

    def __call__(self):
        return self.template()

    def getATFTIs(self):
        ''' return a list of all at-types with existing instances
        (including default-types)  '''
        pass

    def getDXFTIs(self):
        '''return the FTI's of all DX-Types (including default-types)
        '''
        results = []
        portal = self.context
        ttool = getToolByName(portal, 'portal_types')
        for ti in ttool.listTypeInfo():
            if IDexterityFTI.providedBy(ti):
                results.append(ti)

    def getFieldsForATType(self, typename):
        pass

    def getFieldsForDXType(self, typename):
        pass

    def getPossibleTargetField(self, fieldtype):
        ''' a list of DX-field types'''

    def isFolderish(self):
        ''' decide which base-class we use for the migrator'''
