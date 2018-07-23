#! /usr/bin/env python
# encoding: utf-8
"""
"""

from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals

__copyright__ = """
  * Copyright © 2016 - 2018 by Global Phasing Ltd. All rights reserved
  *
  * This software is proprietary to and embodies the confidential
  * technology of Global Phasing Limited (GPhL).
  *
  * Any possession or use (including but not limited to duplication, 
  * reproduction and dissemination) of this software (in either source or 
  * compiled form) is forbidden except where an agreement with GPhL that 
  * permits such possession or use is in force.
"""
__author__ = "rhfogh"
__date__ = "16/07/18"


import os
import sys
import itertools

_i = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _i not in sys.path:
    sys.path.insert(0, _i)
else:
    _i = None

# from . import stratcal_wrap
import stratcal_wrap

if _i:
    sys.path.remove(_i)
del _i

def analyse_data(data):
    """Analyse stratcal test data"""


    result = []

    for crystal, orientation, fp in data:

        state = None
        values = {'crystal':crystal}
        result.append(values)
        for ii,tag in enumerate(('euler_ang_1', 'euler_ang_2', 'euler_ang_3')):
            values[tag] = orientation[ii]

        for line in open(fp).readlines():

            if state is None:
                if 'Initial orientation in diffractometer system' in line:
                    state = 'init_angles'
                elif 'pg_symop' in line:
                    header = line.strip().split()
                elif 'Selected alignments' in line:
                    state = 'alignment'
                elif 'Reflections processing' in line:
                    state = 'final_angles'

            elif state == 'init_angles':
                ll = line.strip().split()
                if not ll:
                    pass
                elif ll[0] == '1':
                    values['init_ang_x'] = ll[1]
                elif ll[0] == '2':
                    values['init_ang_y'] = ll[1]
                elif ll[0] == '3':
                    values['init_ang_z'] = ll[1]
                    state = None

            elif state == 'final_angles':
                ll = line.strip().split()
                if not ll:
                    pass
                elif ll[0] == '1':
                    values['final_ang_x'] = ll[1]
                elif ll[0] == '2':
                    values['final_ang_y'] = ll[1]
                elif ll[0] == '3':
                    values['final_ang_z'] = ll[1]
                    state = None

            elif state == 'alignment':
                line = line.strip()
                if line:
                    ll = line.replace(', ', ',').split()
                    values.update(dict(zip(header, ll)))
                    state = None
    #
    return result


if __name__ == '__main__':

    # template input file
    fp_template = "/home/rhfogh/scratch/stratcal_test_201807/stratcal_id30b.in"
    crystal_dir = "/home/rhfogh/pycharm/MXCuBE-Qt_26r/ExampleFiles/HardwareObjects.xml/gphl_config/test_samples/"
    test_dir = "/home/rhfogh/scratch/stratcal_test_201807/20180723_4"
    executable = "/public/xtal/Server-nightly-alpha-bdg-linux64/autoPROC/bin/linux64/stratcal"

    # 3n0s	P21	monoclinic
    # 4k4k	P21212	orthorhombic	NEW
    # 4k61	I4		tetragonal
    # 4j8p	P41212	tetragonal
    # 5y6h	H3		trigonal	NEW
    # 4jrl		H32		trigonal
    # 4kh8	P65 	hexagonal	NEW
    # 4iej		P6122	hexagonal
    # 5g0f	I23		cubic (tetrahedral) NEW
    # 4KW2	F432	cubic	NEW
    # Further crystals: 4mxt (C2), thermolysin (P6122), germanagte (Ia-3d)
    #             '4iej', 'thermolysin', '4kw2','germanate', ]
    # crystals = ['3n0s', '4k4k', '4k61', '4j8p', '5y6h', '4jrl',
    #             '4kh8', '4iej', '5g0f', '4kw2', ]
    crystals = ['4k4k']

    # angles are in order phi, theta, omega,
    # where phi and theta are (+/-)the polar coiordinates of the rotation axis
    # in the crystal orthonormal system, and omega is the rotation
    # around the omega axis
    angles = [(4, 15, 22, 30, 45, 60, 105),
              (0, 20, 45, 55, 70, 90,),
              (0,)]
    # angles = [(30,),
    #           (45,),
    #           (0, 15, 22, 30, 45, 60, 105, 130, 180)]

    # Environment variables for test stup. Edit to change
    ENVS = {
        'OMP_STACKSIZE':'16M',
        'OMP_THREAD_LIMIT':'6',
        'OMP_NUM_THREADS':'6',
        'GPHL_STRATCAL_BINARY':executable,
        'BDG_home':'/public/xtal/Server-nightly-alpha-bdg-linux64/'
    }
    for key, val in ENVS.items():
        os.environ[key] = val

    stratcal_options = {
        'driver':6,
        'type-of-correction':2,
        'main-only':None
    }

    for fp in (fp_template, executable):
        print ('@~@~ path exists', os.path.exists(fp), fp)
    data = []

    # offset = (0.1, 0.1, 0.1)
    offset = ()
    for crystal in crystals:
        # for orientation in orientations:
        print ('@~@~ angles', list(itertools.product(*angles)))
        for orientation in itertools.product(*angles):
            if offset:
                orientation = tuple(x + offset[ii]
                                    for ii, x in enumerate(orientation))
            print ('@~@~ testing', crystal, orientation)
            fp_crystal = os.path.join(crystal_dir, crystal, 'crystal.nml')
            fp_log = stratcal_wrap.test_stratcal_wrap(crystal,
                                                      orientation,
                                                      fp_template=fp_template,
                                                      fp_crystal=fp_crystal,
                                                      test_dir=test_dir,
                                                      force=True,
                                                      # log_to_file=False,
                                                      **stratcal_options)
            if fp_log:
                data.append((crystal, orientation, fp_log))

    table = analyse_data(data)
    header = ['euler_ang_1', 'euler_ang_2', 'euler_ang_3',
              'init_ang_x', 'init_ang_y', 'init_ang_z',
              'final_ang_x', 'final_ang_y', 'final_ang_z',
              'Phi', 'Kappa', 'Omega',
              'compl', 'redun', 'error',
              ]
    print ('  '.join(header))
    for datum in table:
        print ('\t'.join(str(datum[tag]) for tag in header))

