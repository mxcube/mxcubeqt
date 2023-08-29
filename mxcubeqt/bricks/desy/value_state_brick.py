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

from mxcubeqt.base_components import BaseWidget
from mxcubeqt.utils import colors, icons, qt_import

import logging

log = logging.getLogger("HWR")


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class ValueStateBrick(BaseWidget):

    STATE_COLORS = (
        colors.LIGHT_RED,  # ALARM
        colors.LIGHT_YELLOW,  # WARNING
        colors.LIGHT_GREEN,  # ON
        colors.DARK_GRAY,  # UNKNOWN
    )  # NOTINITIALIZED

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.channel_hwobj = None

        # Properties ----------------------------------------------------------
        self.add_property("label", "string", "")
        self.add_property("mnemonic", "string", "")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        _main_hlayout = qt_import.QHBoxLayout(self)
        _main_hlayout.addWidget(self.label_label)
        _main_hlayout.addWidget(self.value_label)
        self.label_label = qt_import.QLabel("")
        self.value_label = qt_import.QLabel("")

        # Layout --------------------------------------------------------------
        _main_hlayout.setSpacing(2)
        _main_hlayout.setContentsMargins(2, 2, 2, 2)

        # Size Policy ---------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------

    def setToolTip(self, name=None, state=None):
        states = ("ON", "WARNING", "ALARM")
        if name is None:
            name = self["mnemonic"]

        self.label.setToolTip(tip)

    def channel_state_changed(self, state):
        if state == "ALARM":
            self.value_label.setStyleSheet("background-color: {self.alarm_color}")
        elif state == "WARNING":
            self.value_label.setStyleSheet("background-color: {self.warning_color}")
        else:
            self.value_label.setStyleSheet("background-color: {self.on_color}")

    def channel_value_changed(self, value):
        self.value_label.setText(f"{value}")

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "label":
            self.label_label.setText(new_value)
        elif property_name == "mnemonic":
            self.channel_hwobj = self.get_hardware_object(new_value)

            if self.channel_hwobj is not None:
                self.connect(
                    self.channel_hwobj, "valueChanged", self.channel_value_changed
                )
                self.connect(
                    self.motor_hwobj, "stateChanged", self.channel_state_changed
                )
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)
