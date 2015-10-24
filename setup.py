#!/usr/bin/env python

from distutils.core import setup

setup(
    name='LD Vulcanize',
    description='Self-Contained Library Paths',
    author='Volker Braun',
    author_email='vbraun.name@gmail.com',
    packages=['ld_vulcanize', 'ld_vulcanize.tool'],
    scripts=['bin/ld-vulcanize'],
    version='1.0',
    url='https://github.com/vbraun/ld-vulcanize',
)
