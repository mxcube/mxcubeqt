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
import math

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
        space_group = None
        omega_projection_angle = None

        indx = 0
        for line in open(fp).readlines():

            if state is None:
                if '@~@~' in line:

                    if  'omega_projection_angle' in line:
                        omega_projection_angle = float(line.split()[2])

                elif 'Total CPU' in line:
                    values['time'] = float(line.split()[-1])

                elif 'Space group' in line:
                    space_group = line.split()[-1]

                elif 'Initial orientation in diffractometer system' in line:
                    state = 'init_angles'
                    indx += 1
                    values0 = {'crystal':crystal, 'indx':indx, 'time':'     ',
                               'omega_projection_angle':omega_projection_angle}
                    for ii,tag in enumerate(('euler_ang_1', 'euler_ang_2', 'euler_ang_3')):
                        values0[tag] = orientation[ii]

                elif 'pg_symop' in line:
                    header = line.strip().split()
                elif 'Selected alignments' in line:
                    values = values0.copy()
                    result.append(values)
                    state = 'alignment'
                elif 'Reflections processing' in line:
                    state = 'final_angles'

            elif state == 'init_angles':
                ll = line.strip().split()
                if not ll:
                    pass
                elif ll[0] == '1':
                    values0['init_ang_x'] = float(ll[1])
                elif ll[0] == '2':
                    values0['init_ang_y'] = float(ll[1])
                elif ll[0] == '3':
                    values0['init_ang_z'] = float(ll[1])
                    state = None

            elif state == 'final_angles':
                ll = line.strip().split()
                if not ll:
                    pass
                elif ll[0] == '1':
                    values['final_ang_x'] = float(ll[1])
                elif ll[0] == '2':
                    values['final_ang_y'] = float(ll[1])
                elif ll[0] == '3':
                    values['final_ang_z'] = float(ll[1])
                    if space_group in ('P2', 'P21', 'C2'):
                        theta = values['final_ang_y']
                        sign = -1 if values['final_ang_z'] <= 90 else 1
                    else:
                        theta = values['final_ang_z']
                        sign = 1 if values['final_ang_y'] <= 90  else -1
                    angx = math.radians(values['final_ang_x'])
                    angt = math.radians(theta)
                    print ('@~@~ angles', values['final_ang_x'], theta)
                    print ('@~@~', math.cos(angx)/math.sin(angt))
                    phi = sign * math.acos(min(1.0,math.cos(angx)/math.sin(angt)))

                    values ['final_theta'] = theta
                    values ['final_phi'] = math.degrees(phi)
                    state = None

            elif state == 'alignment':
                line = line.strip()
                if line:
                    for ii, ss in enumerate(line.replace(', ', ',').split()):
                        tag = header[ii]
                        try:
                            values[tag] = float(ss)
                        except ValueError:
                            values[tag] = ss
                    state = None
    #
    return result


def fform(xx):
    """Format xx to give nice output table"""
    if isinstance(xx, float):
        return '% 5.2f' % xx
    else:
        return str(xx)

if __name__ == '__main__':

    # template input file
    fp_template = "/home/rhfogh/scratch/stratcal_test_201807/stratcal_id30b.in"
    crystal_dir = "/home/rhfogh/pycharm/MXCuBE-Qt_26r/ExampleFiles/HardwareObjects.xml/gphl_config/test_samples/"
    test_dir = "/home/rhfogh/scratch/stratcal_test_201807/20180801_8"
    executable = "/public/xtal/Server-nightly-alpha-bdg-linux64/autoPROC/bin/linux64/stratcal"
    # executable = "//home/claus/tmp/stratcal-rf-20180802"

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
    crystals = ['3n0s', '4k4k', '4k61', '4j8p', '4jrl',
                '5y6h', '4kh8', '4iej', '5g0f', '4kw2', ]
    # crystals = ['4kw2']

    # angles are in order phi, theta, omega,
    # where phi and theta are (+/-)the polar coiordinates of the rotation axis
    # in the crystal orthonormal system, and omega is the rotation
    # around the omega axis
    angles1 = [(0,0,0), (0,10,0), (0, 90, 0)]
    angles2 = [(-45, 0, 30, 112),
              (20, 40, 55, 70, 95,),
              (0,)]
    # angles1 = [(0,0,0), (0,30,0), (0,45,0), (0,60,0), (0, 90, 0), (0,-30,0),
    #            (-30,90,0), (30,90,0), (45,90,0), (60,90,0), (90, 90, 0),
    #            ]
    # angles1 = [(0,0,0)]
    # angles2 = []

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
        'type-of-correction':1,
        'main-only':None,
        'selection_mode':4
    }

    for fp in (fp_template, executable):
        print ('@~@~ path exists', os.path.exists(fp), fp)
    data = []

    # offset = (0.1, 0.1, 0.1)
    offset = ()
    orientations = list(angles1)
    if angles2:
        orientations += list(itertools.product(*angles2))
    if offset:
        orientations = list(tuple(x + offset[ii] for ii, x in enumerate(tt))
                            for tt in orientations)
    print ('@~@~ angles', orientations)
    for crystal in crystals:
        for orientation in orientations:
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
    header = ['crystal', 'indx', 'euler_ang_1', 'euler_ang_2', 'euler_ang_3',
              'init_ang_x', 'init_ang_y', 'init_ang_z',
              'final_ang_x', 'final_ang_y', 'final_ang_z',
              'final_phi', 'final_theta', 'Phi', 'Kappa', 'Omega',
              'compl', 'redun', 'error',
              ]

    print ('  '.join(header))
    for datum in table:
        print ('\t'.join(fform(datum.get(tag, ' ')) for tag in header))
