#! /usr/bin/env python
# encoding: utf-8
""" Wrapper file to make and collate multiple stratcal calls depending
on the space group of the crystal, for native data collection strategies

The file is a standalone plug-in replacement for stratcal,
and will produce .out2.def and .stdout files,
as well as stratcal output for individual runs
"""

from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals

import os
import sys
import subprocess
import f90nml
import math
import copy
import numpy as np
import mgen
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

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
__date__ = "11/07/18"

DEG2RAD = math.pi/180

def run_stratcal_wrap(input, logfile=None, output=None, main_only=None, selection_mode=None,
                      *args, **options):
    """Run stratcal wrapper, adapting options and dispatching to correct runner

    args is currently not used

    option are passed to stratcal executable as command line options
    """
    print ('@~@~ run_stratcal_wrap', input, output, main_only, selection_mode,
           sorted(tt for tt in options.items()))

    options['input'] = input

    if output is None:
        output = os.path.splitext(input)[0] + '.out'
    options['output'] = output

    if main_only is not None:
        options['main-only'] = main_only
    if selection_mode is not None:
        options['selection-mode'] = selection_mode

    if options.get('driver') == 6:
        # Native data collection - determine strategy and run with driver 5
        options['driver'] = 5
        run_stratcal_native(logfile=logfile, **options)

    else:
        running_process = run_stratcal(logfile=logfile, **options)
        running_process.wait()

