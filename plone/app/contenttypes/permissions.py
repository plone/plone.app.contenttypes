# -*- coding: utf-8 -*-
from AccessControl.Permission import addPermission
from AccessControl.SecurityInfo import ModuleSecurityInfo
from plone.app.contenttypes.utils import DEFAULT_TYPES

security = ModuleSecurityInfo('plone.app.contenttypes')

TYPE_ROLES = ('Manager', 'Site Administrator', 'Owner', 'Contributor')

perms = []

for typename in DEFAULT_TYPES:
    permid = 'Add' + typename
    permname = 'plone.app.contenttypes: Add ' + typename
    security.declarePublic(permid)
    addPermission(permname, default_roles=TYPE_ROLES)

AddCollection = 'plone.app.contenttypes: Add Collection'
AddDocument = 'plone.app.contenttypes: Add Document'
AddEvent = 'plone.app.contenttypes: Add Event'
AddFile = 'plone.app.contenttypes: Add File'
AddFolder = 'plone.app.contenttypes: Add Folder'
AddImage = 'plone.app.contenttypes: Add Image'
AddLink = 'plone.app.contenttypes: Add Link'
AddNewsItem = 'plone.app.contenttypes: Add News Item'
