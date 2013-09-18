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

pkg = __import__('jumon')
setup(
    name=pkg.__name__,
    version=pkg.__version__,
    url='https://bitbucket.org/takesxi_sximada/jumon',
    download_url='https://bitbucket.org/takesxi_sximada/jumon',
    license='Apache License 2.0',
    author='TakesxiSximada',
    author_email='takesxi.sximada@gmail.com',
    description='The small framework for sub commands.',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apple Public Source License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    platforms='any',
    py_modules=['jumon'],
    include_package_data=True,
    install_requires=requires,
)