def get_laue_group(sg_name):
    """Get Laue gropup from space-group"""

    try:
        from queue_model_enumerables_v1 import SPACEGROUP_DATA, SPACEGROUP_MAP
    except ImportError:
        from collections import namedtuple
        SpaceGroupInfo = namedtuple('SpaceGroupInfo',
                                    ('number', 'name', 'point_group', 'laue_group'))
        # Complete list of 230 crystallographic space groups
        # Direct source: GPhL stratcal source code. RHFogh.
        SPACEGROUP_DATA = [
            SpaceGroupInfo(0, '', '', ''),
            SpaceGroupInfo(1, 'P1', '1', '-1'),
            SpaceGroupInfo(2, 'P-1', '-1', '-1'),
            SpaceGroupInfo(3, 'P2', '2', '2/m'),
            SpaceGroupInfo(4, 'P21', '2', '2/m'),
            SpaceGroupInfo(5, 'C2', '2', '2/m'),
            SpaceGroupInfo(6, 'Pm', 'm', '2/m'),
            SpaceGroupInfo(7, 'Pc', 'm', '2/m'),
            SpaceGroupInfo(8, 'Cm', 'm', '2/m'),
            SpaceGroupInfo(9, 'Cc', 'm', '2/m'),
            SpaceGroupInfo(10, 'P2/m', '2/m', '2/m'),
            SpaceGroupInfo(11, 'P21/m', '2/m', '2/m'),
            SpaceGroupInfo(12, 'C2/m', '2/m', '2/m'),
            SpaceGroupInfo(13, 'P2/c', '2/m', '2/m'),
            SpaceGroupInfo(14, 'P21/c', '2/m', '2/m'),
            SpaceGroupInfo(15, 'C2/c', '2/m', '2/m'),
            SpaceGroupInfo(16, 'P222', '222', 'mmm'),
            SpaceGroupInfo(17, 'P2221', '222', 'mmm'),
            SpaceGroupInfo(18, 'P21212', '222', 'mmm'),
            SpaceGroupInfo(19, 'P212121', '222', 'mmm'),
            SpaceGroupInfo(20, 'C2221', '222', 'mmm'),
            SpaceGroupInfo(21, 'C222', '222', 'mmm'),
            SpaceGroupInfo(22, 'F222', '222', 'mmm'),
            SpaceGroupInfo(23, 'I222', '222', 'mmm'),
            SpaceGroupInfo(24, 'I212121', '222', 'mmm'),
            SpaceGroupInfo(25, 'Pmm2', 'mm2', 'mmm'),
            SpaceGroupInfo(26, 'Pmc21', 'mm2', 'mmm'),
            SpaceGroupInfo(27, 'Pcc2', 'mm2', 'mmm'),
            SpaceGroupInfo(28, 'Pma2', 'mm2', 'mmm'),
            SpaceGroupInfo(29, 'Pca21', 'mm2', 'mmm'),
            SpaceGroupInfo(30, 'Pnc2', 'mm2', 'mmm'),
            SpaceGroupInfo(31, 'Pmn21', 'mm2', 'mmm'),
            SpaceGroupInfo(32, 'Pba2', 'mm2', 'mmm'),
            SpaceGroupInfo(33, 'Pna21', 'mm2', 'mmm'),
            SpaceGroupInfo(34, 'Pnn2', 'mm2', 'mmm'),
            SpaceGroupInfo(35, 'Cmm2', 'mm2', 'mmm'),
            SpaceGroupInfo(36, 'Cmc21', 'mm2', 'mmm'),
            SpaceGroupInfo(37, 'Ccc2', 'mm2', 'mmm'),
            SpaceGroupInfo(38, 'Amm2', 'mm2', 'mmm'),
            SpaceGroupInfo(39, 'Abm2', 'mm2', 'mmm'),
            SpaceGroupInfo(40, 'Ama2', 'mm2', 'mmm'),
            SpaceGroupInfo(41, 'Aba2', 'mm2', 'mmm'),
            SpaceGroupInfo(42, 'Fmm2', 'mm2', 'mmm'),
            SpaceGroupInfo(43, 'Fdd2', 'mm2', 'mmm'),
            SpaceGroupInfo(44, 'Imm2', 'mm2', 'mmm'),
            SpaceGroupInfo(45, 'Iba2', 'mm2', 'mmm'),
            SpaceGroupInfo(46, 'Ima2', 'mm2', 'mmm'),
            SpaceGroupInfo(47, 'Pmmm', 'mmm', 'mmm'),
            SpaceGroupInfo(48, 'Pnnn', 'mmm', 'mmm'),
            SpaceGroupInfo(49, 'Pccm', 'mmm', 'mmm'),
            SpaceGroupInfo(50, 'Pban', 'mmm', 'mmm'),
            SpaceGroupInfo(51, 'Pmma', 'mmm', 'mmm'),
            SpaceGroupInfo(52, 'Pnna', 'mmm', 'mmm'),
            SpaceGroupInfo(53, 'Pmna', 'mmm', 'mmm'),
            SpaceGroupInfo(54, 'Pcca', 'mmm', 'mmm'),
            SpaceGroupInfo(55, 'Pbam', 'mmm', 'mmm'),
            SpaceGroupInfo(56, 'Pccn', 'mmm', 'mmm'),
            SpaceGroupInfo(57, 'Pbcm', 'mmm', 'mmm'),
            SpaceGroupInfo(58, 'Pnnm', 'mmm', 'mmm'),
            SpaceGroupInfo(59, 'Pmmn', 'mmm', 'mmm'),
            SpaceGroupInfo(60, 'Pbcn', 'mmm', 'mmm'),
            SpaceGroupInfo(61, 'Pbca', 'mmm', 'mmm'),
            SpaceGroupInfo(62, 'Pnma', 'mmm', 'mmm'),
            SpaceGroupInfo(63, 'Cmcm', 'mmm', 'mmm'),
            SpaceGroupInfo(64, 'Cmca', 'mmm', 'mmm'),
            SpaceGroupInfo(65, 'Cmmm', 'mmm', 'mmm'),
            SpaceGroupInfo(66, 'Cccm', 'mmm', 'mmm'),
            SpaceGroupInfo(67, 'Cmma', 'mmm', 'mmm'),
            SpaceGroupInfo(68, 'Ccca', 'mmm', 'mmm'),
            SpaceGroupInfo(69, 'Fmmm', 'mmm', 'mmm'),
            SpaceGroupInfo(70, 'Fddd', 'mmm', 'mmm'),
            SpaceGroupInfo(71, 'Immm', 'mmm', 'mmm'),
            SpaceGroupInfo(72, 'Ibam', 'mmm', 'mmm'),
            SpaceGroupInfo(73, 'Ibca', 'mmm', 'mmm'),
            SpaceGroupInfo(74, 'Imma', 'mmm', 'mmm'),
            SpaceGroupInfo(75, 'P4', '4', '4/m'),
            SpaceGroupInfo(76, 'P41', '4', '4/m'),
            SpaceGroupInfo(77, 'P42', '4', '4/m'),
            SpaceGroupInfo(78, 'P43', '4', '4/m'),
            SpaceGroupInfo(79, 'I4', '4', '4/m'),
            SpaceGroupInfo(80, 'I41', '4', '4/m'),
            SpaceGroupInfo(81, 'P-4', '-4', '4/m'),
            SpaceGroupInfo(82, 'I-4', '-4', '4/m'),
            SpaceGroupInfo(83, 'P4/m', '4/m', '4/m'),
            SpaceGroupInfo(84, 'P42/m', '4/m', '4/m'),
            SpaceGroupInfo(85, 'P4/n', '4/m', '4/m'),
            SpaceGroupInfo(86, 'P42/n', '4/m', '4/m'),
            SpaceGroupInfo(87, 'I4/m', '4/m', '4/m'),
            SpaceGroupInfo(88, 'I41/a', '4/m', '4/m'),
            SpaceGroupInfo(89, 'P422', '422', '4/mmm'),
            SpaceGroupInfo(90, 'P4212', '422', '4/mmm'),
            SpaceGroupInfo(91, 'P4122', '422', '4/mmm'),
            SpaceGroupInfo(92, 'P41212', '422', '4/mmm'),
            SpaceGroupInfo(93, 'P4222', '422', '4/mmm'),
            SpaceGroupInfo(94, 'P42212', '422', '4/mmm'),
            SpaceGroupInfo(95, 'P4322', '422', '4/mmm'),
            SpaceGroupInfo(96, 'P43212', '422', '4/mmm'),
            SpaceGroupInfo(97, 'I422', '422', '4/mmm'),
            SpaceGroupInfo(98, 'I4122', '422', '4/mmm'),
            SpaceGroupInfo(99, 'P4mm', '4mm', '4/mmm'),
            SpaceGroupInfo(100, 'P4bm', '4mm', '4/mmm'),
            SpaceGroupInfo(101, 'P42cm', '4mm', '4/mmm'),
            SpaceGroupInfo(102, 'P42nm', '4mm', '4/mmm'),
            SpaceGroupInfo(103, 'P4cc', '4mm', '4/mmm'),
            SpaceGroupInfo(104, 'P4nc', '4mm', '4/mmm'),
            SpaceGroupInfo(105, 'P42mc', '4mm', '4/mmm'),
            SpaceGroupInfo(106, 'P42bc', '4mm', '4/mmm'),
            SpaceGroupInfo(107, 'I4mm', '4mm', '4/mmm'),
            SpaceGroupInfo(108, 'I4cm', '4mm', '4/mmm'),
            SpaceGroupInfo(109, 'I41md', '4mm', '4/mmm'),
            SpaceGroupInfo(110, 'I41cd', '4mm', '4/mmm'),
            SpaceGroupInfo(111, 'P-42m', '-42m', '4/mmm'),
            SpaceGroupInfo(112, 'P-42c', '-42m', '4/mmm'),
            SpaceGroupInfo(113, 'P-421m', '-42m', '4/mmm'),
            SpaceGroupInfo(114, 'P-421c', '-42m', '4/mmm'),
            SpaceGroupInfo(115, 'P-4m2', '-4m2', '4/mmm'),
            SpaceGroupInfo(116, 'P-4c2', '-4m2', '4/mmm'),
            SpaceGroupInfo(117, 'P-4b2', '-4m2', '4/mmm'),
            SpaceGroupInfo(118, 'P-4n2', '-4m2', '4/mmm'),
            SpaceGroupInfo(119, 'I-4m2', '-4m2', '4/mmm'),
            SpaceGroupInfo(120, 'I-4c2', '-4m2', '4/mmm'),
            SpaceGroupInfo(121, 'I-42m', '-42m', '4/mmm'),
            SpaceGroupInfo(122, 'I-42d', '-42m', '4/mmm'),
            SpaceGroupInfo(123, 'P4/mmm', '4/mmm', '4/mmm'),
            SpaceGroupInfo(124, 'P4/mcc', '4/mmm', '4/mmm'),
            SpaceGroupInfo(125, 'P4/nbm', '4/mmm', '4/mmm'),
            SpaceGroupInfo(126, 'P4/nnc', '4/mmm', '4/mmm'),
            SpaceGroupInfo(127, 'P4/mbm', '4/mmm', '4/mmm'),
            SpaceGroupInfo(128, 'P4/mnc', '4/mmm', '4/mmm'),
            SpaceGroupInfo(129, 'P4/nmm', '4/mmm', '4/mmm'),
            SpaceGroupInfo(130, 'P4/ncc', '4/mmm', '4/mmm'),
            SpaceGroupInfo(131, 'P42/mmc', '4/mmm', '4/mmm'),
            SpaceGroupInfo(132, 'P42/mcm', '4/mmm', '4/mmm'),
            SpaceGroupInfo(133, 'P42/nbc', '4/mmm', '4/mmm'),
            SpaceGroupInfo(134, 'P42/nnm', '4/mmm', '4/mmm'),
            SpaceGroupInfo(135, 'P42/mbc', '4/mmm', '4/mmm'),
            SpaceGroupInfo(136, 'P42/mnm', '4/mmm', '4/mmm'),
            SpaceGroupInfo(137, 'P42/nmc', '4/mmm', '4/mmm'),
            SpaceGroupInfo(138, 'P42/ncm', '4/mmm', '4/mmm'),
            SpaceGroupInfo(139, 'I4/mmm', '4/mmm', '4/mmm'),
            SpaceGroupInfo(140, 'I4/mcm', '4/mmm', '4/mmm'),
            SpaceGroupInfo(141, 'I41/amd', '4/mmm', '4/mmm'),
            SpaceGroupInfo(142, 'I41/acd', '4/mmm', '4/mmm'),
            SpaceGroupInfo(143, 'P3', '3', '-3'),
            SpaceGroupInfo(144, 'P31', '3', '-3'),
            SpaceGroupInfo(145, 'P32', '3', '-3'),
            SpaceGroupInfo(146, 'R3', '3', '-3'),
            SpaceGroupInfo(147, 'P-3', '-3', '-3'),
            SpaceGroupInfo(148, 'R-3', '-3', '-3'),
            SpaceGroupInfo(149, 'P312', '312', '-3m'),
            SpaceGroupInfo(150, 'P321', '321', '-3m'),
            SpaceGroupInfo(151, 'P3112', '312', '-3m'),
            SpaceGroupInfo(152, 'P3121', '321', '-3m'),
            SpaceGroupInfo(153, 'P3212', '312', '-3m'),
            SpaceGroupInfo(154, 'P3221', '321', '-3m'),
            SpaceGroupInfo(155, 'R32', '32', '-3m'),
            SpaceGroupInfo(156, 'P3m1', '3m1', '-3m'),
            SpaceGroupInfo(157, 'P31m', '31m', '-3m'),
            SpaceGroupInfo(158, 'P3c1', '3m1', '-3m'),
            SpaceGroupInfo(159, 'P31c', '31m', '-3m'),
            SpaceGroupInfo(160, 'R3m', '3m', '-3m'),
            SpaceGroupInfo(161, 'R3c', '3m', '-3m'),
            SpaceGroupInfo(162, 'P-31m', '-31m', '-3m'),
            SpaceGroupInfo(163, 'P-31c', '-31m', '-3m'),
            SpaceGroupInfo(164, 'P-3m1', '-3m1', '-3m'),
            SpaceGroupInfo(165, 'P-3c1', '-3m1', '-3m'),
            SpaceGroupInfo(166, 'R-3m', '-3m', '-3m'),
            SpaceGroupInfo(167, 'R-3c', '-3m', '-3m'),
            SpaceGroupInfo(168, 'P6', '6', '6/m'),
            SpaceGroupInfo(169, 'P61', '6', '6/m'),
            SpaceGroupInfo(170, 'P65', '6', '6/m'),
            SpaceGroupInfo(171, 'P62', '6', '6/m'),
            SpaceGroupInfo(172, 'P64', '6', '6/m'),
            SpaceGroupInfo(173, 'P63', '6', '6/m'),
            SpaceGroupInfo(174, 'P-6', '-6', '6/m'),
            SpaceGroupInfo(175, 'P6/m', '6/m', '6/m'),
            SpaceGroupInfo(176, 'P63/m', '6/m', '6/m'),
            SpaceGroupInfo(177, 'P622', '622', '6/mmm'),
            SpaceGroupInfo(178, 'P6122', '622', '6/mmm'),
            SpaceGroupInfo(179, 'P6522', '622', '6/mmm'),
            SpaceGroupInfo(180, 'P6222', '622', '6/mmm'),
            SpaceGroupInfo(181, 'P6422', '622', '6/mmm'),
            SpaceGroupInfo(182, 'P6322', '622', '6/mmm'),
            SpaceGroupInfo(183, 'P6mm', '6mm', '6/mmm'),
            SpaceGroupInfo(184, 'P6cc', '6mm', '6/mmm'),
            SpaceGroupInfo(185, 'P63cm', '6mm', '6/mmm'),
            SpaceGroupInfo(186, 'P63mc', '6mm', '6/mmm'),
            SpaceGroupInfo(187, 'P-6m2', '-6m2', '6/mmm'),
            SpaceGroupInfo(188, 'P-6c2', '-6m2', '6/mmm'),
            SpaceGroupInfo(189, 'P-62m', '-62m', '6/mmm'),
            SpaceGroupInfo(190, 'P-62c', '-62m', '6/mmm'),
            SpaceGroupInfo(191, 'P6/mmm', '6/mmm', '6/mmm'),
            SpaceGroupInfo(192, 'P6/mcc', '6/mmm', '6/mmm'),
            SpaceGroupInfo(193, 'P63/mcm', '6/mmm', '6/mmm'),
            SpaceGroupInfo(194, 'P63/mmc', '6/mmm', '6/mmm'),
            SpaceGroupInfo(195, 'P23', '23', 'm-3'),
            SpaceGroupInfo(196, 'F23', '23', 'm-3'),
            SpaceGroupInfo(197, 'I23', '23', 'm-3'),
            SpaceGroupInfo(198, 'P213', '23', 'm-3'),
            SpaceGroupInfo(199, 'I213', '23', 'm-3'),
            SpaceGroupInfo(200, 'Pm-3', 'm-3', 'm-3'),
            SpaceGroupInfo(201, 'Pn-3', 'm-3', 'm-3'),
            SpaceGroupInfo(202, 'Fm-3', 'm-3', 'm-3'),
            SpaceGroupInfo(203, 'Fd-3', 'm-3', 'm-3'),
            SpaceGroupInfo(204, 'Im-3', 'm-3', 'm-3'),
            SpaceGroupInfo(205, 'Pa-3', 'm-3', 'm-3'),
            SpaceGroupInfo(206, 'Ia-3', 'm-3', 'm-3'),
            SpaceGroupInfo(207, 'P432', '432', 'm-3m'),
            SpaceGroupInfo(208, 'P4232', '432', 'm-3m'),
            SpaceGroupInfo(209, 'F432', '432', 'm-3m'),
            SpaceGroupInfo(210, 'F4132', '432', 'm-3m'),
            SpaceGroupInfo(211, 'I432', '432', 'm-3m'),
            SpaceGroupInfo(212, 'P4332', '432', 'm-3m'),
            SpaceGroupInfo(213, 'P4132', '432', 'm-3m'),
            SpaceGroupInfo(214, 'I4132', '432', 'm-3m'),
            SpaceGroupInfo(215, 'P-43m', '-43m', 'm-3m'),
            SpaceGroupInfo(216, 'F-43m', '-43m', 'm-3m'),
            SpaceGroupInfo(217, 'I-43m', '-43m', 'm-3m'),
            SpaceGroupInfo(218, 'P-43n', '-43m', 'm-3m'),
            SpaceGroupInfo(219, 'F-43c', '-43m', 'm-3m'),
            SpaceGroupInfo(220, 'I-43d', '-43m', 'm-3m'),
            SpaceGroupInfo(221, 'Pm-3m', 'm-3m', 'm-3m'),
            SpaceGroupInfo(222, 'Pn-3n', 'm-3m', 'm-3m'),
            SpaceGroupInfo(223, 'Pm-3n', 'm-3m', 'm-3m'),
            SpaceGroupInfo(224, 'Pn-3m', 'm-3m', 'm-3m'),
            SpaceGroupInfo(225, 'Fm-3m', 'm-3m', 'm-3m'),
            SpaceGroupInfo(226, 'Fm-3c', 'm-3m', 'm-3m'),
            SpaceGroupInfo(227, 'Fd-3m', 'm-3m', 'm-3m'),
            SpaceGroupInfo(228, 'Fd-3c', 'm-3m', 'm-3m'),
            SpaceGroupInfo(229, 'Im-3m', 'm-3m', 'm-3m'),
            SpaceGroupInfo(230, 'Ia-3d', 'm-3m', 'm-3m')
        ]
        SPACEGROUP_MAP = OrderedDict((info.name, info) for info in SPACEGROUP_DATA)


    if sg_name.isdigit():
        sg_info = SPACEGROUP_DATA[int(sg_name)]
    else:
        sg_info = SPACEGROUP_MAP[sg_name]
    return sg_info.laue_group



