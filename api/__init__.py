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
import warnings

from HardwareRepository import HardwareRepository


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"


"""
api provides access to the hardware repository.
Following namespace is used:
"""

_hwr_logger = logging.getLogger("HWR")
for handler in _hwr_logger.handlers:
    _hwr_logger.removeHandler(handler)

beamline_setup = None
queue_model = None
queue_manager = None

CORE_HWOBJ_ROLES = (
    "transmission",
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
    "collect",
)

ADDITIONAL_HWOBJ_ROLES = (
    "sample_changer",
    "plate_manipulator",
    "energyscan",
    "xrf_spectrum",
    "xray_imaging",
    "data_analysis",
    "auto_processing",
    "parallel_processing",
    "gphl_workflow",
    "gphl_connection",
)


def init(hwr_path):
    # hwr = HardwareRepository.getHardwareRepository(hwr_path)

    warnings.warn("The api module is deprecated - use the Beamline object instead")
    hwr = HardwareRepository.getHardwareRepository()
    hwr.connect()

    global beamline_setup
    global queue_model
    global queue_manager

    beamline_setup = hwr.getHardwareObject("beamline-setup")
    queue_model = hwr.getHardwareObject("queue-model")
    queue_manager = hwr.getHardwareObject("queue")

    logging.getLogger("API").debug("Initializing API...")
    error_count = 0

    for role in CORE_HWOBJ_ROLES:
        if hasattr(beamline_setup, "%s_hwobj" % role):
            setattr(
                sys.modules[__name__], role, getattr(beamline_setup, "%s_hwobj" % role)
            )
        else:
            setattr(sys.modules[__name__], role, None)
            logging.getLogger("HWR").warning(
                "API: %s role is not defined in the beamline_setup" % role
            )
            error_count += 1

    for role in ADDITIONAL_HWOBJ_ROLES:
        if hasattr(beamline_setup, "%s_hwobj" % role):
            setattr(
                sys.modules[__name__], role, getattr(beamline_setup, "%s_hwobj" % role)
            )
        else:
            setattr(sys.modules[__name__], role, None)

    if error_count == 0:
        logging.getLogger("HWR").info("Initializing of API done")
    else:
        logging.getLogger("API").info(
            "Initializing of API done (%d warning(s): see messages above)."
            % error_count
        )

    setattr(sys.modules[__name__], "lims", getattr(beamline_setup, "lims_client_hwobj"))
    setattr(
        sys.modules[__name__],
        "graphics",
        getattr(beamline_setup, "shape_history_hwobj"),
    )
