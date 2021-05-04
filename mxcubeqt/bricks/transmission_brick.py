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

from mxcubeqt.utils import colors, qt_import
from mxcubeqt.base_components import BaseWidget

from mxcubecore import HardwareRepository as HWR

__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class TransmissionBrick(BaseWidget):

    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------

        # Internal variables --------------------------------------------------

        # Properties ----------------------------------------------------------
        self.add_property("formatString", "formatString", "###.##")

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.group_box = qt_import.QGroupBox("Transmission", self)
        current_label = qt_import.QLabel("Current:", self.group_box)
        current_label.setFixedWidth(75)
        self.transmission_ledit = qt_import.QLineEdit(self.group_box)
        self.transmission_ledit.setReadOnly(True)
        set_to_label = qt_import.QLabel("Set to:", self.group_box)
        self.new_value_ledit = qt_import.QLineEdit(self.group_box)

        # Layout --------------------------------------------------------------
        _group_box_gridlayout = qt_import.QGridLayout(self.group_box)
        _group_box_gridlayout.addWidget(current_label, 0, 0)
        _group_box_gridlayout.addWidget(self.transmission_ledit, 0, 1)
        _group_box_gridlayout.addWidget(set_to_label, 1, 0)
        _group_box_gridlayout.addWidget(self.new_value_ledit, 1, 1)
        _group_box_gridlayout.setSpacing(0)
        _group_box_gridlayout.setContentsMargins(1, 1, 1, 1)

        _main_vlayout = qt_import.QVBoxLayout(self)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 2, 2)
        _main_vlayout.addWidget(self.group_box)

        # SizePolicies --------------------------------------------------------

        # Other ---------------------------------------------------------------
        self._update_ledit_color(colors.LIGHT_GREEN)
        self.validator = qt_import.QDoubleValidator(0, 100, 2, self.new_value_ledit)
        self.new_value_ledit.setToolTip("Transmission limits 0 : 100 %")
        self.instance_synchronize("transmission_ledit", "new_value_ledit")

        if HWR.beamline.transmission is not None:
            # Qt signal/slot connections ------------------------------------------
            self.new_value_ledit.returnPressed.connect(self.current_value_changed)
            self.new_value_ledit.textChanged.connect(self.input_field_changed)
            self.connect(HWR.beamline.transmission, "stateChanged", self._state_changed)
            self.connect(HWR.beamline.transmission, "valueChanged", self._value_changed)
            self.connected()
        else:
            self.disconnected()

    def connected(self):
        self.setEnabled(True)

    def disconnected(self):
        self.setEnabled(False)

    def input_field_changed(self, text):
        """Paints the QLineEdit green if entered values is acceptable"""
        if self.validator.validate(text, 0)[0] == qt_import.QValidator.Acceptable:
            self._update_ledit_color(colors.LINE_EDIT_CHANGED)
        else:
            self._update_ledit_color(colors.LINE_EDIT_ERROR)

    def current_value_changed(self):
        """Sets new transmission value"""
        text = self.new_value_ledit.text()
        if self.validator.validate(text, 0)[0] == qt_import.QValidator.Acceptable:
            HWR.beamline.transmission.set_value(float(text))
            self.new_value_ledit.setText("")
            self._update_ledit_color(colors.LINE_EDIT_ACTIVE)

    def _state_changed(self, state):
        """Updates new value QLineEdit based on the state"""
        self._update_ledit_color(colors.COLOR_STATES[state])

    def _value_changed(self, new_value):
        """Updates transmission value"""
        try:
            new_values_str = self["formatString"] % new_value
            self.transmission_ledit.setText("%s %%" % new_values_str)
        except BaseException:
            pass

    def _update_ledit_color(self, color):
        colors.set_widget_color(self.new_value_ledit, color, qt_import.QPalette.Base)
