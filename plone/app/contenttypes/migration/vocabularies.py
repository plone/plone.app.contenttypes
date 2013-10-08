# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFCore.utils import getToolByName
from plone.app.contenttypes.migration.utils import ATCT_LIST
from plone.app.contenttypes.migration.utils import isSchemaExtended
from .. import _


def results(context, extended_types=False):
    extended = {}
    ifaces = []
    for k, v in ATCT_LIST.items():
        iface = v['iface'].__identifier__
        real = isSchemaExtended(v['iface'])
        expected = v['extended_fields']
        is_extended = len(real) > len(expected)
        if is_extended and extended_types:
            ifaces.append(iface)
            extended[k]['fields'] = real.remove(expected[0])

        elif not extended_types and not is_extended:
            ifaces.append(iface)
    catalog = getToolByName(context, "portal_catalog")
    brains = catalog.search({'object_provides': ifaces})
    counter = {}
    for i in brains:
        pt = i.portal_type
        if not counter.get(pt):
            counter[pt] = 0
        counter[pt] += 1

    results = []
    for k, v in counter.iteritems():
        if extended_types:
            display = "{0} ({1}) - extended fields: {2}".format(context.translate(_(k)), v, extended[k]['fields'])
        else:
            display = "{0} ({1})".format(context.translate(_(k)), v)
        term = SimpleVocabulary.createTerm(k, k, display)
        results.append(term)
        # for k, v in counter.iteritems()
    results.sort(key=lambda x: x.title)

    return SimpleVocabulary(results)


class ATCTypesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Return a vocabulary with standard content types
        and, for each one, the number of occurrences
        """
        return results(context, extended_types=False)


class ExtendedTypesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """bla
        """
        return results(context, extended_types=True)
