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
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

from gui.BaseComponents import BaseWidget
from gui.utils import Colors, QtImport

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class PhaseBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Internal values -----------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("confirmPhaseChange", "boolean", False)

        # Properties to initialize hardware objects --------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.group_box = QtImport.QGroupBox("Phase", self)
        self.phase_combobox = QtImport.QComboBox(self.group_box)

        # Layout --------------------------------------------------------------
        _group_box_vlayout = QtImport.QVBoxLayout(self.group_box)
        _group_box_vlayout.addWidget(self.phase_combobox)
        _group_box_vlayout.addStretch()
        _group_box_vlayout.setSpacing(2)
        _group_box_vlayout.setContentsMargins(0, 0, 0, 0)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.group_box)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(2, 2, 2, 2)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.phase_combobox.activated.connect(self.change_phase)

        # Other ---------------------------------------------------------------
        Colors.set_widget_color(
            self.phase_combobox, Colors.LIGHT_GREEN, QtImport.QPalette.Button
        )

        self.init_phase_list()

        self.connect(
            HWR.beamline.diffractometer, "minidiffPhaseChanged", self.phase_changed
        )
        HWR.beamline.diffractometer.update_values()

    def init_phase_list(self):
        self.phase_combobox.clear()
        phase_list = HWR.beamline.diffractometer.get_phase_list()
        if len(phase_list) > 0:
            for phase in phase_list:
                self.phase_combobox.addItem(phase)
            self.setEnabled(True)
        else:
            self.setEnabled(False)

    def change_phase(self):
        if HWR.beamline.diffractometer is not None:
            requested_phase = self.phase_combobox.currentText()
            if self["confirmPhaseChange"] and requested_phase == "BeamLocation":
                conf_msg = "Please remove any objects that might cause collision!\n" + \
                           "Continue"
                if (
                    QtImport.QMessageBox.warning(
                        None,
                        "Warning",
                        conf_msg,
                        QtImport.QMessageBox.Ok,
                        QtImport.QMessageBox.Cancel,
                   )
                   == QtImport.QMessageBox.Ok
                ):
                   HWR.beamline.diffractometer.set_phase(requested_phase, timeout=None)
            else:
                HWR.beamline.diffractometer.set_phase(requested_phase, timeout=None)

    def phase_changed(self, phase):
        if phase.lower() != "unknown" and self.phase_combobox.count() > 0:
            # index = self.phase_combobox.findText(phase)
            # self.phase_combobox.setEditText(phase)
            self.phase_combobox.setCurrentIndex(self.phase_combobox.findText(phase))
        else:
            self.phase_combobox.setCurrentIndex(-1)
