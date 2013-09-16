#-*- coding: utf-8 -*-
from setuptools import setup, find_packages
setup(
    name='testcmd',
    version='1',
    license='BSD',
    author='TakesxiSximada',
    author_email='takesxi.sximada@gmail.com',
    packages=find_packages(),
    entry_points = """\
    [console_scripts]
    testcmd = testcmd.command:main
    """
)
