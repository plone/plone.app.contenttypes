import os
import unittest

from plone.testing import layered

import robotsuite

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_ACCEPTANCE_TESTING

def test_suite():
    suite = unittest.TestSuite()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    acceptance_dir = os.path.join(current_dir, 'acceptance')
    acceptance_tests = [os.path.join('acceptance', doc) for doc in
                        os.listdir(acceptance_dir) if doc.endswith('.txt') and 
                        doc.startswith('test_')]              
    for test in acceptance_tests:
        suite.addTests([
            layered(robotsuite.RobotTestSuite(test),
                    layer=PLONE_APP_CONTENTTYPES_ACCEPTANCE_TESTING),
        ])
    return suite
