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
BeamstopDistanceBrick
"""

from gui.utils import Colors, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class BeamstopDistanceBrick(BaseWidget):
    def __init__(self, *args):

        BaseWidget.__init__(self, *args)

        # Hardware objects ----------------------------------------------------
        self.beamstop_hwobj = None

        # Internal variables --------------------------------------------------
        self.beamstop_limits = [0, 200]

        # Properties ----------------------------------------------------------
        self.add_property("mnemonic", "string", "")
        self.add_property("formatString", "formatString", "###.##")

        # Graphic elements ----------------------------------------------------
        self.group_box = QtImport.QGroupBox("Beamstop distance", self)
        current_label = QtImport.QLabel("Current:", self.group_box)
        current_label.setFixedWidth(75)
        self.beamstop_distance_ledit = QtImport.QLineEdit(self.group_box)
        self.beamstop_distance_ledit.setReadOnly(True)
        set_to_label = QtImport.QLabel("Set to:", self.group_box)
        self.new_value_ledit = QtImport.QLineEdit(self.group_box)

        # Layout --------------------------------------------------------------
        _group_box_gridlayout = QtImport.QGridLayout(self.group_box)
        _group_box_gridlayout.addWidget(current_label, 0, 0)
        _group_box_gridlayout.addWidget(self.beamstop_distance_ledit, 0, 1)
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

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            if self.beamstop_hwobj is not None:
                self.disconnect(self.beamstop_hwobj, "deviceReady", self.connected)
                self.disconnect(
                    self.beamstop_hwobj, "deviceNotReady", self.disconnected
                )
                self.disconnect(
                    self.beamstop_hwobj,
                    "beamstopDistanceChanged",
                    self.beamstop_distance_changed,
                )

            self.beamstop_hwobj = self.get_hardware_object(new_value)

            if self.beamstop_hwobj is not None:
                self.connect(self.beamstop_hwobj, "deviceReady", self.connected)
                self.connect(self.beamstop_hwobj, "deviceNotReady", self.disconnected)
                self.connect(
                    self.beamstop_hwobj,
                    "beamstopDistanceChanged",
                    self.beamstop_distance_changed,
                )
                self.beamstop_hwobj.update_values()
            else:
                self.disconnected()
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def connected(self):
        self.beamstop_limits = (0, 200)
        self.group_box.setEnabled(True)

    def disconnected(self):
        self.beamstop_limits = None
        self.group_box.setEnabled(False)

    def input_field_changed(self, input_field_text):
        if input_field_text == "":
            Colors.set_widget_color(
                self.new_value_ledit, Colors.LINE_EDIT_ACTIVE, QtImport.QPalette.Base
            )
        else:
            Colors.set_widget_color(
                self.new_value_ledit, Colors.LINE_EDIT_CHANGED, QtImport.QPalette.Base
            )

    def beamstop_distance_changed(self, value):
        if value is None:
            return
        if value < 0:
            self.beamstop_distance_ledit.setText("")
        else:
            value_str = self["formatString"] % value
            self.beamstop_distance_ledit.setText("%s mm" % value_str)

    def current_value_changed(self):
        try:
            val = float(str(self.new_value_ledit.text()))
        except (ValueError, TypeError):
            return

        if self.beamstop_limits is not None:
            if val < self.beamstop_limits[0] or val > self.beamstop_limits[1]:
                return
        self.beamstop_hwobj.set_distance(val)
        self.new_value_ledit.setText("")
