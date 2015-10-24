
import subprocess
import re as re

from ld_vulcanize.path import Path


def otool_load_commands(path):
    """
    Parse ``otool -l`` output  
    """
    output = subprocess.check_output(['otool', '-l', str(path)])
    separator = re.compile('Load command ')
    blocks = separator.split(output)
    for i, load_cmd in enumerate(blocks[1:]):
        cmd = dict()
        lines = load_cmd.splitlines()
        assert i == int(lines[0])
        for line in lines[1:]:
            if line == 'Section':
                break  # Ignore section details for LC_SEGMENT*
            key, value = line.lstrip().split(' ', 1)
            cmd[key] = value
            if key == 'name':
                cmd['filename'] = value.split(' ', 1)[0]
        yield cmd
    


class ActualPath(object):

    EXECUTABLE_PATH = '@executable_path'
    LOADER_PATH = '@loader_path'
    RPATH = '@rpath'
    
    def __init__(self, executable_path=None, loader_path=None, rpath=None):
        """
        Functor to replace dyld special path components
        """
        self._executable_path = executable_path
        self._loader_path = loader_path
        self._rpath = rpath

    def __call__(self, loader_path):
        path = str(loader_path)
        if path.startswith(self.EXECUTABLE_PATH):
            if self._executable_path is None:
                raise RuntimeError('need executable path to resolve {0}'.format(path))
            path = self._executable_path + path[len(self.EXECUTABLE_PATH):]
        if path.startswith(self.LOADER_PATH):
            if self._loader_path is None:
                raise RuntimeError('need loader path to resolve {0}'.format(path))
            path = self._loader_path + path[len(self.LOADER_PATH):]
        if path.startswith(self.RPATH):
            if self._rpath is None:
                raise RuntimeError('need rpath to resolve {0}'.format(path))
            path = self._rpath + path[len(self.RPATH):]
        return Path(path)
    
