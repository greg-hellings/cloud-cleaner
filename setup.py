#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='cloud-cleaner',
    version='0.1.0',
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
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
        'munch',
        'pytz'
    ],
    extras_require={
        ":python_version<'3.3'": [
            "py2-ipaddress"
        ]
    },
    entry_points={
        'console_scripts': [
            'cloud-clean=cloud_cleaner.bin.entrypoint:cloud_clean'
        ]
    }
)
