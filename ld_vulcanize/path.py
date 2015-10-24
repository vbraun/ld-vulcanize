"""
Abstraction of a path
"""

import os


class Path(object):

    def __init__(self, path):
        if isinstance(path, Path):
            self._abs = path.absolute()
        else:
            self._abs = os.path.abspath(os.path.realpath(path))
        if not os.path.exists(self.absolute()):
            raise ValueError('path must be an existing file or directory, got {0}'.format(self))

    def __repr__(self):
        return self._abs
        
    def absolute(self):
        """
        Return the absolute path

        Returns:
            str: The absolute path
        """
        return self._abs

    def is_dir(self):
        return os.path.isdir(self.absolute())
    
    def is_abs(self):
        return os.path.isabs(self.absolute())
    
    def relative(self, base):
        """
        Return the path relative to ``base``
        """
        if not base.is_dir():
            return os.path.relpath(self.absolute(), base.dirname())
        else:
            return os.path.relpath(self.absolute(), base.absolute())

    def dirname(self):
        return os.path.dirname(self.absolute())
        
    def __hash__(self):
        return hash(self.absolute())
    
    def __add__(lhs, rhs):
        return Path(os.path.join(lhs.absolute(), rhs))

    def __eq__(lhs, rhs):
        if not isinstance(rhs, Path):
            rhs = Path(rhs)
        return lhs.absolute() == rhs.absolute()

    def __contains__(self, path):
        return path.absolute().startswith(self.absolute())