def run_stratcal_native(logfile=None, **options):
    """Run stratcal for native phasing (mode 6)"""
    print('@~@~ run_stratcal_native', sorted(tt for tt in options.items()))
    fp_in = options.get('input')
    input_data_exch = f90nml.read(fp_in)
    input_data_org = stratcal_exch2org(input_data_exch)

    # NB assumes only one crystal
    crystal_data = input_data_exch['crystal_list']
    sg_name = crystal_data['sg_name'].strip()
    laue_group = get_laue_group(sg_name)

    crystal_matrix = [
        crystal_data['cell_a_axis'],
        crystal_data['cell_b_axis'],
        crystal_data['cell_c_axis'],
    ]
    mm = []
    # transform to unit vectors
    for ll in crystal_matrix:
        length = math.sqrt(sum(x*x for x in ll))
        mm.append(list(x/length for x in ll))
    # transform to orthonormal coordinate system
    if laue_group == '-1':
        mm[2] = np.cross(mm[0], mm[1])
        mm[1] = np.cross(mm[2], mm[0])
    elif laue_group == '2/m':
        mm[2] = np.cross(mm[0], mm[1])
    else:
        mm[1] = np.cross(mm[2], mm[0])
    crystal_unit_np = np.array(mm)


    # NB assumes omega scan axis
    scan_axis = input_data_exch['stratcal_instrument_list']['omega_axis']

    # orthog_component is a unit vector orthogonal to the symmetry axis
    # and in the same plane as the symmetry and rotation axes.
    # symm_projection is the signed length of the rotation axis component
    # along the symmetry axis
    # These two values are used below to determine crystal alignments
    if  laue_group == '2/m':
        # Index of symetry axis
        symm_axis_index = 1
    else:
        symm_axis_index = 2
    cr_scan_axis_np = crystal_unit_np.dot(scan_axis)
    symm_projection = cr_scan_axis_np[symm_axis_index]
    orthog_component = list(cr_scan_axis_np / math.sqrt(1 - symm_projection ** 2))
    orthog_component[symm_axis_index] = 0

    print ('@~@~ crystal', sg_name, laue_group, '\n', crystal_unit_np)
    print('@~@~ axis', scan_axis, cr_scan_axis_np, symm_projection, orthog_component)

    if laue_group == '-1':
        # Triclinic, nothing doing. Pass on to default stratcal
        running_process = run_stratcal(**options)
        running_process.wait()
        return

    elif laue_group == '2/m':
        # Monoclinic
        # Two directions, theta=54.7deg; phi +/-45 deg away from symmetry axis
        ll = list(orthog_component)
        ll[symm_axis_index] = math.copysign(math.tan(35.3*DEG2RAD), symm_projection)
        orientation = tuple(mgen.rotation_around_axis(
            crystal_unit_np[symm_axis_index], math.pi/4
        ).dot(ll))
        add_crystal_orientation(input_data_org, orientation)
        orientation = tuple(mgen.rotation_around_axis(
            crystal_unit_np[symm_axis_index], -math.pi/4
        ).dot(ll))
        add_crystal_orientation(input_data_org, orientation)

    elif laue_group == 'mmm':
        # Orthorhombic
        # Along a body diagonal - selecting diagonal closest to the rotation axis
        orientation = tuple(math.copysign(1,x) for x in cr_scan_axis_np)
        add_crystal_orientation(input_data_org, orientation)

    elif laue_group == '4/m':
        # 'C4'
        # One directions, theta=54.7deg
        ll = list(orthog_component)
        ll[symm_axis_index] = math.copysign(math.tan(35.3*DEG2RAD), symm_projection)
        add_crystal_orientation(input_data_org, tuple(ll))

    elif laue_group == '4/mmm':
        # 422
        # theta=67.5, 22.5 deg from the plane of a twofold axis
        ll = [1, 0, 0]
        ll[symm_axis_index] = math.tan(35.3*DEG2RAD)
        orientation = tuple(mgen.rotation_around_axis(
            crystal_unit_np[symm_axis_index], math.pi/8
        ).dot(ll))
        orientation = tuple(math.copysign(1,x) for x in orientation)
        # NB this gives alignment in correct quadrant but not necessarily closest to axis
        # TODO
        add_crystal_orientation(input_data_org, orientation)

    elif laue_group == '-3':
        # 'C3'
        # Two directions ca. 30deg and 40 deg above the plane, 60deg apart
        ll = list(orthog_component)
        ll[symm_axis_index] = math.copysign(math.tan(math.pi/6),
                                            symm_projection)
        orientation = tuple(mgen.rotation_around_axis(
            crystal_unit_np[symm_axis_index], math.pi/6
        ).dot(ll))
        add_crystal_orientation(input_data_org, orientation)
        ll[symm_axis_index] = math.copysign(math.tan(math.pi/4.5),
                                                symm_projection)
        orientation = tuple(mgen.rotation_around_axis(
            crystal_unit_np[symm_axis_index], -math.pi/6
        ).dot(ll))
        add_crystal_orientation(input_data_org, orientation)

    elif laue_group == '-3m':
        # '32'
        # One direction, theta=60deg, phi 30 deg from a twofold axis
        # One direction 30 deg from the plane of  a twofold axis and 30 deg above the plane
        ll = list(orthog_component)
        ll[symm_axis_index] = math.copysign(math.tan(math.pi/6),
                                            symm_projection)
        orientation = tuple(mgen.rotation_around_axis(
            crystal_unit_np[symm_axis_index], math.pi/6
        ).dot(ll))
        add_crystal_orientation(input_data_org, orientation)

    elif laue_group == '6/m':
        # 'C6'
        # One directions, theta=60deg
        ll = list(orthog_component)
        ll[symm_axis_index] = math.copysign(math.tan(math.pi/6),
                                            symm_projection)
        add_crystal_orientation(input_data_org, tuple(ll))

    elif laue_group == '6/mmm':
        # '622'
        # theta=70, 15 deg from the plane of a twofold axis
        ll = [1, 0, 0]
        ll[symm_axis_index] = math.tan(math.pi/9)
        orientation = tuple(mgen.rotation_around_axis(
            crystal_unit_np[symm_axis_index], math.pi/12
        ).dot(ll))
        add_crystal_orientation(input_data_org, orientation)

    elif laue_group == 'm-3':
        # '23'
        # CA. 1, 0.3, 0.3 (on diagonal cross of a face)
        orientation = (1, 0.3, 0.3)
        # Put in same quadrant as rotation axis
        orientation = tuple(math.copysign(orientation[ii], cr_scan_axis_np[ii]) for ii in range(3))
        add_crystal_orientation(input_data_org, orientation)

    elif laue_group == 'm-3m':
        # '432'
        # Ca, 1.0, 0.2, 0.4
        orientation = (1, 0.2, 0.4)
        # Put in same quadrant as rotation axis
        orientation = tuple(math.copysign(orientation[ii], cr_scan_axis_np[ii]) for ii in range(3))
        add_crystal_orientation(input_data_org, orientation)

    else:
        # sg_name must be empty string
        raise ValueError("Illegal value (empty string) for SG_NAME")

    # Add orient list count
    n_orients = len(input_data_org['orient_list'])
    input_data_org['setup_list']['n_orients'] = n_orients

    # Move aside old input and save new input in input_data_org['orient_list'])ts place
    tt = os.path.splitext(fp_in)
    fp_in_backup = '_wrap'.join(tt)
    os.rename(fp_in, fp_in_backup)
    f90nml.write(input_data_org, fp_in)

    # Run stratcal
    running_process = run_stratcal(logfile=logfile, **options)
    running_process.wait()
    return

