from collections import Counter
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFCore.utils import getToolByName
from .utils import CT_LIST
from .. import ploneMessageFactory


class ATCTypesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Return a vocabulary with standard content types
        and, for each one, the number of occurrences
        """
        ct_names = [i[0] for i in CT_LIST]
        catalog = getToolByName(context, "portal_catalog")
        brains = catalog.search({'portal_type': ct_names})
        counter = Counter([i.portal_type for i in brains])
        results = [
            SimpleVocabulary.createTerm(k, k, "{0} ({1})".format(
                context.translate(ploneMessageFactory(k)), v)
            )
            for k, v in counter.iteritems()
            if k in ct_names
        ]
        results.sort(key=lambda x: x.title)

        return SimpleVocabulary(results)
