"""
Find Files in the Filesystem
"""

import os
import sys

from ld_vulcanize.logger import log
from ld_vulcanize.path import Path
from ld_vulcanize.binary import platform_dependent


class Find(object):

    def __init__(self, root_path, factory=Path):
        self._path = Path(root_path)
        self._factory = factory

    def __iter__(self):
       for path, dirs, files in os.walk(self._path.absolute()):
           for filename in files:
               yield self._factory(os.path.join(path, filename))
    


class UniqueFactory(object):

    _cache = dict()
    
    def __init__(self, factory):
        self._factory = factory

    @property
    def EXT(self):
        return self._factory.EXT
        
    def __call__(self, path):
        if not isinstance(path, Path):
            path = Path(path)
        try:
            return self._cache[path]
        except KeyError:
            obj = self._factory(path)
            self._cache[path] = obj
            return obj

                   
                   
class ArtifactFinder(object):

    SharedLibrary = platform_dependent(sys.platform)['shared_library']
    Executable = platform_dependent(sys.platform)['executable']

    def __init__(self, path):
        self._shared_library_factory = UniqueFactory(self.SharedLibrary)
        self._executable_factory = UniqueFactory(self.Executable)
        path = Path(path)
        self._init_pre()
        if path.is_dir():
            self._root_path = path
            self._init_binaries()
        else:
            root_path, filename = os.path.split(path.absolute())
            self._root_path = Path(root_path)
            self._init_binary(path)
        self._init_dependents()
        self._init_post()
        self._init_links()
            
    @property
    def root_path(self):
        return self._root_path

    def _init_pre(self):
        self._shlib_name = dict()
        self._internal_path = dict()
        self._external_path = dict()
        self._executable = set()

    def _init_post(self):
        self._internal_shlib = frozenset(self._internal_path.values())
        self._external_shlib = frozenset(self._external_path.values())
        log.info('Found {0} shared libraries'.format(len(self._internal_shlib)))
        self._executable = frozenset(self._executable)
        log.info('Found {0} executables'.format(len(self._executable)))

    def _init_links(self):
        everything = list(self.executable) + list(self.internal_shlib) + list(self.external_shlib)
        for artifact in everything:
            internal = []
            external = []
            for path in artifact.dependents:
                shlib_int = self._internal_path.get(path, None)
                shlib_ext = self._external_path.get(path, None)
                if shlib_int:
                    assert shlib_ext is None
                    internal.append(shlib_int)
                if shlib_ext:
                    assert shlib_int is None
                    external.append(shlib_ext)
            artifact._init_shlib(internal, external)
        
    def _init_binaries(self):
        log.info('Searching binaries {0}'.format(self.root_path))
        find = Find(self._root_path)
        count = 0
        for path in iter(find):
            if path in self._root_path:   # skip symlinked binaries
                self._init_binary(path)
                count += 1
        log.info('Found {0} files'.format(count))

    def _init_binary(self, path):            
        if self.SharedLibrary.is_file(path):
            self._make_shared_library(path)
        elif self.Executable.is_file(path):
            self._make_executable(path)
        else:
            pass  # not interesting file

    def _init_dependents(self):
        log.info('Searching executable dependencies')
        for exe in self._executable:
            exe._init_dependents(self, self._make_shared_library)
        log.info('Searching shared library dependencies')
        for shlib in self._internal_path.values():
            shlib._init_dependents(self, self._make_shared_library)
        num_internal = len(self._internal_path)
        for shlib in self._external_path.values():
            # Do not create new shared library objects from dependents
            shlib._init_dependents(self)
        assert num_internal == len(self._internal_path), 'external libraries cannot link internal ones'
        log.info('Found {0} external shared libraries'.format(len(self._external_path)))
        
    def _make_shared_library(self, path):
        shlib = self._shared_library_factory(path)
        if shlib.path in self.root_path:
            self._internal_path[shlib.path] = shlib
        else:
            self._external_path[shlib.path] = shlib
        if shlib.filename in self._shlib_name:
            if self._shlib_name[shlib.filename] is not None:
                log.info('Duplicate library filename: {0} and {1}'.format(
                    shlib.path,
                    self._shlib_name[shlib.filename].path
                ))
            self._shlib_name[shlib.filename] = None
        else:
            self._shlib_name[shlib.filename] = shlib
                  
    def _make_executable(self, path):
        exe = self._executable_factory(path)
        self._executable.add(exe)

    def _init_library_dependencies(self):
        for shlib in self._internal_shlib:
            pass
        
    @property
    def internal_shlib(self):
        """
        Project-Internal Shared Libraries

        This are all shared libraries that are inside the specified
        project root.
        """
        return self._internal_shlib
        
    @property
    def external_shlib(self):
        """
        Project-External Shared Libraries

        This are all linked shared libraries that are outside of the
        specified project root. They are not transitively closed, that
        is, the external libraries in the output may link to further
        external libraries that are not in the output.

        Since we can only modify :meth:`internal_shlib` libraries we
        do not need the transitive closure.
        """
        return frozenset(self._external_shlib)
        
    @property
    def executable(self):
        """
        Project-Internal Executables
        """
        return self._executable

    @property
    def internal_artifacts(self):
        """
        Project-Internal Binaries

        Returns:
            Executables and internal shared libraries. This is the set
            of artifacts that need to be rewritten.
        """
        return list(self.executable) + list(self.internal_shlib)
    
    def pretty_print(self):
        print('#' * 79)
        print('# Internal shared libraries')
        for shlib in self.internal_shlib:
            print('File {0}:'.format(shlib.path))
        print('#' * 79)
        print('# External shared libraries')
        for shlib in self.external_shlib:
            print('File {0}:'.format(shlib.path))
        print('#' * 79)
        print('# Executables')
        for exe in self.executable:
            print('File {0}:'.format(exe.path))
        
    def make_paths_relative(self):
        for artifact in self.internal_artifacts:
            artifact.make_paths_relative()
            
    def make_paths_absolute(self):
        for artifact in self.internal_artifacts:
            artifact.make_paths_absolute()
            

