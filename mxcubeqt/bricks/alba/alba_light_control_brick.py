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


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "ALBA"


#
# These state list is as in ALBAEpsActuator.py
#
STATE_OUT, STATE_IN, STATE_MOVING, STATE_FAULT, STATE_ALARM, STATE_UNKNOWN = (
    0,
    1,
    9,
    11,
    13,
    23,
)

STATES = {
    STATE_IN: colors.LIGHT_GREEN,
    STATE_OUT: colors.LIGHT_GRAY,
    STATE_MOVING: colors.LIGHT_YELLOW,
    STATE_FAULT: colors.LIGHT_RED,
    STATE_ALARM: colors.LIGHT_RED,
    STATE_UNKNOWN: colors.LIGHT_GRAY,
}


class AlbaLightControlBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)
        self.logger = logging.getLogger("GUI Alba Actuator")
        self.logger.info("__init__()")

        self.on_color = colors.color_to_hexa(colors.LIGHT_GREEN)
        self.off_color = colors.color_to_hexa(colors.LIGHT_GRAY)
        self.fault_color = colors.color_to_hexa(colors.LIGHT_RED)
        self.unknown_color = colors.color_to_hexa(colors.DARK_GRAY)

        # Hardware objects ----------------------------------------------------
        self.light_ho = None

        self.state = None
        self.level = None
        self.icons = None
        self.level_limits = [None, None]

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")
        self.add_property("icons", "string", "")

        # Graphic elements ----------------------------------------------------
        self.widget = qt_import.load_ui_file("alba_lightcontrol.ui")

        qt_import.QHBoxLayout(self)

        self.layout().addWidget(self.widget)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.widget.layout().setContentsMargins(0, 0, 0, 0)
        self.widget.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.widget.button.clicked.connect(self.do_switch)
        self.widget.slider.valueChanged.connect(self.do_set_level)

        # SizePolicies --------------------------------------------------------
        self.setSizePolicy(
            qt_import.QSizePolicy.Expanding, qt_import.QSizePolicy.MinimumExpanding
        )

        # Defaults
        self.set_icons("BulbCheck,BulbDelete")

        # Other ---------------------------------------------------------------
        self.setToolTip("Control of light (set level and on/off switch.")

        self.update()

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.light_ho is not None:
                self.disconnect(
                    self.light_ho, qt_import.SIGNAL("levelChanged"), self.level_changed
                )
                self.disconnect(
                    self.light_ho, qt_import.SIGNAL("stateChanged"), self.state_changed
                )

            self.light_ho = self.get_hardware_object(new_value)

            if self.light_ho is not None:
                self.setEnabled(True)
                self.connect(
                    self.light_ho, qt_import.SIGNAL("levelChanged"), self.level_changed
                )
                self.connect(
                    self.light_ho, qt_import.SIGNAL("stateChanged"), self.state_changed
                )
                self.light_ho.re_emit_values()
                self.setToolTip(
                    "Control of %s (light level and on/off switch."
                    % self.light_ho.getUserName()
                )
                self.set_level_limits(self.light_ho.get_limits())
                self.set_label(self.light_ho.getUserName())
            else:
                self.setEnabled(False)
        elif property_name == "icons":
            self.set_icons(new_value)
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def update(self, state=None):
        if self.light_ho is not None:
            self.setEnabled(True)
            if self.state is "on":
                color = self.on_color
                self.widget.slider.setEnabled(True)
                if self.icons:
                    self.widget.button.setIcon(self.icons["on"])
                    self.widget.button.setToolTip("Set light Off")
            elif self.state is "off":
                color = self.off_color
                # self.widget.slider.setEnabled(False)
                self.widget.slider.setEnabled(True)
                if self.icons:
                    self.widget.button.setIcon(self.icons["off"])
                    self.widget.button.setToolTip("Set light On")
            else:
                color = self.fault_color
                self.setEnabled(False)

            if self.level is not None and None not in self.level_limits:
                self.widget.slider.blockSignals(True)
                self.widget.slider.setValue(self.level)
                self.widget.slider.blockSignals(False)
                self.widget.slider.setToolTip("Light Level: %s" % self.level)
        else:
            self.setEnabled(False)
            color = self.unknown_color

        self.widget.button.setStyleSheet("background-color: %s;" % color)

    def set_icons(self, icons):
        icons = icons.split(",")
        if len(icons) == 2:
            self.icons = {
                "on": icons.load_icon(icons[0]),
                "off": icons.load_icon(icons[1]),
            }
            self.widget.button.setIcon(self.icons["on"])

    def level_changed(self, level):
        self.level = level
        self.update()

    def state_changed(self, state):
        self.state = state
        self.update()

    def set_label(self, text):
        self.widget.label.setText(text)

    def set_level_limits(self, limits):
        self.level_limits = limits
        if None not in self.level_limits:
            self.widget.slider.setMinimum(self.level_limits[0])
            self.widget.slider.setMaximum(self.level_limits[1])

    def do_set_level(self):  # when slider is moved
        newvalue = self.widget.slider.value()
        self.light_ho.setLevel(newvalue)

    def do_switch(self):
        if self.state == "on":
            self.light_ho.setOff()
        elif self.state == "off":
            self.light_ho.setOn()
        else:
            pass
