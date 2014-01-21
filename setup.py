#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages


ROOT = os.path.dirname(os.path.abspath(__file__))
README_PATH = os.path.join(ROOT, 'README')

try:
    with open(README_PATH, 'rb') as fp:
        long_desc = fp.read()
except:
    long_desc = ''
    
requires = []

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Topic :: Software Development",
]


pkg = __import__('jumon')
setup(
    name=pkg.__name__,
    version=pkg.__version__,
    url='http://sximadaw3.web.fc2.com/work/jumon',
    download_url='https://bitbucket.org/takesxi_sximada/jumon',
    license='Apache License 2.0',
    author='TakesxiSximada',
    author_email='takesxi.sximada@gmail.com',
    description='The small framework for sub commands.',
    long_description=long_desc,
    zip_safe=False,
    classifiers=classifiers,
    platforms='any',
    py_modules=['jumon'],
    include_package_data=True,
    install_requires=requires,
)
