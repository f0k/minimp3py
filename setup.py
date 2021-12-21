#!/usr/bin/env python3
# -*- coding: utf8 -*-
"""
Installation file for the minimp3py Python module.

You may want to set CFLAGS="-O3 -march=native" during installation to compile
with SSE if your CPU supports it.
"""

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension
import os

backend = Extension('minimp3py.backend',
                    sources=['minimp3py/backend.c'],
                    include_dirs=['minimp3'])

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()
setup(name='minimp3py',
      version='0.2.3',
      description='Python bindings to the minimp3 decoder',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Jan Schlüter',
      author_email='github@jan-schlueter.de',
      url='https://github.com/f0k/minimp3py',
      license='MIT',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
      ],
      keywords='minimp3 mp3 audio decoder',
      ext_modules=[backend],
      packages=['minimp3py'],
      extras_require={'test': ['pytest', 'numpy']},
      python_requires='>=3',
      )
