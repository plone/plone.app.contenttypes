# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFCore.utils import getToolByName
from .utils import ATCT_LIST
from .. import _


class ATCTypesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Return a vocabulary with standard content types
        and, for each one, the number of occurrences
        """
        ifaces = [v['iface'].__identifier__ for k, v in ATCT_LIST.items()]
        catalog = getToolByName(context, "portal_catalog")
        brains = catalog.search({'object_provides': ifaces})
        counter = {}
        for i in brains:
            pt = i.portal_type
            if not counter.get(pt):
                counter[pt] = 0
            counter[pt] += 1

        results = [
            SimpleVocabulary.createTerm(k, k, "{0} ({1})".format(
                context.translate(_(k)), v)
            )
            for k, v in counter.iteritems()
        ]
        results.sort(key=lambda x: x.title)

        return SimpleVocabulary(results)
