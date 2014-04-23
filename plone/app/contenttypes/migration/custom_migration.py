# -*- coding: UTF-8 -*-
from Products.Five.browser import BrowserView
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import iterSchemataForType
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.content.base import ATContentTypeSchema


HAS_EXTENDER = True
try:
    from archetypes.schemaextender.extender import instanceSchemaFactory
except ImportError:
    HAS_EXTENDER = False


class CustomMigrationForm(BrowserView):

    template = ViewPageTemplateFile('custom_migration.pt')
    metadata_fields = ATContentTypeSchema.keys()

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
        '''Returns the FTI's of all DX-Types (including default-types).'''
        results = []
        portal = self.context
        ttool = getToolByName(portal, 'portal_types')
        for fti in ttool.listTypeInfo():
            if IDexterityFTI.providedBy(fti):
                results.append({'id': fti.getId(),
                                'title': fti.Title()})
        return results

    def getFieldsForATType(self, typename):
        '''Returns schema fields (name and type) for the given AT typename.'''
        results = []
        typesTool = getToolByName(self.context, 'portal_types')
        fti = typesTool.getTypeInfo(typename)
        archetype_tool = getToolByName(self.context, 'archetype_tool', None)
        if not fti or not archetype_tool:
            return results
        schema = None
        # a schema instance is stored in the archetype_tool
        for regType in archetype_tool.listRegisteredTypes():
            if regType['meta_type'] == fti.content_meta_type:
                if HAS_EXTENDER:
                    schema = instanceSchemaFactory(regType['klass'])
                else:
                    schema = regType['schema']
                break
        if not schema:
            return results
        for field in schema.fields():
            if not field.getName() in self.metadata_fields:
                results.append({'id': field.getName(),
                                'title': '%s (%s)' % (field.widget.label, field.widget.getName())})
        return results

    def getFieldsForDXType(self, typename):
        '''Returns schema fields (name and type) for the given DX typename.'''
        results = []
        typesTool = getToolByName(self.context, 'portal_types')
        fti = typesTool.getTypeInfo(typename)
        if not fti:
            return results

        for schemata in iterSchemataForType(typename):
            for fieldName, field in schemata.namesAndDescriptions():
                # ignore Dublin Core fields
                if fieldName in self.metadata_fields:
                    continue
                results.append({'id': fieldName,
                                'title': '%s (%s)' % (field.title, field.__class__.__name__)})
        return results

    def getPossibleTargetField(self, fieldtype):
        ''' a list of DX-field types'''

    def isFolderish(self):
        ''' decide which base-class we use for the migrator'''
