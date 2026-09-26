from plone.app.contenttypes.interfaces import IImage

try:
    from plone.app.dexterity.config import MAX_TITLE_LENGTH as _MAX_TITLE_LENGTH
except ImportError:
    _MAX_TITLE_LENGTH = 1024


def set_title_description(obj, event):
    """Sets title to filename if no title
    was provided.
    Also sets an empty unicode as description if
    no description was provided.
    """
    title = obj.title
    if not title:
        if IImage.providedBy(obj):
            datafield = obj.image
        else:
            datafield = obj.file
        if datafield:
            filename = datafield.filename or ""
            obj.title = filename[:_MAX_TITLE_LENGTH]

    description = obj.description
    if not description:
        obj.description = ""
