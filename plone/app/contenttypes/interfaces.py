# -*- coding: utf-8 -*-
from zope.interface import Interface, Attribute


class IEvent(Interface):

    '''
    Marker Interface for events.
    With this, the start and end dates can get indexed
    '''

    start_date = Attribute('A start date.')
    end_date = Attribute('An end date.')
