# -*- coding: utf-8 -*-
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.formwidget.querystring.widget import QueryStringFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.util import getSpecification
from zope.component import adapter


QueryStringFieldWidget = adapter(
    getSpecification(ICollection['query']),
    IFormLayer
)(QueryStringFieldWidget)
