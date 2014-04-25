# -*- coding: UTF-8 -*-
from zope.i18n import translate
from Products.Five.browser import BrowserView
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import iterSchemataForType
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from plone.app.contenttypes.migration.migration import migrateCustomAT


HAS_EXTENDER = True
try:
    from archetypes.schemaextender.extender import instanceSchemaFactory
except ImportError:
    HAS_EXTENDER = False


class CustomMigrationForm(BrowserView):

    template = ViewPageTemplateFile('custom_migration.pt')
    at_metadata_fields = ATContentTypeSchema.keys()
    dx_metadata_fields = list(at_metadata_fields)
    # some metadata names are different between AT and DX...
    dx_metadata_fields.remove('allowDiscussion')
    dx_metadata_fields.remove('excludeFromNav')
    dx_metadata_fields.append('allow_discussion')
    dx_metadata_fields.append('exclude_from_nav')

    def __call__(self):
        # check that we can actually access this form, aka the current user has an advice to add or edit
        form = self.request.form
        cancelled = form.get('form.button.Cancel', False)
        submitted = form.get('form.button.Migrate', False)
        if submitted:
            # proceed, call the migration methdd
            self.migrate()
            msg = translate('Migration applied.',
                            domain='plone.app.contenttypes')
            self.context.plone_utils.addPortalMessage(msg)
        elif cancelled:
            self.request.response.redirect(form.get('form.HTTP_REFERER'))
        return self.index()

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
            if not field.getName() in self.at_metadata_fields:
                results.append({'id': field.getName(),
                                'title': '%s (%s)' % (field.widget.label, field.widget.getName()),
                                'type': field.widget.getName()})
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
                if fieldName in self.dx_metadata_fields:
                    continue
                results.append({'id': fieldName,
                                'title': '%s (%s)' % (field.title, field.__class__.__name__),
                                'type': field.__class__.__name__})
        return results

    def getPossibleTargetField(self, fieldtype):
        ''' a list of DX-field types'''

    def isFolderish(self):
        ''' decide which base-class we use for the migrator'''

    def migrate(self):
        '''Build data from self.request.form, we will build something like :
           {'MyATPortalType': {'MyDXPortalType': {'at_fielname1': 'dx_fieldname1', 'at_fieldname2': 'dx_fieldname2'}}}
           Call the migrateCustomAT migrator for each AT content_type we choose to migrate.'''
        data = {}
        form = self.request.form
        for k in self.request.form.keys():
            if k.startswith('dx_select_'):
                # we found select where we choose a DX type regarding an AT type
                # the selelect name is like 'dx_select_MyATPortalType'
                if not form[k]:
                    # nothing selected in this select, continue
                    continue
                at_typename = k[10:]
                dx_typename = form[k]
                data[at_typename] = {dx_typename: {}}
                # now handle fields mapping for found DX/AT type migration definition
                # we have 2 keys we relevant mappings, first key is the AT typename
                # second key is a particular key like 'dx_DXPortalType__for__MyATPortalType
                dx_key = 'dx_%s__for__%s' % (dx_typename, at_typename)
                for at_fieldname in form[at_typename]:
                    data[at_typename][dx_typename][at_fieldname] = form[dx_key][form[at_typename].index(at_fieldname)]
        for at_typename, dx_mappings in data.items():
            for k, v in dx_mappings.items():
                migrateCustomAT(self.context, fields_mapping=v, src_type=at_typename, dst_type=dx_typename)

        #data = ({'AT_field_name': 'text',
        #         'AT_field_type': 'RichText',
        #         'DX_field_name': 'text',
        #         'DX_field_type': 'TextLine', }, )
        #migrateCustomAT(self.context, fields_mapping=data, src_type='DocumentAT', dst_type='Document')


class DisplayDXFields(CustomMigrationForm):

    template = ViewPageTemplateFile('custom_migration_display_dx_fields.pt')

    def __init__(self, context, request):
        CustomMigrationForm.__init__(self, context, request)
        self.at_typename = request.get('at_typename')
        self.dx_typename = request.get('dx_typename')

    def __call__(self):
        '''
        '''
        return self.index()
