#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='pyzerigo',
      version='0.0.2',
      author='Louis Opter',
      install_requires=['restkit == 0.9.3'],
      package_dir = {'zerigo' : 'zerigo'},
      packages=['zerigo'],
     )
