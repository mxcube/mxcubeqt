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
import uuid
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

def run_stratcal_wrap(input, logfile=None, output=None, main_only=None,
                      selection_mode=None, type_of_correction=None,
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

    if main_only:
        options['main-only'] = None
    elif 'main-only' in options:
        if options['main-only']:
            options['main-only'] = None
        else:
            del options['main-only']

    if selection_mode is not None:
        options['selection-mode'] = selection_mode
    if type_of_correction is not None:
        options['type-of-correction'] = type_of_correction

    if options.get('driver') == 6:
        # Native data collection - determine strategy and run with driver 5
        options['driver'] = 5
        return run_stratcal_native(logfile=logfile, **options)

    else:
        running_process = run_stratcal(logfile=logfile, **options)
        running_process.wait()
    return running_process.returncode

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

def stratcal_merge_output(indata_exch, outdata_exch):
    """Merges information from indata_exch and outdata_exch
    keeping all information from the indata,
    replacing the stratcal_sweep_list, and asdding new IDs as needed"""

    result = copy.deepcopy(indata_exch)

    loop_counts = result['loop_count_list']

    # Copy settings back with their IDs
    ll = outdata_exch['goniostat_setting_list']
    if not isinstance(ll, list):
        ll = [ll]
    loop_counts['n_goniostat_settings'] = len(ll)
    result['goniostat_setting_list'] = ll

    ll = outdata_exch['centred_goniostat_setting_list']
    if not isinstance(ll, list):
        ll = [ll]
    loop_counts['n_centred_goniostat_settings'] = len(ll)
    result['centred_goniostat_setting_list'] = ll

    result['stratcal_sweep_list'] = sweeps = outdata_exch['stratcal_sweep_list']
    if not isinstance(sweeps, list):
        sweeps = [sweeps]
    loop_counts['n_sweeps'] = len(sweeps)

    # Transfer beam, beamstop and detector setting IDs from input
    # NBNB This assumes that there was only one of each
    # and it was transferred as by stratcal_exch2org
    dd = {}
    for tag in ('beam_setting', 'beamstop_setting', 'detector_setting'):
        ll = indata_exch[tag + '_list']
        if isinstance(ll, list):
            dd[tag + '_id'] = ll[0]['id']
        else:
            dd[tag + '_id'] = ll['id']
    for sweep in sweeps:
        sweep.update(dd)

    #
    return result


def stratcal_merge_output_2(indata_exch, outdata):
    """Merges information from indata_exch and outdata
    keeping all information from the indata,
    replacing the stratcal_sweep_list, and asdding new IDs as needed

    NB Variant, that gets its input from original (NOT exchange) format stratcal.out
    Written when stratcal.out.def was NOT correct.

    NBNB HACKY"""

    result = copy.deepcopy(indata_exch)

    sweeps = outdata['sweep_list']
    if not isinstance(sweeps, list):
        sweeps = [sweeps]
    goniostat_setting_list = result['goniostat_setting_list'] = []
    centred_setting_list = result['centred_goniostat_setting_list'] = []
    stratcal_sweep_list = result['stratcal_sweep_list'] = []
    goniostat_setting_map = {}

    # Transfer beam, beamstop and detector setting IDs from input
    # NBNB This assumes that there was only one of each
    # and it was transferred as by stratcal_exch2org
    other_settings = {}
    for tag in ('beam_setting', 'beamstop_setting', 'detector_setting'):
        ll = indata_exch[tag + '_list']
        if isinstance(ll, list):
            other_settings[tag + '_id'] = ll[0]['id']
        else:
            other_settings[tag + '_id'] = ll['id']

    ii = 0
    for sweep in sweeps:

        sw = f90nml.Namelist()
        sw.update(other_settings)

        # Make startcal_sweep
        ii += 1
        stratcal_sweep_list.append(sw)
        sw['start_deg'] = sweep['omega_deg']
        sw['length_deg'] = sweep['n_frames'] * sweep['step_deg']
        sw['type'] = 'MAIN:ORIENT'
        sw['group_no'] = ii

        # Check if we have the exact same setting already
        settings = (
            sweep['omega_deg'],
            sweep['kappa_deg'],
            sweep['phi_deg']
        ) + tuple(sweep['trans_xyz'])
        use_id = goniostat_setting_map.get(settings)
        has_centring = any(x for x in settings[3:])
        if not use_id:

            # Make goniostat_setting
            goniostat_setting = f90nml.Namelist()
            goniostat_setting['id'] = str(uuid.uuid1())
            goniostat_setting['omega_deg'] = settings[0]
            goniostat_setting['kappa_deg'] = settings[1]
            goniostat_setting['phi_deg'] = settings[2]
            goniostat_setting['spindle_deg'] = sweep['spindle_deg']
            goniostat_setting['scan_axis_no'] = sweep['axis_no']
            goniostat_setting['aligned_crystal_axis_order'] = 0
            goniostat_setting_list.append(goniostat_setting)

            if has_centring:
                # Make centring_goniostat_setting
                obj = f90nml.Namelist()
                use_id = obj['id'] =  str(uuid.uuid1())
                obj['goniostat_setting_id'] = goniostat_setting['id']
                obj['trans_1'], obj['trans_2'], obj['trans_3'] = settings[3:]
                centred_setting_list.append(obj)
            else:
                use_id = goniostat_setting['id']

        if has_centring:
            sw['centred_goniostat_setting_id'] = use_id
            sw['goniostat_setting_id'] = ' '
        else:
            sw['goniostat_setting_id'] = use_id
            sw['centred_goniostat_setting_id'] = ' '

    loop_counts = result['loop_count_list']
    loop_counts['n_sweeps'] = len(sweeps)
    loop_counts['n_goniostat_settings'] = len(goniostat_setting_list)
    loop_counts['n_centred_goniostat_settings'] = len(centred_setting_list)
    #
    return result

def run_stratcal_native(logfile=None, **options):
    """Run stratcal for native phasing (mode 6)"""

    # Programmers note:
    #Plain names are in lab coordinate system,
    # suffux _cr are in orthobnormal crystal system.

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

    # coordinates of reciprocal-space crystal matrix
    # in real-space coordinate system
    # Could also be done with metric tensor
    mm = [
        np.cross(crystal_matrix[1], crystal_matrix[2]),
        np.cross(crystal_matrix[2], crystal_matrix[0]),
        np.cross(crystal_matrix[0], crystal_matrix[1]),
    ]
    # Now make orthonormal coordinate system
    if laue_group == '-1':
        mm[2] = unit_vector(np.cross(mm[0], mm[1]))
        mm[1] = unit_vector(np.cross(mm[2], mm[0]))
        mm[0] = unit_vector(mm[0])
    elif laue_group == '2/m':
        mm[2] = unit_vector(np.cross(mm[0], mm[1]))
        mm[1] = unit_vector(mm[1])
        mm[0] = unit_vector(mm[0])
    else:
        mm[2] = unit_vector(mm[2])
        mm[1] = unit_vector(np.cross(mm[2], mm[0]))
        mm[0] = unit_vector(mm[0])
    crystal_unit_np = np.array(mm)

    # NB for all except triclinic crystals, the Y and Z axes of
    # crystal_unit_np match the Y and Z axes of the real-space lattice
    # Only the X axis does not

    # scan axis in real-space coordinate system. NB assumes omega scan axis
    scan_axis = unit_vector(
        input_data_exch['stratcal_instrument_list']['omega_axis']
    )

    # orthog_component is a unit vector orthogonal to the symmetry axis
    # and in the same plane as the symmetry and rotation axes.
    # omega_projection_angle is the angle from the orthonormal X axis to the
    # projection of the omega axis
    scan_axis_cr = unit_vector(crystal_unit_np.dot(scan_axis))
    if  laue_group == '2/m':
        # Index of symmetry axis
        symm_axis_index = 1
        symm_axis_cr = np.array((0,1,0))
        xx = scan_axis_cr[0]
        zz = scan_axis_cr[2]
        omega_projection_angle = -math.atan2(zz, xx)
        if zz:
            orthog_component_cr = unit_vector((xx, 00, zz))
        else:
            orthog_component_cr = np.array((1,0,0))
    else:
        # For triclinic there is no symmetry axis but we might as well use c*
        symm_axis_index = 2
        symm_axis_cr = np.array((0,0,1))
        xx = scan_axis_cr[0]
        yy = scan_axis_cr[1]
        omega_projection_angle = math.atan2(yy, xx)
        if yy:
            orthog_component_cr = unit_vector((xx, yy, 0))
        else:
            orthog_component_cr = np.array((1,0,0))

    cr_symm_axis = crystal_unit_np[symm_axis_index]
    symm_projection = symm_axis_cr.dot(scan_axis_cr)
    print ('@~@~ scan_axis_cr', scan_axis_cr)
    # if abs(symm_projection) == 1:
    #     orthog_component = crystal_unit_np[0]
    #     omega_projection_angle = 0
    # else:
    #     orthog_component = unit_vector(
    #         scan_axis - cr_symm_axis.dot(scan_axis) * cr_symm_axis
    #     )
    #     # Angle between the projection of the omega axis in the crystal
    #     # orthogonal plane and the crystal symmetry axis
    #     omega_projection_angle = angle_between(crystal_unit_np[0],
    #                                            orthog_component)

    print ('@~@~ crystal', sg_name, laue_group, '\n', crystal_unit_np)
    print('@~@~ axis', scan_axis, scan_axis_cr, symm_projection, orthog_component_cr)
    print ('@~@~ cell lengths', [np.linalg.norm(crystal_matrix[ii])
                                 for ii in range(3)])
    print('@~@~ +/- angle bc',
          angle_between(crystal_matrix[1], crystal_matrix[2], deg=True),
          angle_between(crystal_unit_np[1], crystal_unit_np[2], deg=True))
    print('@~@~ +/- angle ac',
          angle_between(crystal_matrix[0], crystal_matrix[2], deg=True) ,
          angle_between(crystal_unit_np[0], crystal_unit_np[2], deg=True))
    print('@~@~ +/- angle ab',
          angle_between(crystal_matrix[0], crystal_matrix[1], deg=True),
          angle_between(crystal_unit_np[0], crystal_unit_np[1], deg=True) )
    print('@~@~ +/- angle a-omega',
          angle_between(crystal_matrix[0], scan_axis, deg=True),
          angle_between(crystal_unit_np[0], scan_axis_cr, deg=True))
    print('@~@~ +/- angle b-omega',
          angle_between(crystal_matrix[1], scan_axis, deg=True),
          angle_between(crystal_unit_np[1], scan_axis_cr, deg=True) )
    print('@~@~ +/- angle c-omega',
          angle_between(crystal_matrix[2], scan_axis, deg=True),
          angle_between(crystal_unit_np[2], scan_axis_cr, deg=True) )
    print ('@~@~ omega_projection_angle', math.degrees(omega_projection_angle))

    if laue_group == '-1':
        # Triclinic, nothing doing. Pass on to default stratcal
        running_process = run_stratcal(**options)
        running_process.wait()
        return running_process.returncode

    elif laue_group == '2/m':
        # Monoclinic
        # Two directions, theta=54.7deg; phi +/-45 deg away from symmetry axis
        zval = math.tan(math.radians(35.3))
        vv = orthog_component_cr + symm_axis_cr * zval

        for ii in (1,-1):
            rot_matrix = mgen.rotation_around_y(ii * math.pi/4)
            # We are using post-multiplication (of row vectors)
            # so we must transpose the rotation matrix.
            # See mgen docs and links therein
            rot_matrix.transpose()
            orientation = tuple(vv.dot(rot_matrix))
            orthog_vector = tuple(np.cross(orientation, symm_axis_cr))
            add_crystal_orientation(input_data_org, orientation, orthog_vector)

    elif laue_group == 'mmm':
        # Orthorhombic
        # Along a body diagonal - selecting diagonal closest to the rotation axis
        orientation = tuple(math.copysign(1,x) for x in scan_axis_cr)
        orthog_vector = tuple(np.cross(orientation, symm_axis_cr))
        add_crystal_orientation(input_data_org, orientation, orthog_vector)

    elif laue_group == '4/m':
        # 'C4'
        # One directions, theta=54.7deg
        zval = math.tan(math.radians(35.3))
        orientation = tuple(orthog_component_cr + zval * symm_axis_cr)
        orthog_vector = tuple(np.cross(orientation, symm_axis_cr))
        add_crystal_orientation(input_data_org, orientation, orthog_vector)

    elif laue_group == '4/mmm':
        # 422
        # theta=67.5, 22.5 deg from the plane of a twofold axis
        # As close as possible to omega axis
        mult, remainder = nearest_modulo(omega_projection_angle, math.pi/2)
        aa = mult*math.pi/2 + math.copysign(math.pi/8, remainder)
        orientation = (math.cos(aa), math.sin(aa), math.tan(math.pi/8))
        orthog_vector = tuple(np.cross(orientation, symm_axis_cr))
        add_crystal_orientation(input_data_org, orientation, orthog_vector)

    elif laue_group == '-3':
        # 'C3'
        # Two directions ca. 30deg and 40 deg above the plane, 60deg apart
        for ii in (1,-1):
            zval =math.tan(math.radians(35.3 + ii * 5))
            vv = orthog_component_cr + zval * symm_axis_cr
            rot_matrix = mgen.rotation_around_z(ii * math.pi/6)
            # We are using post-multiplication (of row vectors)
            # so we must transpose the rotation matrix.
            # See mgen docs and links therein
            rot_matrix.transpose()
            orientation = tuple(vv.dot(rot_matrix))
            orthog_vector = tuple(np.cross(orientation, symm_axis_cr))
            add_crystal_orientation(input_data_org, orientation, orthog_vector)

    elif laue_group == '-3m':
        # '32'
        # One direction, theta=60deg, phi 30 deg from a twofold axis
        # NB X* is 30 deg from a twofold axis
        # As close as possible to omega axis
        mult, remainder = nearest_modulo(omega_projection_angle, math.pi/3)
        # aa = mult*math.pi/3 + math.copysign(math.pi/6, remainder)
        aa = mult*math.pi/3

        orientation = (math.cos(aa), math.sin(aa), math.tan(math.pi/6))
        orthog_vector = tuple(np.cross(orientation, symm_axis_cr))
        add_crystal_orientation(input_data_org, orientation, orthog_vector)

    elif laue_group == '6/m':
        # 'C6'
        # One directions, theta=60deg
        zval = math.tan(math.pi/6)
        orientation = tuple(orthog_component_cr + zval * symm_axis_cr)
        orthog_vector = tuple(np.cross(orientation, symm_axis_cr))
        add_crystal_orientation(input_data_org, orientation, orthog_vector)

    elif laue_group == '6/mmm':
        # '622'
        # theta=70, 15 deg from the plane of a twofold axis
        # NB X* is on a twofold axis
        # As close as possible to omega axis
        mult, remainder = nearest_modulo(omega_projection_angle, math.pi/3)
        aa = mult*math.pi/3 + math.copysign(math.pi/12, remainder)
        orientation = (math.cos(aa), math.sin(aa), math.tan(math.pi/9))
        orthog_vector = tuple(np.cross(orientation, cr_symm_axis))
        add_crystal_orientation(input_data_org, orientation, orthog_vector)

    elif laue_group == 'm-3':
        # '23'
        # CA. 1, 0.3, 0.3 (on diagonal cross of a face)
        orientation = (1, 0.3, 0.3)
        # Put in same quadrant as rotation axis
        orientation = tuple(math.copysign(orientation[ii], scan_axis_cr[ii])
                            for ii in range(3))
        orthog_vector = tuple(np.cross(orientation, cr_symm_axis))
        add_crystal_orientation(input_data_org, orientation, orthog_vector)

    elif laue_group == 'm-3m':
        # '432'
        # Ca, 1.0, 0.2, 0.4
        orientation = (1, 0.2, 0.4)
        # Put in same quadrant as rotation axis
        orientation = tuple(math.copysign(orientation[ii], scan_axis_cr[ii])
                            for ii in range(3))
        orthog_vector = tuple(np.cross(orientation, cr_symm_axis))
        add_crystal_orientation(input_data_org, orientation, orthog_vector)

    else:
        # sg_name must be empty string
        raise ValueError("Illegal value (empty string) for SG_NAME")

    # Add orient list count
    orient_list = input_data_org['orient_list']
    n_orients = len(orient_list)
    input_data_org['setup_list']['n_orients'] = n_orients

    # Move aside old input and save new input in input_data_org['orient_list'])ts place
    tt = os.path.splitext(fp_in)
    fp_in_backup = '_wrap'.join(tt)
    os.rename(fp_in, fp_in_backup)
    f90nml.write(input_data_org, fp_in)

    # Run stratcal
    running_process = run_stratcal(logfile=logfile, **options)
    running_process.wait()

    # NBNB TODO rewrite .out file to get correct ids etc.
    outfile = options['output']
    stem, junk = os.path.splitext(outfile)
    for ext in ('.out.def', '.out2.def'):
        fp_out = stem + ext
        if os.path.exists(fp_out):
            fp_bak = '_raw'.join((stem, ext))
            # out_data = f90nml.read(fp_out)
            # Temporary, while reading .out instead of .out.def
            out_data = f90nml.read(fp_out[:-4])
            out_data = stratcal_merge_output_2(input_data_exch, out_data)
            # out_data = f90nml.read(fp_out)
            # out_data = stratcal_merge_output(input_data_exch, out_data)
            os.rename(fp_out, fp_bak)
            f90nml.write(out_data, fp_out)

    return running_process.returncode

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


def add_crystal_orientation(data_dict, orientation, orthogonal_orientation):
    """Add an orient_list record using orientation in orthonormal crystal coordinates
    orthogonal_orientation is the direction to align for setting starting omega"""

    print('@~@~ add_crystal_orientation', orientation, orthogonal_orientation)

    setup_list = data_dict['setup_list']

    orient_list = data_dict.get('orient_list')
    if not orient_list:
        orient_list = data_dict['orient_list'] = []
    orient = f90nml.Namelist()
    orient_list.append(orient)

    # Parameters identical to default omitted, I assume they will be filled in.
    orient['crys_vec_mode'] = [2, 2]    # orthonormal space
    orient['lab_vec_mode'] = 1          # Main orientation
    orient['crys_vec_1'] = list(orientation) # Orient this
    orient['crys_vec_2'] = list(orthogonal_orientation)    # with omega here
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
    # # Gives problems, reads as unicode, which FOPRTRAN cannot read
    # orient['name_template'] = "data/sweep%s_????.cbf"  # dummy, not used
    orient['step_deg'] = 1              # 1 degree steps
    orient['n_frames'] = 360            # 360 of them
    orient['image_no'] = 1              # 360 of them

def run_stratcal(logfile=None, **options):
    """Call stratcal binary using command line options 'options'"""
    envs = os.environ
    # NBNB this little hack is necessary as stratcal points to this file
    # We need to get the underlying binary in some other way
    # NB this requires the top GPhL installation property to be set
    # This is hacky, but the wrapper is a temporary expedient anyway
    stratcal_binary = envs.get('GPHL_STRATCAL_BINARY')
    if stratcal_binary is None:
        stratcal_binary = os.path.join(envs['GPHL_INSTALLATION'], 'stratcal')
    cmd_list = [stratcal_binary]
    for tag, val in sorted(options.items()):
        cmd_list.append('--' + tag)
        if val not in (None, ''):
            cmd_list.append(str(val))
    print ('@~@~ running stratcal', cmd_list)
    if isinstance(logfile, (str, unicode)):
        fp_log = open(logfile, 'w')
    else:
        fp_log = logfile
        # Flush the file, to make sure stratcal output (on stderr) is not mixed
        if fp_log and not isinstance(fp_log, str):
            # Could be None
            fp_log.flush()
            os.fsync(fp_log.fileno())
    try:
        result = subprocess.Popen(cmd_list, env=envs, stdout=fp_log,
                                  stderr=fp_log)
    finally:
        if isinstance(logfile, (str, unicode)):
            fp_log.flush()
            os.fsync(fp_log.fileno())
            fp_log.close()
    #
    return result

def get_std_crystal_axes(crystal_data, omega_name='Z'):
    """get (cell_a_axis, cell_b_axis, cell_c_axis) in unrotated position
    from a read-in crystal_list dictionary (with lower case tags)

    Use ONLY for testing to get predictable orientations from input angles

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
            (-b/2, math.cos(math.pi/6)*b, 0),
            (0, 0, c)
        )
    elif laue_group == '2/m':
        # monoclinic
        if angles:
            beta = angles[1]
        else:
            beta = angle_between(axes[0], axes[2], deg=True)
        newaxes = (
            (a, 0, 0),
            (0, b, 0),
            (c*math.cos(math.radians(beta)), 0, -c*math.sin(math.radians(beta)))
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
                (0,-newaxes[0][0],0),
                (newaxes[1][1],0,0),
                (0, -newaxes[2][0], newaxes[2][2])
            )
            result = (result, 'XZX')
        elif omega_name == 'Z':
            # Rotate 90 around X to match omega Z axis
            result = (
                newaxes[0],
                (0, 0, newaxes[1][1]),
                (newaxes[2][0], -newaxes[2][2], 0)
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
                (0,0,-newaxes[0][0]),
                (0, newaxes[1][1],-newaxes[1][0]),
                (newaxes[2][2],0,0)
            )
            result = (result, 'XYX')
        elif omega_name == 'Y':
            # Rotate -90 around X to match omega Y axis
            result = (
                newaxes[0],
                (0,newaxes[1][2],-newaxes[1][1]),
                (0,newaxes[2][2],0)
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
        # return logfile
        fp_log = open(logfile, 'w')
        sys.stdout = sys.stderr = fp_log
    else:
        logfile = fp_log = None

    try:

        print ('@~@~ test_stratcal_wrap', crystal, orientation, fp_in)

        orientation = tuple(math.radians(x) for x in orientation)
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
        # We are using post-multiplication (of row vectors)
        # so we must transpose the rotation matrix.
        # See mgen docs and links therein
        rot_matrix.transpose()
        print ('\n\n\n@~@~ rot_matrix', rot_matrix)
        npaxes2 = npaxes.dot(rot_matrix)
        print ('@~@~ npaxes2', npaxes2)
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
                       angle_between(axes[ii], axes[jj], deg=True))

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


# Angle utility functions (Thanks to DAvid Wolever,
# https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python#13849249


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    if not isinstance(vector, np.ndarray):
        vector = np.array(vector)
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2, deg=False):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
    result = math.copysign(angle, np.linalg.norm(np.cross(v1_u, v2_u)))
    if deg:
        return math.degrees(result)
    else:
        return result

def nearest_modulo(value, divisor):
    half = divisor/2
    tt = divmod(value+half, divisor)
    return (tt[0], tt[1]-half)


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
        "--driver", dest="driver", type='int', metavar="driver", default=6,
        help="Stratcal driver, defaults to 1 (phasing), use 5 for alignment-only mode, 6 for native collection mode",
    )
    optparser.add_option(
        "--toc", dest="type_of_correction", type='int', default=1,
        help="""type-of-correction (if exact alignment is not possible)
    0:apply selection_mode and throw error if no solution found.
    1:correction type 'right', disregard selection mode
    2:correction type 'left', disregard selection mode
    3:correction type 'two-sided', disregard selection mode. Buggy as of 20180731
    """
                         )
    optparser.add_option(
        "--main-only", dest="main_only", action='store_true', default=True,
        help="main-only - calculate only main alignment, skipping cusp alignment"
    )
    optparser.add_option(
        "--selection-mode", dest="selection_mode", type='int', default=4,
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
    options_dict = dict(tt for tt in options.__dict__.items()
                        if tt[1] is not None)
    returncode = run_stratcal_wrap(*args, **options_dict)
    # This tells workdflow that program ran OK:
    print (' NORMAL termination')
    sys.exit(returncode)
