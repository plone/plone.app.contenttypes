# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityFTI

from zope.component import queryUtility


def update_fti(context):
    """ Schema-files moved into their own folder after 1.0b1
    """
    # Document
    fti = queryUtility(
        IDexterityFTI,
        name='Document'
    )
    fti.model_file = "plone.app.contenttypes.schema:document.xml"
    # File
    fti = queryUtility(
        IDexterityFTI,
        name='File'
    )
    fti.model_file = "plone.app.contenttypes.schema:file.xml"
    # Folder
    fti = queryUtility(
        IDexterityFTI,
        name='Folder'
    )
    fti.model_file = "plone.app.contenttypes.schema:folder.xml"
    # Image
    fti = queryUtility(
        IDexterityFTI,
        name='Image'
    )
    fti.model_file = "plone.app.contenttypes.schema:image.xml"
    # Link
    fti = queryUtility(
        IDexterityFTI,
        name='Link'
    )
    fti.model_file = "plone.app.contenttypes.schema:link.xml"
    # News Item
    fti = queryUtility(
        IDexterityFTI,
        name='News Item'
    )
    fti.model_file = "plone.app.contenttypes.schema:news_item.xml"
