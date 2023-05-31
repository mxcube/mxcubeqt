#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages


requirements_filename = 'requirements_mxcubecore.txt'

with open(requirements_filename) as f:
    content = f.readlines()
requirements = [x.strip() for x in content]
requirements = [x for x in requirements if not x.startswith('#')]

setup_requirements = []

tests_requirements = []

extras_requirements = {}

console_scripts = ['mxcube = mxcubeqt.__main__:run']

gui_scripts = []

entry_points = {
        'console_scripts': console_scripts,
        'gui_scripts': gui_scripts
    }

setup(
    name='mxcubeqt',
    # version='0.1.0',
    # author='The MXCuBE developers',
    # author_email='mxcube@mxcube.org',
    description='Qt front-end version for MXCuBE',
    long_description='Front-end version for MXCuBE based on Qt framework',
    url='http://github.com/mxcube/mxcubeqt',
    packages=find_packages(),
    package_dir={},
    include_package_data=True,
    package_data={'mxcubeqt': ['ui_files/*.ui',
                               'icons/*.png',
                               'examples/*'],
                  },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
    ],
    platforms='all',
    license='LGPL',
    entry_points=entry_points,
    install_requires=requirements,
    setup_requires=setup_requirements,
    tests_require=tests_requirements,
    extras_require=extras_requirements,
    python_requires='>=3.8',
   )
