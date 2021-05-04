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

import logging

from mxcubeqt.utils import icons, qt_import
from mxcubeqt.bricks.motor_spinbox_brick import MotorSpinboxBrick

"""
Controls both the light on/off (light_actuator) and intensity (motor)
"""

__category__ = "General"

STATE_OUT, STATE_IN, STATE_MOVING, STATE_FAULT, STATE_ALARM, STATE_UNKNOWN = (
    0,
    1,
    9,
    11,
    13,
    23,
)


class LightControlBrick(MotorSpinboxBrick):
    def __init__(self, *args):

        MotorSpinboxBrick.__init__(self, *args)
        self.light_actuator_hwo = None
        self.light_saved_pos = None

        self.light_off_button = qt_import.QPushButton(self.main_gbox)
        self.light_off_button.setIcon(icons.load_icon("BulbDelete"))
        self.light_off_button.setFixedSize(27, 27)

        self.light_on_button = qt_import.QPushButton(self.main_gbox)
        self.light_on_button.setIcon(icons.load_icon("BulbCheck"))
        self.light_on_button.setFixedSize(27, 27)

        self.light_off_button.clicked.connect(self.light_button_off_clicked)
        self.light_on_button.clicked.connect(self.light_button_on_clicked)

        self._gbox_hbox_layout.addWidget(self.light_off_button)
        self._gbox_hbox_layout.addWidget(self.light_on_button)

        self.light_off_button.setToolTip(
            "Switches off the light and sets the intensity to zero"
        )
        self.light_on_button.setToolTip(
            "Switches on the light and sets the intensity back to the previous setting"
        )

        self.light_off_button.setSizePolicy(
            qt_import.QSizePolicy.Fixed, qt_import.QSizePolicy.Minimum
        )
        self.light_on_button.setSizePolicy(
            qt_import.QSizePolicy.Fixed, qt_import.QSizePolicy.Minimum
        )

    # Light off pressed: switch off lamp and extract the light holder (if any)
    def light_button_off_clicked(self):
        if self.motor_hwobj is not None and hasattr(self.motor_hwobj, "move_out"):
            self.motor_hwobj.move_out()
            return
        if self.light_actuator_hwo is not None:
            if self.light_actuator_hwo.get_state() != STATE_OUT:
                if self.motor_hwobj is not None:
                    try:
                        self.light_saved_pos = self.motor_hwobj.get_value()
                    except BaseException:
                        logging.exception("could not get light actuator position")
                        self.light_saved_pos = None

                    if self["out_delta"] != "":
                        delta = float(self["out_delta"])
                    else:
                        delta = 0.0

                    light_limits = self.motor_hwobj.get_limits()
                    self.motor_hwobj.set_value(light_limits[0] + delta)

                self.light_state_changed(STATE_UNKNOWN)
                self.light_actuator_hwo.cmdOut()
            else:
                self.light_off_button.setDown(True)

    # Light on pressed: set in the light holder (if any) and set lamp to previous position
    def light_button_on_clicked(self):
        print('LightControlBrick light_button_on_clicked')
        if self.motor_hwobj is not None and hasattr(self.motor_hwobj, "move_in"):
            self.motor_hwobj.move_in()
            print('in self.motor_hwobj.move_in()')
            return
        if self.light_actuator_hwo is not None:
            if self.light_actuator_hwo.get_state() != STATE_IN:
                self.light_state_changed(STATE_UNKNOWN)
                self.light_actuator_hwo.cmdIn()
                if self.light_saved_pos is not None and self.motor_hwobj is not None:
                    self.motor_hwobj.set_value(self.light_saved_pos)
            else:
                self.light_on_button.setDown(True)

    def light_state_changed(self, state):
        print('LightControlBrick light_state_changed')
        if state == STATE_IN:
            self.light_on_button.setDown(True)
            self.light_off_button.setDown(False)
            self.move_left_button.setEnabled(True)
            self.move_right_button.setEnabled(True)
        elif state == STATE_OUT:
            self.light_on_button.setDown(False)
            self.light_off_button.setDown(True)
            self.move_left_button.setEnabled(False)
            self.move_right_button.setEnabled(False)
        else:
            self.light_on_button.setDown(False)
            self.light_off_button.setDown(False)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            MotorSpinboxBrick.property_changed(
                self, property_name, old_value, new_value
            )
            if self.motor_hwobj is not None:
                if self.motor_hwobj.is_ready():
                    limits = self.motor_hwobj.get_limits()
                    motor_range = float(limits[1] - limits[0])
                    self["delta"] = str(motor_range / 10.0)
                else:
                    self["delta"] = 1.0
        else:
            MotorSpinboxBrick.property_changed(
                self, property_name, old_value, new_value
            )
