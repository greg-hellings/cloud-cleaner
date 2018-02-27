#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='cloud-cleaner',
    version='0.0.2',
    license='BSD',
    author='Gregory Hellings',
    author_email='greg.hellings@gmail.com',
    url='https://github.com/greg-hellings/cloud-cleaner',
    description='Utilities to clean up old OpenStack resources',
    packages=find_packages(exclude=('tests')),
    keywords=['cloud', 'openstack'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    install_requires=[
        'shade',
        'os-client-config',
        'munch'
    ],
    entry_points={
        'console_scripts': [
            'cloud-clean=cloud_cleaner.bin.entrypoint:cloud_clean'
        ]
    }
)
