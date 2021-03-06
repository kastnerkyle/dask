#!/usr/bin/env python

from os.path import exists
from setuptools import setup
import dask

setup(name='dask',
      version=dask.__version__,
      description='Minimal task scheduling abstraction',
      url='http://github.com/ContinuumIO/dask/',
      maintainer='Matthew Rocklin',
      maintainer_email='mrocklin@gmail.com',
      license='BSD',
      keywords='task-scheduling parallelism',
      packages=['dask', 'dask.array', 'dask.bag', 'dask.store', 'dask.dataframe'],
      long_description=(open('README.rst').read() if exists('README.rst')
                        else ''),
      install_requires=(list(open('requirements.txt').read().strip().split('\n'))),
      zip_safe=False)


setup(name='pframe',
      version='0.1.0',
      description='Partitioned on-disk storage of DataFrames',
      url='http://github.com/ContinuumIO/dask/',
      maintainer='Matthew Rocklin',
      maintainer_email='mrocklin@gmail.com',
      license='BSD',
      keywords='pandas partitioning out-of-core',
      packages=['pframe'],
      long_description=(open('README.rst').read() if exists('README.rst')
                        else ''),
      install_requires=(list(open('pframe.requirements.txt').read().strip().split('\n'))),
      zip_safe=False)
