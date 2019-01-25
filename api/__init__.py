#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import sys
import logging

from HardwareRepository import HardwareRepository


__credits__ = ["MXCuBE colaboration"]
__license__ = "LGPLv3+"


"""
api provides access to the hardware repository.
Following namespace is used:
"""

beamline_setup = None
queue_model = None
queue_manager = None

HWOBJ_ROLES = ("transmission",
               "resolution",
               "energy",
               "flux",
               "beam_info",
               "omega_axis",
               "kappa_axis",
               "kappa_phi_axis",
               "detector",
               "detector_distance",
               "door_interlock",
               "fast_shutter",
               "safety_shutter",
               "machine_info",
               "session",
               "diffractometer",

               "sample_changer",
               "plate_manipulator",

               "collect",
               "energyscan",
               "xrf_spectrum",
               "xray_imaging",

               "data_analysis",
               "auto_processing",
               "parallel_processing")

def init(hwr_path):
    hwr = HardwareRepository.getHardwareRepository(hwr_path)
    hwr.connect()

    global beamline_setup
    global queue_model
    global queue_manager

    beamline_setup = hwr.getHardwareObject("beamline-setup")
    queue_model = hwr.getHardwareObject("queue-model")
    queue_manager = hwr.getHardwareObject("queue")

    for role in HWOBJ_ROLES:
        if hasattr(beamline_setup, "%s_hwobj" % role):
            setattr(sys.modules[__name__], role, getattr(beamline_setup, "%s_hwobj" % role))
        else:
            setattr(sys.modules[__name__], role, None)
            logging.getLogger("API").warning("%s role is not defined in the beamline_setup" % role)

    setattr(sys.modules[__name__], "lims", getattr(beamline_setup, "lims_client_hwobj"))
    setattr(sys.modules[__name__], "graphics", getattr(beamline_setup, "shape_history_hwobj"))

    """
    global beamline_setup
    global transmission
    global resolution
    global energy
    global flux
    global beam_info
    global osc_axis
    global kappa_axis
    global kappa_phi_axis
    global detector
    global detector_distance
    global door_interlock
    global fast_shutter
    global machine_info
    global safety_shutter

    global diffractometer
    global sample_changer
    global plate_manipulator

    global graphics
    global session
    global collect
    global lims
    global energyscan
    global xrf_spectrum
    global xray_imaging

    global data_analysis
    global auto_processing
    global parallel_processing
    """
