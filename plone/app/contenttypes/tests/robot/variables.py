# -*- coding: utf-8 -*-
from pkg_resources import resource_filename

TEST_FOLDER_ID = 'robot-test-folder'
PLONE_PATH = '/plone'
COLLECTION_TEST_QUERY = '[{"i": "path", "o": "plone.app.querystring.operation.string.path", "v": "%s/%s"}]' % (PLONE_PATH, TEST_FOLDER_ID)  # noqa
PATH_TO_TEST_FILES = resource_filename("plone.app.contenttypes.tests", "")