def stratcal_exch2org(exch_data):
    """Convert exchange format stratcal input data to original format"""

    indata = copy.deepcopy(exch_data)

    result = f90nml.Namelist()
    result['setup_list'] = setup_list = f90nml.Namelist()

    for tag, val in indata.pop('crystal_list').items():
        if tag != 'id':
            setup_list[tag] = val

    # Assuming that the first beam_setting is the default, and later ones are specific
    beam_setting_lists = indata.pop('beam_setting_list')
    setup_list['lambda_def'] = beam_setting_lists[0]['lambda']

    # The original format has different names here
    renames = {
        'trans_1_axis':'trans_x_axis',
        'trans_2_axis':'trans_y_axis',
        'trans_3_axis':'trans_z_axis',
    }
    for tag, val in indata.pop('stratcal_instrument_list').items():
        if tag != 'id':
            setup_list[renames.get(tag, tag)] = val

    for tag, val in indata.pop('detector_list').items():
        if tag != 'id':
            setup_list[tag] = val

    dd = indata.pop('detector_setting_list')
    setup_list['det_coord_def'] = dd['det_coord']

    for tag, val in indata.pop('beamstop_setting_list').items():
        # Assumes a single beamstop-list
        if tag != 'id':
            setup_list[tag] = val

    segment_lists = indata.pop('segment_list')
    setup_list['n_segments'] = len(segment_lists)

    result['segment_list'] = segment_lists
    #
    return result


