# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# from Products.CMFCore.utils import getToolByName


class AlbumView(BrowserView):

    template = ViewPageTemplateFile('templates/folder_album_view.pt')

    def getAlbumContent(self,
                        container=None,
                        images=0,
                        folders=0,
                        subimages=0,
                        others=0):
        """ Mostly ripped out from atctListAlbum.py
        """

        if not container:
            container = self.context

        result = {}

        if images:
            result['images'] = container.getFolderContents(
                {'portal_type': ('Image',)}, full_objects=True)

        if folders:
            result['folders'] = container.getFolderContents(
                {'portal_type': ('Folder',)})

        if subimages:
            # Handle brains or objects
            if getattr(container, 'getPath', None) is not None:
                path = container.getPath()
            else:
                path = '/'.join(container.getPhysicalPath())
            # Explicitly set path to remove default depth
            result['subimages'] = container.getFolderContents(
                {'portal_type': ('Image',), 'path': path})

        if others:
            utils = getToolByName(self.context, 'plone_utils')
            searchContentTypes = utils.getUserFriendlyTypes()
            filtered = [p_type for p_type in searchContentTypes
                        if p_type not in ('Image', 'Folder',)]
            if filtered:
                # We don't need the full objects for the folder_listing
                result['others'] = container.getFolderContents(
                    {'portal_type': filtered})
            else:
                result['others'] = ()

        return result
