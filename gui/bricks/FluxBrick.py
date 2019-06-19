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

from gui.utils import Colors, Icons, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


STATES = {"unknown": Colors.GRAY, "ready": Colors.LIGHT_BLUE, "error": Colors.LIGHT_RED}


class FluxBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.flux_hwobj = None

        # Internal values -----------------------------------------------------

        # Properties (name, type, default value, comment)----------------------

        # Properties for hwobj initialization ---------------------------------
        self.add_property("hwobj_flux", "string", "")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        flux_label = QtImport.QLabel("Flux:", self)
        beam_label = QtImport.QLabel("Beam:", self)
        dose_label = QtImport.QLabel("Dose:", self)
        self.flux_value_label = QtImport.QLabel("-", self)
        self.beam_info_value_label = QtImport.QLabel("-", self)
        self.dose_value_label = QtImport.QLabel("-", self)

        # Layout --------------------------------------------------------------
        _groupbox_vlayout = QtImport.QGridLayout(self)
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
        if property_name == "hwobj_flux":
            if self.flux_hwobj is not None:
                self.disconnect(self.flux_hwobj, "fluxChanged", self.flux_changed)

            self.flux_hwobj = self.get_hardware_object(new_value)

            if self.flux_hwobj is not None:
                self.connect(self.flux_hwobj, "fluxChanged", self.flux_changed)
                self.flux_changed(self.flux_hwobj.get_flux_info())
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def flux_changed(self, info_dict):
        if info_dict:
            self.flux_value_label.setText("%.2e ph/s" % info_dict["flux"])
