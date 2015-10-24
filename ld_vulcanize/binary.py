"""
Abstraction for binaries (executables and shared libraries)
"""

import subprocess
import os

from ld_vulcanize.logger import log
from ld_vulcanize.path import Path


class FilesystemArtifact(object):

    def __init__(self, filename):
        self._path = Path(filename)

    def _init_dependents(self, binaries, make_shared_library=None):
        dependents = []
        for path in self.find_dependents():
            log.debug('Found that %s depends on %s', self.path, path)
            if not path.is_abs():
                raise RuntimeError('dependent {0} is not absolute path'.format(path))
            else:
                dependents.append(path)
                if path in binaries._internal_path:
                    # shared library already found inside the root path
                    if path not in binaries.root_path:
                        raise RuntimeError('internal {0} not in {1}'.format(path, binaries.root_path))
                else:
                    # must be external library
                    if path in binaries.root_path:
                        raise RuntimeError('library {0} in {1}'.format(path, binaries.root_path))
                    if make_shared_library:
                        make_shared_library(path)
        self._dependents = tuple(dependents)

    @property
    def dependents(self):
        """
        Return all dependents

        All shared libraries that are linked by the artifact as
        :class:`ld_vulcanize.path.Path` objects.
        """
        return self._dependents
        
    def _init_shlib(self, internal_shlib, external_shlib):
        self._internal_shlib = frozenset(internal_shlib)
        self._external_shlib = frozenset(external_shlib)

    @property
    def internal_shlib(self):
        return self._internal_shlib
        
    @property
    def external_shlib(self):
        return self._external_shlib
        
    @property
    def path(self):
        return self._path

    @property
    def filename(self):
        return os.path.split(self.path.absolute())[1]

    def __eq__(self, other):
        return self.path == other.path

    def __hash__(self):
        return hash(self.path)

    def find_dependents(self):
        raise NotImplementedError('to be implemented in derived class')
    




class SharedLibraryABC(FilesystemArtifact):

    EXT = frozenset()

    @classmethod
    def is_file(cls, path):
        basename, extension = os.path.splitext(path.absolute())
        return extension in cls.EXT
    
    def __repr__(self):
        return 'SO:{0}'.format(self.filename)


class SharedLibraryOSX(SharedLibraryABC):

    EXT = frozenset(['.dylib', '.so'])

    def find_dependents(self):
        self._linker_path = dict()
        from ld_vulcanize.tool.otool import otool_load_commands, ActualPath
        actual_path = ActualPath(loader_path=self.path.dirname())
        for load_cmd in otool_load_commands(self.path):
            if load_cmd['cmd'] == 'LC_LOAD_DYLIB':
                linker_path = load_cmd['filename']
                path = actual_path(linker_path)
                self._linker_path[path] = linker_path
                yield path
            if load_cmd['cmd'] == 'LC_ID_DYLIB':
                # install name for a dylib; only relevant when linking but not when executing
                # print('LC_ID_DYLIB', self, load_cmd)
                pass

    def make_paths_relative(self):
        for shlib in self.internal_shlib:
            self._make_path_relative_for(shlib)

    def make_paths_absolute(self):
        for shlib in self.internal_shlib:
            self._make_path_absolute_for(shlib)
            
    def _make_path_relative_for(self, shlib):
        cmd = [
            'install_name_tool',
            '-change',
            self._linker_path[shlib.path],
            os.path.join('@loader_path', shlib.path.relative(self.path)),
            str(self.path)
        ]
        log.debug('Exec: "{0}"'.format(' '.join(cmd)))
        subprocess.check_call(cmd)
            
    def _make_path_absolute_for(self, shlib):
        cmd = [
            'install_name_tool',
            '-change',
            self._linker_path[shlib.path],
            str(shlib.path),
            str(self.path)
        ]
        log.debug('Exec: "{0}"'.format(' '.join(cmd)))
        subprocess.check_call(cmd)

                
    
class SharedLibraryLinux(SharedLibraryABC):

    EXT = frozenset(['.so'])    

    

class ExecutableABC(FilesystemArtifact):

    @classmethod
    def is_file(cls, path):
        if not os.access(path.absolute(), os.X_OK):
            return False
        with open(path.absolute(), 'rb') as f:
            head = f.read(512)
        for magic in cls.MAGIC:
            if head.startswith(magic):
                return True
        return False

    def __repr__(self):
        return 'EX:{0}'.format(self.filename)
    
        

class ExecutableOSX(ExecutableABC):

    MAGIC = frozenset([
        '\xCA\xFE\xBA\xBE',  # Mach-O Fat Binary
        '\xFE\xED\xFA\xCE',  # Mach-O binary (32-bit)
        '\xFE\xED\xFA\xCF',  # Mach-O binary (64-bit)
        '\xCE\xFA\xED\xFE',  # Mach-O binary (reverse byte ordering scheme, 32-bit)
        '\xCF\xFA\xED\xFE',  # Mach-O binary (reverse byte ordering scheme, 64-bit)
    ])

    def find_dependents(self):
        self._linker_path = dict()
        from ld_vulcanize.tool.otool import otool_load_commands, ActualPath
        actual_path = ActualPath(executable_path=self.path.dirname())
        for load_cmd in otool_load_commands(self.path):
            if load_cmd['cmd'] == 'LC_LOAD_DYLIB':
                linker_path = load_cmd['filename']
                path = actual_path(linker_path)
                self._linker_path[path] = linker_path
                yield path
            if load_cmd['cmd'] == 'LC_ID_DYLIB':
                # Is that legal in an executable?
                print('LC_ID_DYLIB', self, load_cmd)

    def make_paths_relative(self):
        for shlib in self.internal_shlib:
            self._make_path_relative_for(shlib)

    def make_paths_absolute(self):
        for shlib in self.internal_shlib:
            self._make_path_absolute_for(shlib)
            
    def _make_path_relative_for(self, shlib):
        cmd = [
            'install_name_tool',
            '-change',
            self._linker_path[shlib.path],
            os.path.join('@executable_path', shlib.path.relative(self.path)),
            str(self.path)
        ]
        log.debug('Exec: "{0}"'.format(' '.join(cmd)))
        subprocess.check_call(cmd)

    def _make_path_absolute_for(self, shlib):
        cmd = [
            'install_name_tool',
            '-change',
            self._linker_path[shlib.path],
            str(shlib.path),
            str(self.path)
        ]
        log.debug('Exec: "{0}"'.format(' '.join(cmd)))
        subprocess.check_call(cmd)
        
            
            
                
class ExecutableLinux(ExecutableABC):

    MAGIC = frozenset(['\x7fELF'])

    



def platform_dependent(platform):
    if platform == 'darwin':
        return dict(
            shared_library=SharedLibraryOSX,
            executable=ExecutableOSX,
        )
    elif platform == 'linux2':
        return dict(
            shared_library=SharedLibraryLinux,
            executable=ExecutableLinux,
        )
    else:
        raise ValueError('platform not supported: {0}'.format(platform))

   
