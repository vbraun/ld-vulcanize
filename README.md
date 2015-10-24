Self-Contained Library Paths
============================

This program rewrites search paths in executables and shared libraries
to be relative instead of absolute, and vice versa. This makes a
collection of binaries in a specific path relocatable.

Example (OSX)
=============

Say you have a project tree

  * `/prefix`: Directory
  * `/prefix/bin/foo`: Executable linking to libfoo
  * `/prefix/lib/libfoo.dylib`: Shared library linking to libbar
  * `/prefix/lib/libbar.dylib`: Shared library

Absolute paths means:

  * `/prefix/bin/foo` links to `/prefix/lib/libfoo.dylib`
  * `/prefix/lib/libfoo.dylib` links to `/prefix/lib/libbar.dylib`

Relative paths means:

  * `/prefix/bin/foo` links to `@executable_path/../lib/libfoo.dylib`
  * `/prefix/lib/libfoo.dylib` links to `@loader_path/libbar.dylib`

This tool converts one to the other. Typically, your build process
uses absolute paths everywhere, and if you rename the build tree
`/prefix` then the binaries do not work any more as they cannot find
the shared libraries any more. Solution: Rewrite everything under
`/prefix` to use relative paths:

    $ ld_vulcanize --path=/prefix --rewrite=relative


`DYLD_LIBRARY_PATH` is Evil
---------------------------

Another "solution" is to set `DYLD_LIBRARY_PATH=/prefix/lib` and have
wonky/incorrect paths for the linker paths. Since `DYLD_LIBRARY_PATH`
has precedence, `/prefix/bin/foo` then still works despites paths
pointing to the wrong directories. But it has also severe
disadvantages:

* Needs special environment variable. So you can't just execute the
  binaries any more.

* Name collisions: Other executables that happen to link to their own
  `libfoo.dylib` will not work any more, as `DYLD_LIBRARY_PATH` has
  precedence. Especially fun if bash is the affected binary because
  you have an incompatible `libreadline.dylib`.

* Apple broke `DYLD_LIBRARY_PATH`: In OSX 10.11, it is not passed
  through script interpreters.



Caveats
=======


Caveat: Other Relative Path Schemes
-----------------------------------

There are other strategies for relative paths, e.g. using `@rpath` or
using `@executable_path` also in intermediate shared libraries. They
are ambiguous since multiple binaries might be linking to the very
same shared library. Although such an relative path strategy might
very well work, ``ld_vulcanize`` cannot rewrite it back to absolute
paths.


Caveat: DYLD Install Names
--------------------------

This tool does not deal with OSX dyld install names; They are
important at link time but not at run time.


Caveat: Hardlinks
-----------------

Does not work for hardlinked binaries in different paths. For example:
Git installs hardlinks of the same binary into both
``$prefix/bin/git`` and ``$prefix/lib/libexec/git-core/git`. The
correct relative library path is either ``../lib/libz.so`` or
``../../libz.so``, but since there is only one underlying binary one
of them will be wrong. Whichever relative path we pick will break the
other hardlink of ``git``.

Solution: Replace hard links with soft links.




Name
====

Vulcanize

1. to treat (rubber) with sulphur or sulphur compounds under heat and
   pressure to improve elasticity and strength or to produce a hard
   substance such as vulcanite

2. to treat (substances other than rubber) by a similar process in
   order to improve their properties


License
=======

GPLv3