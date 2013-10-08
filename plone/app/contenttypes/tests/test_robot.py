# -*- coding: utf-8 -*-
from plone.testing import layered
from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_ROBOT_TESTING
)
import os
import robotsuite
import unittest

UNIT_TEST_LEVEL = 1
INTEGRATION_TEST_LEVEL = 2
FUNCTIONAL_TEST_LEVEL = 3
ROBOT_TEST_LEVEL = 5


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc) for doc in
        os.listdir(robot_dir) if doc.endswith('.robot') and
        doc.startswith('test_')
    ]
    for robot_test in robot_tests:
        robottestsuite = robotsuite.RobotTestSuite(robot_test)
        robottestsuite.level = ROBOT_TEST_LEVEL
        suite.addTests([
            layered(
                robottestsuite,
                layer=PLONE_APP_CONTENTTYPES_ROBOT_TESTING
            ),
        ])
    return suite
