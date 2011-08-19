# -*- coding: utf-8 -*-
"""Sets sys.path for the library directories.

The purpose of this file is to have a single place to define extra paths.
This is convenient in case many entry points are used instead of a single
main.py.
"""
import os
import sys

# remove old django
for k in [k for k in sys.modules if k.startswith('django')]: 
    del sys.modules[k]

from google.appengine.dist import use_library
use_library('django', '1.2')

# add lib path
current_path = os.path.abspath(os.path.dirname(__file__))
lib_path = os.path.join(current_path, 'lib')

def set_path():
    # Add lib as primary libraries directory, with fallback to lib/dist
    # and optionally to lib/dist.zip, loaded using zipimport.
    if lib_path not in sys.path:
        sys.path[0:0] = [
            lib_path,
            os.path.join(lib_path, 'dist'),
        ]

set_path()



