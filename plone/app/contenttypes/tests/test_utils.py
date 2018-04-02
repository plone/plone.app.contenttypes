# -*- coding: utf-8 -*-
from plone.app.contenttypes.utils import human_readable_size

import unittest


class PloneAppContenttypesUtilsTestCase(unittest.TestCase):

    def test_human_readable_size(self):
        self.assertEqual(human_readable_size(0), '0 B')
        self.assertEqual(human_readable_size(1), '1 B')
        size = 1000
        self.assertEqual(human_readable_size(1000), '1000 B')
        size += 24
        self.assertEqual(human_readable_size(size), '1.0 KB')
        size += 512
        self.assertEqual(human_readable_size(size), '1.5 KB')
        size *= 1024
        self.assertEqual(human_readable_size(size), '1.5 MB')
        size *= 1024
        self.assertEqual(human_readable_size(size), '1.5 GB')
        size *= 1024
        self.assertEqual(human_readable_size(size), '1536.0 GB')
