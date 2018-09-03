# -*- coding: utf-8 -*-
from datetime import datetime
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_MIGRATION_TESTING  # noqa
from plone.app.contenttypes.testing import TEST_MIGRATION
from plone.app.contenttypes.tests.oldtypes import create1_0EventType
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.textfield.value import RichTextValue
from plone.event.interfaces import IEventAccessor
from Products.CMFCore.utils import getToolByName

import unittest


class MigrateEventContentTypesTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_MIGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        self.request['URL'] = self.portal.absolute_url()
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.portal.acl_users.userFolderAddUser('admin',
                                                'secret',
                                                ['Manager'],
                                                [])
        login(self.portal, 'admin')
        self.portal.portal_workflow.setDefaultChain(
            'simple_publication_workflow')

    def tearDown(self):
        try:
            applyProfile(self.portal, 'plone.app.contenttypes:uninstall')
        except KeyError:
            pass

    def doUpgradeStep(self, source, dest,
                      profile='plone.app.contenttypes:default'):
        """Run upgrade step between 2 specified versions"""
        ps = getToolByName(self.portal, 'portal_setup')
        upgrades = [
            u for u
            in ps.listUpgrades(profile, show_old=True)
            if u['ssource'] == source and u['sdest'] == dest
        ]
        self.assertEqual(len(upgrades), 1)

        request = self.portal.REQUEST
        request.form = dict(
            profile_id=profile,
            upgrades=[upgrades[0]['id']],
        )
        ps.manage_doUpgrades(request=request)

    def createOldEvent(self, container, id, start_date, end_date):
        """Create sample event"""
        old_event = container[container.invokeFactory(
            'Event',
            id,
            location='Newbraska',
            start_date=start_date,
            end_date=end_date,
            attendees='Me\r\nYou',
            event_url='http://woo.com',
            contact_name='Frank',
            contact_email='me@fra.nk',
            contact_phone='+4412345',
        )]
        old_event.text = RichTextValue(
            raw=u'Awesüme',
            mimeType='text/plain',
            outputMimeType='text/x-html-safe'
        )

    @unittest.skipUnless(
        TEST_MIGRATION,
        'Migration tests require ATContentTypes',
    )
    def test_pact_1_0_dxevent_is_migrated(self):
        def getNewEventDetail(obj):
            acc = IEventAccessor(obj)
            return [
                obj.id,
                [acc.start.year, acc.start.month, acc.start.day],
                [acc.end.year, acc.end.month, acc.end.day],
                acc.location,
                acc.attendees
            ]

        # Create some 1.0 Event objects
        create1_0EventType(self.portal)
        self.portal.invokeFactory('Folder', 'event-folder')
        self.createOldEvent(
            self.portal, 'eventa',
            start_date=datetime(2012, 1, 1, 15, 20),
            end_date=datetime(2015, 9, 2, 16, 20),
        )
        self.createOldEvent(
            self.portal['event-folder'], 'eventb',
            start_date=datetime(2013, 3, 3, 15, 20),
            end_date=datetime(2019, 5, 6, 16, 20),
        )

        # IEventAccessor? What's that?
        with self.assertRaisesRegexp(TypeError, 'IEventAccessor'):
            IEventAccessor(self.portal['eventa'])

        # Run upgrade step
        self.doUpgradeStep('1001', '1100')

        # Should be able to use IEventAccessor on events now
        self.assertEqual(
            getNewEventDetail(self.portal['eventa']),
            ['eventa', [2012, 1, 1], [2015, 9, 2],
             u'Newbraska', ('Me', 'You')],
        )
        self.assertEqual(
            getNewEventDetail(self.portal['event-folder']['eventb']),
            ['eventb', [2013, 3, 3], [2019, 5, 6],
             u'Newbraska', ('Me', 'You')],
        )
