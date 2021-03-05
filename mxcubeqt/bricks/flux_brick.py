#
#  Project: MXCuBE
#  https://github.com/mxcube.
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

from mxcubeqt.utils import colors, icons, qt_import
from mxcubeqt.base_components import BaseWidget
from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


STATES = {"unknown": colors.GRAY, "ready": colors.LIGHT_BLUE, "error": colors.LIGHT_RED}


class FluxBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Properties (name, type, default value, comment)----------------------

        # Properties for hwobj initialization ---------------------------------
        self.add_property("hwobj_flux", "string", "")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        flux_label = qt_import.QLabel("Flux:", self)
        beam_label = qt_import.QLabel("Beam:", self)
        dose_label = qt_import.QLabel("Dose:", self)
        self.flux_value_label = qt_import.QLabel("-", self)
        self.beam_info_value_label = qt_import.QLabel("-", self)
        self.dose_value_label = qt_import.QLabel("-", self)

        # Layout --------------------------------------------------------------
        _groupbox_vlayout = qt_import.QGridLayout(self)
        _groupbox_vlayout.addWidget(flux_label, 0, 0)
        _groupbox_vlayout.addWidget(beam_label, 1, 0)
        _groupbox_vlayout.addWidget(dose_label, 2, 0)
        _groupbox_vlayout.addWidget(self.flux_value_label, 0, 1)
        _groupbox_vlayout.addWidget(self.beam_info_value_label, 1, 1)
        _groupbox_vlayout.addWidget(self.dose_value_label, 2, 1)
        _groupbox_vlayout.setSpacing(2)
        _groupbox_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------
        flux_label.setMaximumWidth(40)

        # Other ---------------------------------------------------------------

    def property_changed(self, property_name, old_value, new_value):
        BaseWidget.property_changed(self, property_name, old_value, new_value)

    def flux_changed(self, info_dict):
        if info_dict:
            self.flux_value_label.setText("%.2e ph/s" % info_dict["flux"])
