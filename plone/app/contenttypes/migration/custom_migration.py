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
        '''Returns a list of all AT types with existing instances (including default-types).'''
        results = []
        archetype_tool = getToolByName(self.context, 'archetype_tool', None)
        # if we do not have archetype_tool, it means that we have no registered AT types
        if not archetype_tool:
            return results

        typesTool = getToolByName(self.context, 'portal_types')
        catalog = getToolByName(self.context, 'portal_catalog')
        registeredTypeNames = [registered['name'] for registered in archetype_tool.listRegisteredTypes()]
        for fti in typesTool.listTypeInfo():
            ftiId = fti.getId()
            if hasattr(fti, 'content_meta_type') and \
               fti.content_meta_type in registeredTypeNames and \
               catalog(portal_type=ftiId):
                results.append({'id': ftiId,
                                'title': fti.Title()})
        return results

    def getDXFTIs(self):
        '''return the FTI's of all DX-Types (including default-types).'''
        results = []
        portal = self.context
        ttool = getToolByName(portal, 'portal_types')
        for fti in ttool.listTypeInfo():
            if IDexterityFTI.providedBy(fti):
                results.append({'id': fti.getId(),
                                'title': fti.Title()})
        return results

    def getFieldsForATType(self, typename):
        pass

    def getFieldsForDXType(self, typename):
        pass

    def getPossibleTargetField(self, fieldtype):
        ''' a list of DX-field types'''

    def isFolderish(self):
        ''' decide which base-class we use for the migrator'''
