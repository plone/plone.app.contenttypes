from plone.directives import form
from plone.namedfile.field import NamedBlobFile
from Products.CMFPlone import PloneMessageFactory as _
from zope import schema

from plone.rfc822.interfaces import IPrimaryField

from zope.interface import Interface
from zope.interface import implements
from zope.interface import alsoProvides

class IFile(form.Schema):
    
    form.model("file.xml")