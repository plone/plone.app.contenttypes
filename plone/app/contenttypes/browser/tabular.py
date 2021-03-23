from Products.Five import BrowserView

# BEWARE: the cell views are registered for ContentListingObject
# which are not acquisition aware.
# That precludes using Products.Five.ViewPageTemplateFile
# and imposes to use zope.browserpage.viewpagetemplatefile.
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
# BEWARE

class TitleCell(BrowserView):
    __call__ = ViewPageTemplateFile('templates/titlecell.pt')

    @property
    def title(self):
        return self.context.Title() or self.context.getId()

    @property
    def link(self):
        suffix = (
            '/view'
            if self.context.PortalType in self.table_view.use_view_action
            else ''
        )
        return self.context.getURL() + suffix

    @property
    def type_class(self):
        return ('contenttype-' +
                self.table_view.normalizeString(self.context.PortalType())
                if self.table_view.show_icons else '')

    @property
    def wf_state_class(self):
        return ('state-' +
                self.table_view.normalizeString(self.context.review_state()))

    def render_image(self):
        thumb_scale_table = self.table_view.get_thumb_scale_table()
        img_class = self.table_view.img_class
        return self.table_view.image_scale.tag(
            self.context, 'image',
            scale=thumb_scale_table, css_class=img_class
        )


class CreatorCell(BrowserView):
    __call__ = ViewPageTemplateFile('templates/creatorcell.pt')

    @property
    def author(self):
        return self.table_view.pas_member.info(self.context.Creator)

    @property
    def author_name(self):
        return self.author['fullname'] or self.author['username']
