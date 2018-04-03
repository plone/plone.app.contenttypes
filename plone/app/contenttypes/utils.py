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
    if not url:
        return url

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


def human_readable_size(size):
    """Return human readable size.
    Based on https://stackoverflow.com/a/1094933
    """
    if size < 1024:
        return '{size} B'.format(size=size)

    for unit in ('KB', 'MB', 'GB'):
        size /= 1024.0
        if size < 1024.0:
            return '{size:.1f} {unit}'.format(size=size, unit=unit)

    return '{size:.1f} GB'.format(size=size)
