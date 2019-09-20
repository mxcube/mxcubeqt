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

from gui.utils import Colors, Icons, QtImport
from gui.BaseComponents import BaseWidget

from HardwareRepository import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class DoorInterlockBrick(BaseWidget):

    STATES = {
        "unknown": Colors.LIGHT_GRAY,
        "disabled": Colors.LIGHT_GRAY,
        "error": Colors.LIGHT_RED,
        "unlocked": Colors.LIGHT_GRAY,
        "locked_active": Colors.LIGHT_GREEN,
        "locked_inactive": Colors.LIGHT_GRAY,
    }

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Door interlock", self)
        self.main_groupbox.setAlignment(QtImport.Qt.AlignCenter)
        self.state_label = QtImport.QLabel("<b>unknown</b>", self.main_groupbox)
        Colors.set_widget_color(self.state_label, self.STATES["unknown"])
        self.state_label.setAlignment(QtImport.Qt.AlignCenter)
        self.state_label.setFixedHeight(24)
        self.unlock_door_button = QtImport.QPushButton(
            Icons.load_icon("EnterHutch"), "Unlock", self.main_groupbox
        )

        # Layout --------------------------------------------------------------
        _main_gbox_vlayout = QtImport.QVBoxLayout(self.main_groupbox)
        _main_gbox_vlayout.addWidget(self.state_label)
        _main_gbox_vlayout.addWidget(self.unlock_door_button)
        _main_gbox_vlayout.setSpacing(2)
        _main_gbox_vlayout.setContentsMargins(4, 4, 4, 4)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.unlock_door_button.clicked.connect(self.unlock_doors)

        # Other ---------------------------------------------------------------
        self.state_label.setToolTip("Shows the current door state")
        self.unlock_door_button.setToolTip("Unlocks the doors")

        self.connect(
            HWR.beamline.hutch_interlock,
            "doorInterlockStateChanged",
            self.state_changed
        )
        HWR.beamline.hutch_interlock.update_values()

    def unlock_doors(self):
        self.unlock_door_button.setEnabled(False)
        HWR.beamline.hutch_interlock.unlock_door_interlock()

    def updateLabel(self, label):
        self.main_groupbox.setTitle(label)

    def state_changed(self, state, state_label=None):
        try:
            color = self.STATES[state]
        except KeyError:
            state = "unknown"
            color = self.STATES[state]
        Colors.set_widget_color(self.state_label, color)
        if state_label is not None:
            self.state_label.setText("<b>%s</b>" % state_label)
        else:
            self.state_label.setText("<b>%s</b>" % state)

        self.unlock_door_button.setEnabled(state == "locked_active")
