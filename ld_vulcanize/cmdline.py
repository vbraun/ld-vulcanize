# -*- encoding: utf-8 -*-
"""
Handle Command Line Options
"""

import sys
import os
import warnings
import argparse

from ld_vulcanize.logger import log
from ld_vulcanize.path import Path
from ld_vulcanize.find import ArtifactFinder


description = \
"""
Rewrite Library Paths
"""

def make_parser():
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--log', dest='log', default=None,
        help='one of [DEBUG, INFO, ERROR, WARNING, CRITICAL]')
    parser.add_argument(
        '--path', dest='path', required=True,
        help='root of the directory tree to operate on')
    parser.add_argument(        
        '--rewrite', dest='rewrite', default='readonly',
        help="""one of [readonly, relative, absolute]. How to rewrite the library
        search paths. Default: readonly (no changes written to
        disk)""")
    return parser



def launch():
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])
    if args.log is not None:
        import logging
        level = getattr(logging, args.log)
        log.setLevel(level=level)

    path = Path(args.path)
    binaries = ArtifactFinder(path)
    
    if args.rewrite == 'readonly':
        binaries.pretty_print()
    elif args.rewrite == 'relative':
        binaries.make_paths_relative()
    elif args.rewrite == 'absolute':
        binaries.make_paths_absolute()
    else:
        raise RuntimeError('invalid value for rewrite: {0}'.format(args.rewrite))
        
        


