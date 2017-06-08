# -*- coding: utf-8 -*-
from plone.app.contenttypes.utils import replace_link_variables_by_paths
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from z3c.form.browser.text import TextWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextWidget
from z3c.form.interfaces import NO_VALUE
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.component import adapts
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.schema.interfaces import IField

import json


class ILinkWidget(ITextWidget):
    """ Interface for enhanced link widget

        The widget supports internal, external and email links

    """


class LinkDataConverter(BaseDataConverter):

    adapts(IField, ILinkWidget)

    def toWidgetValue(self, value):
        value = super(LinkDataConverter, self).toWidgetValue(value)
        result = {'internal': u'',
                  'external': u'',
                  'email': u'',
                  'email_subject': u''}
        uuid = None
        if value.startswith('mailto:'):
            value = value[7:]   # strip mailto from beginning
            if '?subject=' in value:
                email, email_subject = value.split('?subject=')
                result['email'] = email
                result['email_subject'] = email_subject
            else:
                result['email'] = value
        else:
            if '/resolveuid/' in value:
                result['internal'] = value.rsplit('/', 1)[-1]
            else:
                portal = getSite()
                path = replace_link_variables_by_paths(portal, value)
                path = path[len(portal.absolute_url())+1:].encode('ascii', 'ignore')  # noqa
                obj = portal.unrestrictedTraverse(path=path, default=None)
                if obj is not None:
                    uuid = IUUID(obj, None)
            if uuid is not None:
                result['internal'] = uuid
            else:
                result['external'] = value
        return result


class LinkWidget(TextWidget):
    """ Implementation of enhanced link widget

    """

    implementsOnly(ILinkWidget)

    def portal_url(self, relative=0):
        return getSite().absolute_url(relative)

    def pattern_data(self):
        pattern_data = {
            'vocabularyUrl': '{0}/@@getVocabulary?name=plone.app.vocabularies.Catalog'.format(self.portal_url()),  # noqa
            'maximumSelectionSize': 1
        }
        return json.dumps(pattern_data)

    def extract(self, default=NO_VALUE):
        form = self.request.form
        internal = form.get(self.name + '.internal')
        external = form.get(self.name + '.external')
        email = form.get(self.name + '.email')
        if internal:
            url = '${portal_url}/resolveuid/' + internal
        elif email:
            subject = form.get(self.name + '.subject')
            if not subject:
                url = 'mailto:' + email
            else:
                url = 'mailto:{}?subject={}'.format(email, subject)
        else:
            url = external   # the default is `http://` so we land here
        if url:
            self.request[self.name] = safe_unicode(url)
        return super(LinkWidget, self).extract(default=default)


@adapter(ITextWidget, IFormLayer)
@implementer(IFieldWidget)
def LinkFieldWidget(field, request):
    """ IFieldWidget factory for KeywordWidget
    """
    return FieldWidget(field, LinkWidget(request))
