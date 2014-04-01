# -*- coding: utf-8 -*-

DEFAULT_TYPES = [
    'Collection',
    'Document',
    'Event',
    'File',
    'Folder',
    'Image',
    'Link',
    'News Item',
]


def replace_link_variables_by_paths(context, url):
    """Take an `url` and replace the variables "${navigation_root_url}" and
    "${portal_url}" by the corresponding paths. `context` is the acquisition
    context.
    """
    portal_state = context.restrictedTraverse('@@plone_portal_state')

    if '${navigation_root_url}' in url:
        url = _replace_variable_by_path(
            url,
            '${navigation_root_url}',
            portal_state.navigation_root()
        )

    if '${portal_url}' in url:
        url = _replace_variable_by_path(
            url,
            '${portal_url}',
            portal_state.portal()
        )

    return url


def _replace_variable_by_path(url, variable, obj):
    path = '/'.join(obj.getPhysicalPath())
    return url.replace(variable, path)