def add_crystal_orientation(data_dict, orientation):
    """Add an orient_list record using orientation in reciprocal-space fractional crystal coordinates"""

    print('@~@~ add_crystal_orientation', orientation)

    setup_list = data_dict['setup_list']

    orient_list = data_dict.get('orient_list')
    if not orient_list:
        orient_list = data_dict['orient_list'] = []
    orient = f90nml.Namelist()
    orient_list.append(orient)

    # Parameters identical to default omitted, I assume they will be filled in.
    orient['crys_vec_mode'] = [2, 1]    # orthonormal space
    orient['lab_vec_mode'] = 1          # Main orientation
    orient['crys_vec_1'] = list(orientation) # Orient this
    orient['crys_vec_2'] = [1, 0, 0]    # X axis - one vector we will never align on
    orient['lab_vec_1'] = [0, 0, 0]    # dummy - autoset for mode 'main'
    orient['lab_vec_2'] = [0, 0, 0]    # dummy - autoset for mode 'main'
    orient['lambda'] = setup_list['lambda_def']
    orient['res_limit'] = setup_list['res_limit_def']
    orient['det_coord'] = setup_list['det_coord_def']
    orient['mu_air'] = -1    # dummy
    orient['mu_sensor'] = -1    # dummy
    orient['two_theta_deg'] = 0    # dummy
    orient['exposure'] = 1    # dummy
    orient['trans_xyz'] = [0, 0, 0]    # dummy
    # # Gives problems, reads as uioncode, which FOPRTRAN cannot read
    # orient['name_template'] = "data/sweep%s_????.cbf"  # dummy, not used
    orient['step_deg'] = 1              # 1 degree steps
    orient['n_frames'] = 360            # 360 of them
    orient['image_no'] = 1              # 360 of them

