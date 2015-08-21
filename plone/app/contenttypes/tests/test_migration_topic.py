# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.migration.topics import migrate_topics
from plone.app.contenttypes.testing import \
    PLONE_APP_CONTENTTYPES_MIGRATION_TESTING
from plone.app.querystring.queryparser import parseFormquery
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility
from zope.interface import implementer

import unittest


@implementer(ICollection)
class FolderishCollection(Container):
    """Test subclass for folderish ``Collections``.
    """


class MigrateTopicsIntegrationTest(unittest.TestCase):

    layer = PLONE_APP_CONTENTTYPES_MIGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.request['ACTUAL_URL'] = self.portal.absolute_url()
        self.request['URL'] = self.portal.absolute_url()
        self.catalog = getToolByName(self.portal, "portal_catalog")
        self.portal.acl_users.userFolderAddUser('admin',
                                                'secret',
                                                ['Manager'],
                                                [])
        login(self.portal, 'admin')
        self.portal.portal_workflow.setDefaultChain(
            "simple_publication_workflow")
        self.portal.invokeFactory("Topic", "topic", title="Topic")
        self.portal.invokeFactory("Folder", "folder", title="Folder")

    def run_migration(self):
        migrate_topics(self.portal)

    def add_criterion(self, index, criterion, value=None):
        name = '%s_%s' % (index, criterion)
        self.portal.topic.addCriterion(index, criterion)
        crit = self.portal.topic.getCriterion(name)
        if value is not None:
            crit.setValue(value)
        return crit

    def test_migrate_simple_topic(self):
        self.assertEqual(self.portal.topic.portal_type, 'Topic')
        self.assertEqual(self.portal.topic.getLayout(), 'atct_topic_view')
        self.assertEqual(self.portal.topic.getLimitNumber(), False)
        self.assertEqual(self.portal.topic.getItemCount(), 0)
        self.assertEqual(self.portal.topic.getCustomViewFields(), ('Title',))
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        new = ICollection(self.portal.topic)
        self.assertEqual(self.portal.topic.portal_type, 'Collection')
        self.assertEqual(self.portal.topic.getLayout(), 'listing_view')
        self.assertEqual(new.sort_on, None)
        self.assertEqual(new.sort_reversed, None)
        self.assertEqual(new.limit, 1000)
        self.assertEqual(new.customViewFields, ('Title',))

    def test_migrate_topic_fields(self):
        self.portal.topic.setText('<p>Hello</p>')
        self.portal.topic.setLimitNumber(True)
        self.portal.topic.setItemCount(42)
        self.portal.topic.setCustomViewFields(('Title', 'Type'))
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        new = ICollection(self.portal.topic)
        self.assertEqual(self.portal.topic.portal_type, 'Collection')
        self.assertEqual(new.limit, 42)
        self.assertEqual(new.customViewFields, ('Title', 'Type'))

    def test_migrate_layout(self):
        self.portal.topic.setLayout('folder_summary_view')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(self.portal.topic.getLayout(), 'summary_view')

    def test_migrate_customView(self):
        self.portal.topic.setCustomView(True)
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(self.portal.topic.getLayout(), 'tabular_view')

    def test_migrate_nested_topic(self):
        self.portal.portal_types['Topic'].filter_content_types = False
        self.portal.topic.invokeFactory("Topic", "subtopic", title="Sub Topic")
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        fti = queryUtility(IDexterityFTI, name='Collection')
        # switch our a custom folderish base-class for collections
        # we need to use _updateProperty because this also refreshes
        # the content_meta_type attribute when klass has changed
        fti._updateProperty(
            'klass',
            'plone.app.contenttypes.tests.test_migration_topic.'
            'FolderishCollection')
        fti._updateProperty('allowed_content_types', ['Document', 'Folder'])
        fti._updateProperty('filter_content_types', False)
        self.run_migration()
        self.assertEqual(self.portal.topic.portal_type, 'Collection')
        self.assertEqual(self.portal.topic.subtopic.portal_type, 'Collection')

    def test_ATSimpleStringCriterion(self):
        self.add_criterion('SearchableText', 'ATSimpleStringCriterion', 'bar')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(
            self.portal.topic.query,
            [{'i': 'SearchableText',
              'o': 'plone.app.querystring.operation.string.contains',
              'v': 'bar'}]
        )

        # Check that the resulting query does not give an error.
        self.portal.topic.getQuery()

    def test_ATSimpleStringCriterionToSelection(self):
        # Some string criterions really should be selection criterions.
        self.add_criterion(
            'review_state',
            'ATSimpleStringCriterion', 'published'
        )
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(
            self.portal.topic.query,
            [{'i': 'review_state',
              'o': 'plone.app.querystring.operation.selection.any',
              'v': 'published'}]
        )

    def test_ATDateCriteriaPast(self):
        # More than 5 days in the past:
        crit = self.add_criterion('created', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('more')
        crit.setDateRange('-')
        # Less than 5 days in the past:
        crit = self.add_criterion('effective', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('less')
        crit.setDateRange('-')
        # The next two are logically a bit weird.
        # More than 0 days in the past is historically interpreted as: after
        # today.
        crit = self.add_criterion('expires', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('more')
        crit.setDateRange('-')
        # Less than 0 days in the past is historically interpreted as: before
        # today.
        crit = self.add_criterion('modified', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('less')
        crit.setDateRange('-')

        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(len(query), 4)

        self.assertEqual(query[0]['i'], 'created')
        self.assertEqual(
            query[0]['o'],
            'plone.app.querystring.operation.date.largerThanRelativeDate'
        )
        self.assertEqual(query[0]['v'], -5)

        self.assertEqual(query[1]['i'], 'effective')
        self.assertEqual(
            query[1]['o'],
            'plone.app.querystring.operation.date.lessThanRelativeDate'
        )
        self.assertEqual(query[1]['v'], -5)

        self.assertEqual(query[2]['i'], 'expires')
        self.assertEqual(
            query[2]['o'],
            'plone.app.querystring.operation.date.afterToday'
        )
        self.assertTrue('v' not in query[2].keys())

        self.assertEqual(query[3]['i'], 'modified')
        self.assertEqual(
            query[3]['o'],
            'plone.app.querystring.operation.date.beforeToday'
        )
        self.assertTrue('v' not in query[3].keys())

        # Check that the resulting query does not give an error.
        self.portal.topic.getQuery()

    def test_ATDateCriteriaFuture(self):
        # More than 5 days in the future:
        crit = self.add_criterion('created', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('more')
        crit.setDateRange('+')
        # Less than 5 days in the future:
        crit = self.add_criterion('effective', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('less')
        crit.setDateRange('+')
        # More than 0 days in the future: after today.
        crit = self.add_criterion('expires', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('more')
        crit.setDateRange('+')
        # Less than 0 days in the future: before today.
        crit = self.add_criterion('modified', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('less')
        crit.setDateRange('+')

        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(len(query), 4)

        self.assertEqual(query[0]['i'], 'created')
        self.assertEqual(
            query[0]['o'],
            'plone.app.querystring.operation.date.largerThanRelativeDate'
        )
        self.assertEqual(query[0]['v'], 5)

        self.assertEqual(query[1]['i'], 'effective')
        self.assertEqual(
            query[1]['o'],
            'plone.app.querystring.operation.date.lessThanRelativeDate'
        )
        self.assertTrue(query[1]['v'], 5)

        self.assertEqual(query[2]['i'], 'expires')
        self.assertEqual(
            query[2]['o'],
            'plone.app.querystring.operation.date.afterToday'
        )
        self.assertTrue('v' not in query[2].keys())

        self.assertEqual(query[3]['i'], 'modified')
        self.assertEqual(
            query[3]['o'],
            'plone.app.querystring.operation.date.beforeToday'
        )
        self.assertTrue('v' not in query[3].keys())

        # Check that the resulting query does not give an error.
        self.portal.topic.getQuery()

    def test_ATDateCriteriaExactDay(self):
        # 5 days ago:
        crit = self.add_criterion('created', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('within_day')
        crit.setDateRange('-')
        # 5 days from now:
        crit = self.add_criterion('effective', 'ATFriendlyDateCriteria', 5)
        crit.setOperation('within_day')
        crit.setDateRange('+')
        # past or future does not matter if the day is today.
        # today minus
        crit = self.add_criterion('expires', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('within_day')
        crit.setDateRange('-')
        # today plus
        crit = self.add_criterion('modified', 'ATFriendlyDateCriteria', 0)
        crit.setOperation('within_day')
        crit.setDateRange('+')

        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        time2 = DateTime()
        self.assertEqual(len(query), 4)

        self.assertEqual(query[0]['i'], 'created')
        self.assertEqual(
            query[0]['o'],
            'plone.app.querystring.operation.date.between'
        )
        self.assertEqual(
            query[0]['v'],
            ((time2 - 5).earliestTime(), (time2 - 5).latestTime())
        )

        self.assertEqual(query[1]['i'], 'effective')
        self.assertEqual(
            query[1]['o'],
            'plone.app.querystring.operation.date.between'
        )
        self.assertEqual(
            query[1]['v'],
            ((time2 + 5).earliestTime(), (time2 + 5).latestTime())
        )

        self.assertEqual(query[2]['i'], 'expires')
        self.assertEqual(
            query[2]['o'],
            'plone.app.querystring.operation.date.today'
        )
        self.assertFalse('v' in query[2].keys())

        self.assertEqual(query[3]['i'], 'modified')
        self.assertEqual(
            query[3]['o'],
            'plone.app.querystring.operation.date.today'
        )
        self.assertFalse('v' in query[3].keys())

        # Check that the resulting query does not give an error.
        self.portal.topic.getQuery()

    def test_ATCurrentAuthorCriterion(self):
        self.add_criterion('Creator', 'ATCurrentAuthorCriterion')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(
            self.portal.topic.query,
            [{'i': 'Creator',
              'o': 'plone.app.querystring.operation.string.currentUser',
              'v': 'admin'}]
        )

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATListCriterion(self):
        # The new-style queries do not currently offer the possibility
        # to choose if the given values should be joined with 'or' or
        # 'and'.  Default is 'or'.
        crit = self.add_criterion('Subject', 'ATListCriterion', ('foo', 'bar'))
        crit.setOperator('or')
        # Note: this could have been an ATPortalTypeCriterion too:
        crit = self.add_criterion(
            'portal_type',
            'ATListCriterion', ('Document', 'Folder')
        )
        crit.setOperator('and')

        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(len(query), 2)
        self.assertEqual(query[0],
                         {'i': 'Subject',
                          'o': 'plone.app.querystring.operation.selection.any',
                          'v': ('foo', 'bar')})
        self.assertEqual(query[1],
                         {'i': 'portal_type',
                          'o': 'plone.app.querystring.operation.selection.any',
                          'v': ('Document', 'Folder')})

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATPathCriterion(self):
        crit = self.add_criterion(
            'path',
            'ATPathCriterion', self.portal.folder.UID())
        crit.setRecurse(True)
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(self.portal.topic.query,
                         [{'i': 'path',
                           'o': 'plone.app.querystring.operation.string.path',
                           'v': self.portal.folder.UID()}])
        # check is the query is correct
        self.assertEqual(
            parseFormquery(self.portal, self.portal.topic.query),
            {'path': {'query': ['/plone/folder']}})

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATPathCriterionNonRecursive(self):
        # Topics supported non recursive search, so search at a
        # specific depth of 1.  At first, new Collections did not
        # support it.  But since plone.app.querystring 1.1.0 it works.
        crit = self.add_criterion(
            'path',
            'ATPathCriterion', self.portal.folder.UID()
        )
        crit.setRecurse(False)
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(len(query), 1)
        self.assertEqual(query,
                         [{'i': 'path',
                           'o': 'plone.app.querystring.operation.string.path',
                           'v': self.portal.folder.UID() + '::1'}])

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATPathCriterionMultiRecursive(self):
        # Collections support multiple paths since
        # plone.app.querystring 1.2.0.
        login(self.portal, 'admin')
        self.portal.invokeFactory("Folder", "folder2", title="Folder 2")
        crit = self.add_criterion(
            'path',
            'ATPathCriterion',
            [self.portal.folder.UID(), self.portal.folder2.UID()]
        )
        crit.setRecurse(True)
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(len(query), 2)
        self.assertEqual(query[0],
                         {'i': 'path',
                          'o': 'plone.app.querystring.operation.string.path',
                          'v': self.portal.folder.UID()})
        self.assertEqual(query[1],
                         {'i': 'path',
                          'o': 'plone.app.querystring.operation.string.path',
                          'v': self.portal.folder2.UID()})

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATPathCriterionMultiNonRecursive(self):
        # Collections support multiple paths since
        # plone.app.querystring 1.2.0.
        login(self.portal, 'admin')
        self.portal.invokeFactory("Folder", "folder2", title="Folder 2")
        crit = self.add_criterion(
            'path',
            'ATPathCriterion',
            [self.portal.folder.UID(), self.portal.folder2.UID()]
        )
        crit.setRecurse(False)
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(len(query), 2)
        self.assertEqual(query[0],
                         {'i': 'path',
                          'o': 'plone.app.querystring.operation.string.path',
                          'v': self.portal.folder.UID() + '::1'})
        self.assertEqual(query[1],
                         {'i': 'path',
                          'o': 'plone.app.querystring.operation.string.path',
                          'v': self.portal.folder2.UID() + '::1'})

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATBooleanCriterion(self):
        # Note that in standard Plone the boolean criterion is only
        # defined for is_folderish and is_default_page.
        crit = self.add_criterion('is_folderish', 'ATBooleanCriterion')
        crit.setBool(True)
        crit = self.add_criterion('is_default_page', 'ATBooleanCriterion')
        crit.setBool(False)
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(len(query), 2)
        self.assertEqual(
            query[0],
            {'i': 'is_folderish',
             'o': 'plone.app.querystring.operation.boolean.isTrue'}
        )
        self.assertEqual(
            query[1],
            {'i': 'is_default_page',
             'o': 'plone.app.querystring.operation.boolean.isFalse'}
        )

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATDateRangeCriteria(self):
        time1 = DateTime()
        # Days in the past:
        crit = self.add_criterion('created', 'ATDateRangeCriterion')
        crit.setStart(time1 - 5)
        crit.setEnd(time1 - 3)
        # Past and future:
        crit = self.add_criterion('effective', 'ATDateRangeCriterion')
        crit.setStart(time1 - 2)
        crit.setEnd(time1 + 2)
        # Days in the future:
        crit = self.add_criterion('expires', 'ATDateRangeCriterion')
        crit.setStart(time1 + 3)
        crit.setEnd(time1 + 5)

        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(len(query), 3)

        self.assertEqual(query[0]['i'], 'created')
        self.assertEqual(
            query[0]['o'],
            'plone.app.querystring.operation.date.between'
        )
        self.assertEqual(query[0]['v'], (time1 - 5, time1 - 3))

        self.assertEqual(query[1]['i'], 'effective')
        self.assertEqual(
            query[1]['o'],
            'plone.app.querystring.operation.date.between'
        )
        self.assertEqual(query[1]['v'], (time1 - 2, time1 + 2))

        self.assertEqual(query[2]['i'], 'expires')
        self.assertEqual(
            query[2]['o'],
            'plone.app.querystring.operation.date.between'
        )
        self.assertEqual(query[2]['v'], (time1 + 3, time1 + 5))

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATPortalTypeCriterion(self):
        self.add_criterion(
            'portal_type',
            'ATPortalTypeCriterion', ('Document', 'Folder')
        )
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(
            query,
            [{'i': 'portal_type',
              'o': 'plone.app.querystring.operation.selection.any',
              'v': ('Document', 'Folder')}]
        )

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATPortalTypeCriterionOfTopic(self):
        # We migrate Topics to Collections, so we should update
        # criterions that search for Topics.
        self.add_criterion(
            'portal_type',
            'ATPortalTypeCriterion', ('Topic',)
        )
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(
            query,
            [{'i': 'portal_type',
              'o': 'plone.app.querystring.operation.selection.any',
              'v': ('Collection',)}])

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATSelectionCriterion(self):
        # The new-style queries do not currently offer the possibility
        # to choose if the given values should be joined with 'or' or
        # 'and'.  Default is 'or'.
        crit = self.add_criterion(
            'Subject',
            'ATSelectionCriterion',
            ('foo', 'bar')
        )
        crit.setOperator('or')
        # Note: this could have been an ATPortalTypeCriterion too:
        # Note that we check that Topic is turned into Collection too.
        crit = self.add_criterion(
            'portal_type',
            'ATSelectionCriterion',
            ('Document', 'Topic')
        )
        crit.setOperator('and')

        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(len(query), 2)
        self.assertEqual(query[0],
                         {'i': 'Subject',
                          'o': 'plone.app.querystring.operation.selection.any',
                          'v': ('foo', 'bar')})
        self.assertEqual(query[1],
                         {'i': 'portal_type',
                          'o': 'plone.app.querystring.operation.selection.any',
                          'v': ('Document', 'Collection')})

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATSelectionCriterionForTypeTitle(self):
        # 'portal_type' is the object id of the FTI in portal_types.
        # 'Type' is the title of that object.
        # For example:
        # - portal_type 'Document' has Type 'Page'.
        # - portal_type 'Topic' has Type 'Collection (old)'.
        # Type is not enabled as criterion index by default, so we
        # want to migrate to a portal_type criterion instead.
        self.add_criterion('Type', 'ATSelectionCriterion', ('Page', 'Folder'))
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        query = self.portal.topic.query
        self.assertEqual(
            query,
            [{'i': 'portal_type',
              'o': 'plone.app.querystring.operation.selection.any',
              'v': ['Document', 'Folder']}])

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATReferenceCriterion(self):
        # Note: the new criterion is disabled by default.  Also, it
        # needs the _referenceIs function in the plone.app.querystring
        # queryparser and that function is not defined.
        self.add_criterion(
            'getRawRelatedItems',
            'ATReferenceCriterion',
            self.portal.folder.UID()
        )
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        # TODO re-enable this check when the queryparser works.
        # self.assertEqual(
        #     self.portal.topic.query,
        #     [{'i': 'getRawRelatedItems',
        #       'o': 'plone.app.querystring.operation.reference.is',
        #       'v': (portal.folder.UID(),)}]
        # )

        # Check that the resulting query does not give an error.
        # self.portal.topic.results

    def test_ATRelativePathCriterion(self):
        crit = self.add_criterion(
            'path',
            'ATRelativePathCriterion'
        )
        crit.setRelativePath('../folder')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(
            self.portal.topic.query,
            [{'i': 'path',
              'o': 'plone.app.querystring.operation.string.relativePath',
              'v': '../folder'}]
        )

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATRelativePathCriterionNonRecursive(self):
        # Topics supported non recursive search, so search at a specific
        # depth.  New Collections do not support it.
        crit = self.add_criterion('path', 'ATRelativePathCriterion')
        crit.setRelativePath('../folder')
        crit.setRecurse(True)
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(
            self.portal.topic.query,
            [{'i': 'path',
              'o': 'plone.app.querystring.operation.string.relativePath',
              'v': '../folder'}])

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATSimpleIntCriterion(self):
        self.add_criterion('getObjPositionInParent', 'ATSimpleIntCriterion', 7)
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(self.portal.topic.query,
                         [{'i': 'getObjPositionInParent',
                           'o': 'plone.app.querystring.operation.int.is',
                           'v': 7}])

        # Check that the resulting query does not give an error.
        self.portal.topic.results

    def test_ATSimpleIntCriterionMinimum(self):
        crit = self.add_criterion(
            'getObjPositionInParent',
            'ATSimpleIntCriterion', 6
        )
        crit.setDirection('min')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(
            self.portal.topic.query,
            [{'i': 'getObjPositionInParent',
              'o': 'plone.app.querystring.operation.int.largerThan',
              'v': 6}]
        )

        # Check that the resulting query does not give an error.
        self.portal.topic.getQuery()

    def test_ATSimpleIntCriterionMaximum(self):
        crit = self.add_criterion(
            'getObjPositionInParent',
            'ATSimpleIntCriterion',
            5
        )
        crit.setDirection('max')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(
            self.portal.topic.query,
            [{'i': 'getObjPositionInParent',
              'o': 'plone.app.querystring.operation.int.lessThan',
              'v': 5}]
        )

        # Check that the resulting query does not give an error.
        self.portal.topic.getQuery()

    def test_ATSimpleIntCriterionBetween(self):
        # This is not supported.
        crit = self.add_criterion(
            'getObjPositionInParent',
            'ATSimpleIntCriterion',
            4
        )
        crit.setDirection('min:max')
        crit.setValue2(8)
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(self.portal.topic.query, [])

        # Check that the resulting query does not give an error.
        self.portal.topic.getQuery()

    def test_ATSortCriterion(self):
        self.add_criterion('modified', 'ATSortCriterion')
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(self.portal.topic.sort_on, 'modified')
        self.assertEqual(self.portal.topic.sort_reversed, False)
        self.assertEqual(self.portal.topic.query, [])

        # Check that the resulting query does not give an error.
        self.portal.topic.getQuery()

    def test_ATSortCriterionReversed(self):
        crit = self.add_criterion('created', 'ATSortCriterion')
        crit.setReversed(True)
        applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.run_migration()
        self.assertEqual(self.portal.topic.sort_on, 'created')
        self.assertEqual(self.portal.topic.sort_reversed, True)
        self.assertEqual(self.portal.topic.query, [])

        # Check that the resulting query does not give an error.
        self.portal.topic.getQuery()
