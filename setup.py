#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages


requirements = ['setuptools']

setup_requirements = []

TESTING = any(x in sys.argv for x in ['test', 'pytest'])
if TESTING:
    setup_requirements += ['pytest-runner']

SPHINX = any(x in sys.argv for x in ['build_sphinx'])
if SPHINX:
    setup_requirements += ['sphinx', 'sphinx-argparse', 'sphinx_rtd_theme']

tests_requirements = []  # ['pytest', 'pytest-cov']

extras_requirements = {} # {
    # 'gui': ['PyQt4', 'taurus', 'taurus-pyqtgraph', 'sardana', 'matplotlib']
#}

console_scripts = ['mxcube = mxcubeqt:run']

gui_scripts = []

entry_points = {
        'console_scripts': console_scripts,
        'gui_scripts': gui_scripts
    }


setup(
    name='mxcubeqt',
    # The version is updated automatically with bumpversion
    version='0.0.1',
    #author='Jordi Andreu',
    #author_email='jandreu@cells.es',
    description='Qt front-end version for MXCuBE',
    long_description='Qt front-end version for MXCuBE',
    url='http://github.com/mxcube/mxcube',
    packages=find_packages(),
    package_dir={},
    include_package_data=True,
    package_data={'mxcubeqt': ['ui_files/*.ui',
                               'icons/*.png',
                               'examples/*'],
                  'mxcubecore': ['configuration/mockup/*.xml',
                                         'configuration/mockup/*.jpg',
                                         'configuration/mockup/qt/*.xml',
                                         'configuration/mockup/qt/*.yml']
                  },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
    ],
    platforms='all',
    license='GPL-3.0+',
    entry_points=entry_points,
    install_requires=requirements,
    setup_requires=setup_requirements,
    tests_require=tests_requirements,
    extras_require=extras_requirements,
    python_requires='>=2.7',
   )