def run_stratcal(logfile=None, **options):
    """Call stratcal binary using command line options 'options'"""
    print ('@~@~ run_stratcal', sorted(tt for tt in options.items()))
    envs = os.environ
    cmd_list = [envs['GPHL_STRATCAL_BINARY']]
    for tag, val in sorted(options.items()):
        cmd_list.append('--' + tag)
        if val not in (None, ''):
            cmd_list.append(str(val))
    print ('@~@~ running stratcal', cmd_list)
    if isinstance(logfile, str):
        fp_log = open(logfile, 'w')
    else:
        fp_log = logfile
        # Flush the file, to make sure stratcal output (on stderr) is not mixed
        if fp_log:
            # Could be None
            fp_log.flush()
            os.fsync(fp_log.fileno())
    try:
        result = subprocess.Popen(cmd_list, env=envs, stdout=fp_log,
                                  stderr=fp_log)
    finally:
        if isinstance(logfile, str):
            fp_log.flush()
            os.fsync(fp_log.fileno())
            fp_log.close()
    #
    return result

def get_std_crystal_axes(crystal_data, omega_name='Z'):
    """get (cell_a_axis, cell_b_axis, cell_c_axis) in unrotated position
    from a read-in crystal_list dictionary (with lower case tags)

    if omega_axis is given will rotate crystal so that the main symmetry axis
    (the Y axis for monoclinic crystals, the Z axis otherwise)
    is rotated onto the omega axis

    if adjust_monoclinic will put the monoclinic symmetry axis on Z instead of Y"""
    sizes = crystal_data.get('cell_dim')
    angles = crystal_data.get('cell_ang_deg')
    axes = []
    for tag in ('cell_a_axis', 'cell_b_axis', 'cell_c_axis'):
        ll = crystal_data.get(tag)
        if ll:
            axes.append(ll)
        else:
            break
    else:
        if not sizes:
            sizes = list((math.sqrt(sum(x*x for x in ll))) for ll in axes)
    a,b,c = sizes

    print ('@~@~ sizes, angles, axes', sizes, angles, axes)

    laue_group = get_laue_group(crystal_data['sg_name'])
    print ('@~@~', sizes, angles, axes)
    # Using canonical angles avoids rounding off errors by calculating
    if laue_group in ('mmm', '4/m', '4/mmm', 'm-3', 'm-3m'):
        # orthogonal
        newaxes = (
            (a, 0, 0),
            (0, b, 0),
            (0, 0, c)
        )
    elif laue_group in ('-3', '-3m', '6/m', '6/mmm'):
        # hexagonal
        newaxes = (
            (a, 0, 0),
            (0, math.cos(math.pi*2/3)*b, -b/2),
            (0, 0, c)
        )
    elif laue_group == '2/m':
        # monoclinic
        if angles:
            beta = angles[1]
        else:
            dotproduct = sum(axes[0][kk] * axes[2][kk]
                             for kk in range(3))
            beta = math.acos(dotproduct/(a * c))
        newaxes = (
            (a, 0, 0),
            (0, b, 0),
            (c*math.cos(beta), 0, c*math.sin(beta))
        )
    else:
        # triclinic
        if axes:
            # Any orientation will do - take the one we have
            newaxes = axes
        else:
            # TODO figure out how to calculate the axes in this case
            raise NotImplementedError(
                "Triclinic crystals must be specified using explicit axes"
            )

    # Align main symmetry axis to omega axis
    if  laue_group == '2/m':
        if omega_name == 'X':
            # Rotate -90 around Z to match omega X axis
            result = (
                newaxes[1],
                tuple(-x for x in newaxes[0]),
                newaxes[2]
            )
            result = (result, 'XZX')
        elif omega_name == 'Z':
            # Rotate 90 around X to match omega Z axis
            result = (
                newaxes[0],
                tuple(-x for x in newaxes[2]),
                newaxes[1]
            )
            result = (result, 'ZYZ')
        else:
            result = (newaxes, 'YZY')
    else:
        # Align orthogonal c axis to omega axis
        # NB for triclinic it does not matter anyway
        if omega_name == 'X':
            # Rotate 90 around Y to match omega X axis
            result = (
                newaxes[2],
                newaxes[1],
                tuple(-x for x in newaxes[0])
            )
            result = (result, 'XYX')
        elif omega_name == 'Y':
            # Rotate -90 around X to match omega Y axis
            result = (
                newaxes[0],
                newaxes[2],
            tuple(-x for x in newaxes[1]),
            )
            result = (result, 'YZY')
        else:
            result = (newaxes, 'ZYZ')

    print ('@~@~ std crystal axes', result)
    #
    return result



