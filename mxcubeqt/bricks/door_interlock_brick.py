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

from mxcubeqt.utils import colors, icons, qt_import
from mxcubeqt.base_components import BaseWidget

from mxcubecore import HardwareRepository as HWR


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class DoorInterlockBrick(BaseWidget):

    STATES = {
        "unknown": colors.LIGHT_GRAY,
        "disabled": colors.LIGHT_GRAY,
        "error": colors.LIGHT_RED,
        "unlocked": colors.LIGHT_GRAY,
        "locked_active": colors.LIGHT_GREEN,
        "locked_inactive": colors.LIGHT_GRAY,
    }

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------

        # Internal values -----------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_groupbox = qt_import.QGroupBox("Door interlock", self)
        self.main_groupbox.setAlignment(qt_import.Qt.AlignCenter)
        self.state_label = qt_import.QLabel("<b>unknown</b>", self.main_groupbox)
        colors.set_widget_color(self.state_label, self.STATES["unknown"])
        self.state_label.setAlignment(qt_import.Qt.AlignCenter)
        self.state_label.setFixedHeight(24)
        self.unlock_door_button = qt_import.QPushButton(
            icons.load_icon("EnterHutch"), "Unlock", self.main_groupbox
        )

        # Layout --------------------------------------------------------------
        _main_gbox_vlayout = qt_import.QVBoxLayout(self.main_groupbox)
        _main_gbox_vlayout.addWidget(self.state_label)
        _main_gbox_vlayout.addWidget(self.unlock_door_button)
        _main_gbox_vlayout.setSpacing(2)
        _main_gbox_vlayout.setContentsMargins(4, 4, 4, 4)

        _main_vlayout = qt_import.QVBoxLayout(self)
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
        colors.set_widget_color(self.state_label, color)
        if state_label is not None:
            self.state_label.setText("<b>%s</b>" % state_label)
        else:
            self.state_label.setText("<b>%s</b>" % state)

        self.unlock_door_button.setEnabled(state == "locked_active")
