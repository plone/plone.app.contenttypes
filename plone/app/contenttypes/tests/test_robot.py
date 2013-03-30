import os
import unittest

from plone.testing import layered

import robotsuite

from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_ROBOT_TESTING
)


def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    robot_dir = os.path.join(current_dir, 'robot')
    robot_tests = [
        os.path.join('robot', doc) for doc in
        os.listdir(robot_dir) if doc.endswith('.robot') and
        doc.startswith('test_')
    ]
    for test in robot_tests:
        suite.addTests([
            layered(robotsuite.RobotTestSuite(test),
                    layer=PLONE_APP_CONTENTTYPES_ROBOT_TESTING),
        ])
    return suite
