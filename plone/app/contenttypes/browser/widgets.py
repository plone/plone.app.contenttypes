# -*- coding: utf-8 -*-
from zope.component import adapter
from z3c.form.interfaces import IFormLayer
from z3c.form.util import getSpecification
from plone.app.widgets.widget import QueryStringFieldWidget
from plone.app.contenttypes.behaviors.collection import ICollection


QueryStringFieldWidget = adapter(
    getSpecification(ICollection['query']),
    IFormLayer
)(QueryStringFieldWidget)
