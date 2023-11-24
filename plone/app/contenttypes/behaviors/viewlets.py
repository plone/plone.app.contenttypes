from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from plone.app.layout.viewlets import ViewletBase


class LeadImageViewlet(ViewletBase):
    """A simple viewlet which renders leadimage"""

    def update(self):
        behavior = ILeadImageBehavior(self.context)
        self.available = True if behavior.image else False