def test_stratcal_wrap(crystal, orientation, fp_template, fp_crystal,
                       test_dir=None, force=False, log_to_file=True,
                       **stratcal_params):
    """Run stratcal_wrap test with given parameters

    crystal is the test crystal name
    orientation is the crystal orientation as z-x-z Euler angles in degrees in the lab frame
    fp_template is the stratcal input template file
    fp_crystal is the crystal.nml file

    """
    if test_dir is None:
        test_dir = os.getcwd()
    elif not os.path.exists(test_dir):
        os.makedirs(test_dir)

    filename = '%s_%s_%s_%s' % ((crystal, ) + tuple(orientation))
    fp = os.path.join(test_dir, filename)
    fp_in = fp + '.in'
    fp_out = fp + '.out'
    if log_to_file:
        logfile = fp + '.log'
        fp_log = open(logfile, 'w')
        sys.stdout = sys.stderr = fp_log
    else:
        logfile = fp_log = None

    try:

        print ('@~@~ test_stratcal_wrap', crystal, orientation, fp_in)

        orientation = tuple(x*DEG2RAD for x in orientation)
        print ('@~@~ orientation rad', orientation)

        # return fp_log

        # Set up files and directories
        for fp in (fp_in, fp_out):
            if os.path.exists(fp) and not force:
                raise IOError(
                    "File %s already exists. Remove it or use force=True" % fp
                )
            dirname  = os.path.dirname(fp)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

        # Set input crystal parameters
        input_data = f90nml.read(fp_template)
        crystal_data = f90nml.read(fp_crystal)['simcal_crystal_list']

        val = input_data['detector_list']['det_name']
        print ('@~@~ det_name', val, type(val))

        # Get omega axis name
        ll = tuple(abs(x) for x in input_data['stratcal_instrument_list']['omega_axis'])
        idx = 0
        for ii in 1,2:
            if ll[ii] > ll[idx]:
                idx = ii
        # NB we do not distinguish between +/- X (etc.) for now
        omega_name = 'XYZ'[idx]

        # NB align monoclinic crystals with the symmetrty axis on Z
        tt = get_std_crystal_axes(crystal_data,
                                  omega_name=omega_name)
        npaxes = np.array(tt[0], dtype=float)
        euler_order = tt[1]
        print ('@~@~ npaxes', npaxes)
        rot_matrix = mgen.rotation_from_angles(orientation, euler_order)
        rot_matrix = np.transpose(rot_matrix)
        print ('\n\n\n@~@~ rot_matrix', rot_matrix)
        npaxes2 = rot_matrix.dot(npaxes)
        npaxes2 = np.transpose(npaxes2)
        axes = npaxes2.tolist()
        print ('@~@~ axes', axes)
        ii = 0
        for tag in ('cell_a_axis', 'cell_b_axis', 'cell_c_axis'):
            crystal_data[tag] = axes[ii]
            ii += 1

        # Test axes:
        ll = []
        for ii in range(3):
            length = math.sqrt(sum(x*x for x in axes[ii] ))
            ll.append(length)
            print('@~@~ length', ii, length)
            for jj in range(ii):
                print ('@~@~ angle', ii, jj,
                       math.acos(sum(axes[ii][kk]*axes[jj][kk]
                                 for kk in range(3))/(ll[ii]*ll[jj]))/DEG2RAD)

        for tag in ('cell_dim', 'cell_ang_deg', 'u_mat_ang_deg'):
            if tag in crystal_data:
                del crystal_data[tag]
        # recommended by Claus
        crystal_data['res_limit_def'] = 2.5
        crystal_data['orient_mode'] = 0

        input_data['crystal_list']  = crystal_data
        f90nml.write(input_data, fp_in, force=force)

        run_stratcal_wrap(logfile=fp_log, input=fp_in, output=fp_out,
                          **stratcal_params)
    finally:
        if fp_log:
            fp_log.flush()
            os.fsync(fp_log.fileno())
            fp_log.close()
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
    #
    return logfile


