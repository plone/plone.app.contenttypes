# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from plone.app.contenttypes.migration.utils import ATCT_LIST
from plone.app.contenttypes.migration.utils import isSchemaExtended
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from .. import _


def get_terms(context, counter, ext_dict, show_extended):
    results = []
    for k, v in counter.iteritems():
        if not show_extended:
            if k not in ext_dict:
                display = u"{0} ({1})".format(context.translate(_(k)), v)
                term = SimpleVocabulary.createTerm(k, k, display)
                results.append(term)
        else:
            if k in ext_dict:
                ext = str(ext_dict[k]['fields']).\
                    replace("[", "").replace("]", "")
                display = u"{0} ({1}) - extended fields: {2}".\
                    format(context.translate(_(k)), v, ext)
                term = SimpleVocabulary.createTerm(k, k, display)
                results.append(term)
    results.sort(key=lambda x: x.title)
    return results


def count(brains):
    counter = {}
    for i in brains:
        pt = i.portal_type
        if "Blob" in i.meta_type:
            if pt == "File":
                pt = "BlobFile"
            else:
                pt = "BlobImage"
        if not counter.get(pt):
            counter[pt] = 0
        if not i.meta_type or 'dexterity' in i.meta_type.lower():
            # There might be DX types with same iface and meta_type than AT
            continue
        counter[pt] += 1
    return counter


def results(context, show_extended=False):
    """Helper method to create the vocabularies used below.
    """
    ext_dict = {}
    ifaces = []
    for k, v in ATCT_LIST.items():
        iface = v['iface'].__identifier__
        extendend_fields = isSchemaExtended(v['iface'])
        expected = v['extended_fields']
        is_extended = len(extendend_fields) > len(expected)
        if is_extended and show_extended:
            ifaces.append(iface)
            ext_dict[k] = {}
            if expected:
                extendend_fields.remove(expected[0])
            ext_dict[k]['fields'] = extendend_fields

        elif not show_extended and not is_extended:
            ifaces.append(iface)

    catalog = getToolByName(context, "portal_catalog")
    brains = catalog.search({'object_provides': ifaces})
    counter = count(brains)

    return SimpleVocabulary(get_terms(context,
                                      counter,
                                      ext_dict,
                                      show_extended))


class ATCTypesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Return a vocabulary with standard content types
        and, for each one, the number of occurrences.
        """
        return results(context, show_extended=False)


class ExtendedTypesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Return a vocabulary with all extended types
        and for each the number of occurences and a list of the
        extended fields.
        """
        return results(context, show_extended=True)
