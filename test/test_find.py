
import os
import unittest

from ld_vulcanize.path import Path
from ld_vulcanize.find import ArtifactFinder


class TestFindBinaries(unittest.TestCase):

    def setUp(self):
        import _sqlite3
        self.ld_dynload = Path(os.path.dirname(_sqlite3.__file__))

    def tearDown(self):
        pass

    def test_find_binaries(self):
        binaries = ArtifactFinder(self.ld_dynload)
        sqlite_path = self.ld_dynload + '_sqlite3.so'
        self.assertTrue(any(
            shlib.path == sqlite_path for shlib in binaries.internal_shlib
        ))

