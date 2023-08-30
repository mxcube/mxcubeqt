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

"""
[Name] MultiStateBrick

[Description]
The MultiStateBrick displays checkbox with available states on a MotorsNState object.

[Properties]
-----------------------------------------------------------------------
| name         | type   | description
-----------------------------------------------------------------------
| mnenmonic  | string | name of the BeamAperture Hardware Object
-----------------------------------------------------------------------

[Signals] -

[Slots] -

[Comments] -

[Hardware Objects]
-----------------------------------------------------------------------
| name            | signals         | functions
-----------------------------------------------------------------------
| mnemonic        | valueChanged |
-----------------------------------------------------------------------
"""

try:
    unichr
except NameError:
    unichr = chr

import logging

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.base_components import BaseWidget

from mxcubecore.BaseHardwareObjects import HardwareObjectState


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class MultiStateBrick(BaseWidget):
    units = {
        "micron": u"\u03BC",
    }

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.multi_hwobj = None

        # Internal values -----------------------------------------------------
        self.positions = None
        self.multibutton = False
        self.multibuttons = []

        # Properties ----------------------------------------------------------
        self.add_property("label", "string", "")
        self.add_property("title", "string", "")
        self.add_property("mnemonic", "string", "")
        self.add_property("multibutton", "boolean", False)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_gbox = qt_import.QGroupBox("", self)
        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_gbox)
        _main_vlayout.addStretch()
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.label = qt_import.QLabel(self.main_gbox)
        self.multi_position_combo = qt_import.QComboBox(self.main_gbox)
        self.multi_position_combo.setMinimumWidth(100)
        self.multi_button_box = qt_import.QWidget(self.main_gbox)
        self._multi_button_hlayout = qt_import.QHBoxLayout(self.multi_button_box)

        # Layout --------------------------------------------------------------
        _main_gbox_hlayout = qt_import.QHBoxLayout(self.main_gbox)
        _main_gbox_hlayout.addWidget(self.label)
        _main_gbox_hlayout.addWidget(self.multi_position_combo)
        _main_gbox_hlayout.addWidget(self.multi_button_box)
        _main_gbox_hlayout.setSpacing(2)
        _main_gbox_hlayout.setContentsMargins(0, 0, 0, 0)

        # Qt signal/slot connections ------------------------------------------
        self.multi_position_combo.activated.connect(self.change_value)
        self.switch_multibutton_mode(False)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "label":
            if new_value == "":
                self.label.setText(new_value)
            else:
                self.label.hide()
        elif property_name == "title":
            if new_value != "":
                self.main_gbox.setTitle(new_value)
        elif property_name == "multibutton":
            if new_value != "":
                self.multibutton = new_value
                if len(self.positions):
                    self.switch_multibutton_mode(self.multibutton)
        elif property_name == "mnemonic":
            if self.multi_hwobj is not None:
                self.disconnect(self.multi_hwobj, "stateChanged", self.state_changed)
                self.disconnect(
                    self.multi_hwobj, "valueChanged", self.value_changed,
                )

            self.multi_hwobj = self.get_hardware_object(new_value)

            if self.multi_hwobj is not None:
                self.connect(self.multi_hwobj, "stateChanged", self.state_changed)
                self.connect(
                    self.multi_hwobj, "valueChanged", self.value_changed,
                )

                self.fill_positions()
                if self.multibutton:
                    self.switch_multibutton_mode(True)
                self.state_changed()
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def switch_multibutton_mode(self, mode):
        if mode:
            self.multi_position_combo.hide()
            self.multi_button_box.show()
        else:
            self.multi_position_combo.show()
            self.multi_button_box.hide()

    def get_position_label(self, posidx):
        pos = self.positions[posidx]
        unit = self.multi_hwobj.get_properties(posidx, "unit")
        label = str(pos)
        if unit is not None:
            if unit in self.units:
                label = label + self.units[unit]
            else:
                label = label + unit
        return label

    def fill_positions(self):

        # fill combo
        self.positions = []
        self.multi_position_combo.clear()

        for pos in self.multi_hwobj.get_position_list():
            self.positions.append(pos)

        # build multibuttons
        self.multibuttons = []

        for posidx in range(len(self.positions)):
            poslabel = self.get_position_label(posidx)
            self.multi_position_combo.addItem(poslabel)

            but = qt_import.QPushButton(poslabel)
            but.clicked.connect(
                lambda bla, this=self, idx=posidx: MultiStateBrick.change_value(
                    this, idx
                )
            )
            self._multi_button_hlayout.addWidget(but)
            self.multibuttons.append(but)

        self.value_changed()

    def change_value(self, index):
        if index >= 0:
            self.multi_hwobj.set_value(index)

    def state_changed(self, state=None):

        if state is None:
            state = self.multi_hwobj.get_state()

        if state == HardwareObjectState.READY:
            color = colors.LIGHT_GREEN
            self.setEnabled(True)
        elif state == HardwareObjectState.BUSY:
            color = colors.LIGHT_YELLOW
            self.setEnabled(False)
        else:
            color = colors.LIGHT_GRAY
            self.setEnabled(False)

        colors.set_widget_color(
            self.multi_position_combo, color, qt_import.QPalette.Button
        )

        for but in self.multibuttons:
            colors.set_widget_color(but, color, qt_import.QPalette.Button)

    def value_changed(self, value=None):

        self.multi_position_combo.blockSignals(True)

        if value is None:
            value = self.multi_hwobj.get_value()

        if value >= 0 and value < len(self.positions):
            self.multi_position_combo.setCurrentIndex(value)
        else:
            self.multi_position_combo.setCurrentIndex(-1)

        self.multi_position_combo.blockSignals(False)

        # value is index
        for button in self.multibuttons:
            button.setEnabled(True)

        self.multibuttons[value].setEnabled(False)
