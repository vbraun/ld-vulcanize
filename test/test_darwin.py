

import sys
import unittest
from ld_vulcanize.tool.otool import otool_load_commands
from ld_vulcanize.binary import SharedLibraryOSX, ExecutableOSX

class TestOtool(unittest.TestCase):

    BINARY = '/bin/ls'
    
    def test_otool_list(self):
        cmds = list(otool_load_commands(self.BINARY))
        dyld = filter(lambda cmd: cmd['cmd'] == 'LC_LOAD_DYLIB', cmds)
        self.assertTrue(len(dyld) > 0)
        

    def test_otool_dependents(self):
        exe = ExecutableOSX('/usr/bin/python')
        self.assertIn('/usr/lib/libSystem.B.dylib', exe.find_dependents())
