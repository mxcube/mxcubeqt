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

import logging

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.base_components import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ALBA"


STATES = {"unknown": colors.GRAY, "ready": colors.LIGHT_BLUE, "error": colors.LIGHT_RED}


class AlbaMachineInfoBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)
        self.logger = logging.getLogger("GUI MachineInfo")
        self.logger.info("__init__()")
        # Hardware objects ----------------------------------------------------
        self.mach_info_hwobj = None

        # Internal values -----------------------------------------------------
        # self.last_value = None

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")
        self.add_property("formatString", "formatString", "###.#")
        # self.addProperty('diskThreshold', 'float', '200')

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------
        self.defineSlot("setColDir", ())

        # Graphic elements ----------------------------------------------------
        self.groupBox = qt_import.QGroupBox("Machine Info", self)
        _main_layout = qt_import.QVBoxLayout(self)
        _main_layout.addWidget(self.groupBox)
        _main_layout.setSpacing(1)
        _main_layout.setContentsMargins(1, 1, 1, 1)

        _glayout = qt_import.QGridLayout()

        self.groupBox.setLayout(_glayout)

        self.current_label = qt_import.QLabel("Machine current:")
        self.current_value_label = qt_import.QLabel()
        self.current_value_label.setAlignment(qt_import.Qt.AlignCenter)
        self.current_value_label.setStyleSheet(
            "font-size: 24px;font-weight: bold; color: #00f"
        )

        # State text
        self.state_text_label = qt_import.QLabel("Machine status:")
        self.state_text_value_label = qt_import.QLabel()
        self.state_text_value_label.setAlignment(qt_import.Qt.AlignCenter)
        self.state_text_value_label.setStyleSheet("font-size: 18px;")

        # TopUp Remaining
        self.topup_remaining_label = qt_import.QLabel("TopUp Remaining:")
        self.topup_remaining_value_label = qt_import.QLabel()
        self.topup_remaining_value_label.setAlignment(qt_import.Qt.AlignCenter)
        self.topup_remaining_value_label.setStyleSheet("font-size: 18px;")

        # Layout --------------------------------------------------------------
        _glayout.addWidget(self.current_label, 0, 0)
        _glayout.addWidget(self.current_value_label, 0, 1)
        _glayout.addWidget(self.state_text_label, 1, 0)
        _glayout.addWidget(self.state_text_value_label, 1, 1)
        _glayout.addWidget(self.topup_remaining_label, 2, 0)
        _glayout.addWidget(self.topup_remaining_value_label, 2, 1)
        _glayout.setSpacing(1)
        _glayout.setContentsMargins(8, 8, 8, 8)

        # SizePolicies --------------------------------------------------------

        # Other ---------------------------------------------------------------
        self.setToolTip(
            "Main information about machine current, "
            + "machine status and top-up remaining time."
        )

    def set_property(self, property_name, value):
        self.property_changed(property_name, None, value)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.mach_info_hwobj is not None:
                self.disconnect(
                    self.mach_info_hwobj,
                    qt_import.SIGNAL("valuesChanged"),
                    self.set_value,
                )

            self.mach_info_hwobj = self.get_hardware_object(new_value)
            if self.mach_info_hwobj is not None:
                self.setEnabled(True)
                self.connect(
                    self.mach_info_hwobj,
                    qt_import.SIGNAL("valuesChanged"),
                    self.set_value,
                )
                self.mach_info_hwobj.re_emit_values()
            else:
                self.setEnabled(False)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def set_value(self, values):
        txt = (
            "??? mA"
            if values[0] is None
            else "<b>%s</b> mA" % str(self["formatString"] % abs(values[0]))
        )
        self.current_value_label.setText(txt)
        self.logger.debug("Setting values %s" % repr(values))

        self.state_text_value_label.setText(values[1])
        if values[2] != "":
            self.logger.debug(
                "Set top up remaining to %s (type %s)", values[2], type(values[2])
            )
            txt = (
                "??? s"
                if values[2] is None
                else "%s s" % str(self["formatString"] % values[2])
            )
            self.topup_remaining_value_label.setText(txt)

    def set_color(self, value):
        if value.get("mach_current") is None:
            colors.set_widget_color(self.current_value_label, STATES["unknown"])
        elif value.get("mach_current"):
            colors.set_widget_color(self.current_value_label, STATES["ready"])
        else:
            colors.set_widget_color(self.current_value_label, STATES["error"])
        colors.set_widget_color(self.state_text_value_label, STATES["ready"])


def test_brick(brick):
    brick.property_changed("mnemonic", None, "/mach-info")
