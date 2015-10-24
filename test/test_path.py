
import os
import unittest

from ld_vulcanize.path import Path


class TestPath(unittest.TestCase):

    def test_add(self):
        self.assertEqual(
            Path('/usr') + 'bin',
            Path('/usr/bin')
        )


    def test_contains(self):
        usr = Path('/usr')
        usr_bin = Path('/usr/bin')
        self.assertTrue(usr_bin in usr)
        self.assertFalse(usr in usr_bin)
        
        



