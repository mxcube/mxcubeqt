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

import QtImport

from gui.utils import Colors
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE colaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class AttenuatorsBrick(BaseWidget):

    STATES = {
        "ON": Colors.color_to_hexa(Colors.LIGHT_GREEN),
        "MOVING": Colors.color_to_hexa(Colors.LIGHT_YELLOW),
        "FAULT": Colors.color_to_hexa(Colors.LIGHT_RED),
        "UNKNOWN": Colors.color_to_hexa(Colors.DARK_GRAY),
    }

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.attenuators_hwobj = None

        # Internal variables --------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")
        self.add_property("mockup_mnemonic", "string", "")
        self.add_property("formatString", "formatString", "###.##")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.group_box = QtImport.QGroupBox("Transmission", self)
        current_label = QtImport.QLabel("Current:", self.group_box)
        current_label.setFixedWidth(75)
        self.transmission_ledit = QtImport.QLineEdit(self.group_box)
        self.transmission_ledit.setReadOnly(True)
        set_to_label = QtImport.QLabel("Set to:", self.group_box)
        self.new_value_ledit = QtImport.QLineEdit(self.group_box)

        # Layout --------------------------------------------------------------
        _group_box_gridlayout = QtImport.QGridLayout(self.group_box)
        _group_box_gridlayout.addWidget(current_label, 0, 0)
        _group_box_gridlayout.addWidget(self.transmission_ledit, 0, 1)
        _group_box_gridlayout.addWidget(set_to_label, 1, 0)
        _group_box_gridlayout.addWidget(self.new_value_ledit, 1, 1)
        _group_box_gridlayout.setSpacing(0)
        _group_box_gridlayout.setContentsMargins(1, 1, 1, 1)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 2, 2)
        _main_vlayout.addWidget(self.group_box)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.new_value_ledit.returnPressed.connect(self.current_value_changed)
        self.new_value_ledit.textChanged.connect(self.input_field_changed)

        # Other ---------------------------------------------------------------
        Colors.set_widget_color(
            self.new_value_ledit, Colors.LINE_EDIT_ACTIVE, QtImport.QPalette.Base
        )
        self.new_value_validator = QtImport.QDoubleValidator(
            0, 100, 2, self.new_value_ledit
        )
        self.new_value_ledit.setToolTip("Transmission limits 0 : 100 %")

        self.instance_synchronize("transmission_ledit", "new_value_ledit")

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.attenuators_hwobj is not None:
                self.disconnect(self.attenuators_hwobj, "deviceReady", self.connected)
                self.disconnect(
                    self.attenuators_hwobj, "deviceNotReady", self.disconnected
                )
                self.disconnect(
                    self.attenuators_hwobj,
                    "stateChanged",
                    self.transmission_state_changed,
                )
                self.disconnect(
                    self.attenuators_hwobj,
                    "valueChanged",
                    self.transmission_value_changed,
                )
            self.attenuators_hwobj = self.get_hardware_object(new_value)
            if self.attenuators_hwobj is not None:
                self.connect(self.attenuators_hwobj, "deviceReady", self.connected)
                self.connect(
                    self.attenuators_hwobj, "deviceNotReady", self.disconnected
                )
                self.connect(
                    self.attenuators_hwobj,
                    "stateChanged",
                    self.transmission_state_changed,
                )
                self.connect(
                    self.attenuators_hwobj,
                    "valueChanged",
                    self.transmission_value_changed,
                )
                self.connected()
                self.attenuators_hwobj.update_values()
            else:
                self.disconnected()
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def input_field_changed(self, input_field_text):
        if (
            self.new_value_validator.validate(input_field_text, 0)[0]
            == QtImport.QValidator.Acceptable
        ):
            Colors.set_widget_color(
                self.new_value_ledit, Colors.LINE_EDIT_CHANGED, QtImport.QPalette.Base
            )
        else:
            Colors.set_widget_color(
                self.new_value_ledit, Colors.LINE_EDIT_ERROR, QtImport.QPalette.Base
            )

    def current_value_changed(self):
        input_field_text = self.new_value_ledit.text()

        if (
            self.new_value_validator.validate(input_field_text, 0)[0]
            == QtImport.QValidator.Acceptable
        ):
            self.attenuators_hwobj.set_value(float(input_field_text))
            self.new_value_ledit.setText("")
            Colors.set_widget_color(
                self.new_value_ledit, Colors.LINE_EDIT_ACTIVE, QtImport.QPalette.Base
            )

    def connected(self):
        self.setEnabled(True)

    def disconnected(self):
        self.setEnabled(False)

    def transmission_state_changed(self, transmission_state):
        if transmission_state in self.STATES:
            color = self.STATES[transmission_state]
        else:
            color = self.STATES["UNKNOWN"]

    def transmission_value_changed(self, new_value):
        try:
            new_values_str = self["formatString"] % new_value
            self.transmission_ledit.setText("%s %%" % new_values_str)
        except BaseException:
            pass
