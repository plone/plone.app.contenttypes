from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles
#http://developer.plone.org/security/custom_permissions.html
security = ModuleSecurityInfo('plone.app.contenttypes')
TYPE_ROLES = ('Manager', 'Site Administrator', 'Owner')
perms = []
for typename in (
    "Collection",
    "Document",
    "Event",
    "File",
    "Folder",
    "Image",
    "Link",
    "News Item",
):
#    ctype = "plone.app.contenttypes." + typename
    permid = 'Add' + typename
    permname = 'plone.app.contenttypes: Add ' + typename
    security.declarePublic(permid)
    setDefaultRoles(permname, TYPE_ROLES)

AddCollection = "plone.app.contenttypes: Add Collection"
AddDocument = "plone.app.contenttypes: Add Document"
AddEvent = "plone.app.contenttypes: Add Event"
AddFile = "plone.app.contenttypes: Add File"
AddFolder = "plone.app.contenttypes: Add Folder"
AddImage = "plone.app.contenttypes: Add Image"
AddLink = "plone.app.contenttypes: Add Link"
AddNewsItem = "plone.app.contenttypes: Add News Item"
