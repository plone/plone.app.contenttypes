# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IImage


def set_title_description(obj, event):
    ''' Sets title to filename if no title
        was provided.
        Also sets an empty unicode as description if
        no description was provided.
    '''
    title = obj.title
    if not title:
        if IImage.providedBy(obj):
            datafield = obj.image
        else:
            datafield = obj.file
        if datafield:
            filename = datafield.filename
            obj.title = filename

    description = obj.description
    if not description:
        obj.description = u''
