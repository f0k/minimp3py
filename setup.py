#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
Installation file for the minimp3py Python module.

You may want to set CFLAGS="-O3 -march=native" during installation to compile
with SSE if your CPU supports it.
"""

try:
    from setuptools.core import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

backend = Extension('minimp3py.backend',
                    sources=['minimp3py/backend.c'],
                    include_dirs=['minimp3'])

setup(name='minimp3py',
      version='0.2.2',
      description='Python binding to the minimp3 decoder',
      author='Jan Schlüter',
      author_email='github@jan-schlueter.de',
      ext_modules=[backend],
      packages=['minimp3py'],
      )