if __name__ == '__main__':

    from optparse import OptionParser

    optparser = OptionParser(description=
    """Plug-in replacement wrapper for stratcal
    
    The environment variable GPHL_STRATCAL_BINARY must point to the stratcal binary
    
    
    """)
    optparser.add_option(
        "--input", dest="input", metavar="infile",
        help="input namelist file infile"
    )
    optparser.add_option(
        "--output", dest="output", metavar="outfile",
        help="output namelist file outfile"
    )
    optparser.add_option(
        "--driver", dest="driver", type='int', metavar="driver",
        help="Stratcal driver, defaults to 1 (phasing), use 5 for alignment-only mode, 6 for native collection mode",
    )
    optparser.add_option(
        "--toc", dest="driver", type='int',
        help="""type-of-correction (if exact alignment is not possible)
    defaults to 3 (two-sided).
    Set to 0 (off) to get only exact alignments (and to try alternative axis alignments)"""
                         )
    optparser.add_option(
        "--main-only", dest="main_only", action='store_true',
        help="main-only - calculate only main alignment, skipping cusp alignment"
    )
    optparser.add_option(
        "--selection-mode", dest="selection_mode", type='int',
        help="""selection-mode for preferred strategy
        Default is 2 for normal and 3 for anomalous
        0: kappa and omega angles have smallest |values|
        1: minimal shadow
        2: normal completeness
        3: anomalous completeness
        4: smallest value of |kappa|"""
    )
    # NB we are using anomalous (default) both for phasing and native.
    # Could be changed

    (options, args) = optparser.parse_args()
    options_dict = dict(tt for tt in options.__dict_.items()
                        if tt[1] is not None)


    run_stratcal_wrap(args, **options_dict)
