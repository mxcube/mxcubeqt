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
Shutter brick provides access to a shutter like device.
Interface is based on the AbstractNState hardware object
"""

from gui.utils import Colors, Icons, QtImport
from gui.BaseComponents import BaseWidget


__credits__ = ["MXCuBE collaboration"]
__license__ = "LGPLv3+"
__category__ = "General"


class ShutterBrick(BaseWidget):
    """Widget contains state label and two buttons to open and close the shutter"""

    def __init__(self, *args):
        BaseWidget.__init__(self, *args)

        # Properties ----------------------------------------------------------
        self.add_property("hwobj_shutter", "string", "")

        # Signals -------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------
        self.shutter_hwobj = None

        # Internal values -----------------------------------------------------

        # Graphic elements ----------------------------------------------------
        self.main_groupbox = QtImport.QGroupBox("Shutter", self)
        self.main_groupbox.setAlignment(QtImport.Qt.AlignCenter)
        self.state_label = QtImport.QLabel("<b>unknown</b>", self.main_groupbox)
        self.state_label.setAlignment(QtImport.Qt.AlignCenter)
        self.state_label.setFixedHeight(24)
        Colors.set_widget_color(self.state_label, Colors.LIGHT_GRAY)
        _button_widget = QtImport.QWidget(self.main_groupbox)

        self.open_button = QtImport.QPushButton(
            Icons.load_icon("ShutterOpen"), "Open", _button_widget
        )
        self.close_button = QtImport.QPushButton(
            Icons.load_icon("ShutterClose"), "Close", _button_widget
        )

        # Layout --------------------------------------------------------------
        _button_widget_hlayout = QtImport.QHBoxLayout(_button_widget)
        _button_widget_hlayout.addWidget(self.open_button)
        _button_widget_hlayout.addWidget(self.close_button)
        _button_widget_hlayout.setSpacing(2)
        _button_widget_hlayout.setContentsMargins(0, 0, 0, 0)

        _main_gbox_vlayout = QtImport.QVBoxLayout(self.main_groupbox)
        _main_gbox_vlayout.addWidget(self.state_label)
        _main_gbox_vlayout.addWidget(_button_widget)
        _main_gbox_vlayout.setSpacing(2)
        _main_gbox_vlayout.setContentsMargins(2, 2, 2, 2)

        _main_vlayout = QtImport.QVBoxLayout(self)
        _main_vlayout.addWidget(self.main_groupbox)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 0, 0)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.open_button.clicked.connect(self.open_button_clicked)
        self.close_button.clicked.connect(self.close_button_clicked)

        # Other ---------------------------------------------------------------

    def open_button_clicked(self):
        """Opens the shutter"""
        self.shutter_hwobj.open()

    def close_button_clicked(self):
        """Closes the shutter"""
        self.shutter_hwobj.close()

    def property_changed(self, property_name, old_value, new_value):
        """Initates the shutter hwobj"""
        if property_name == "hwobj_shutter":
            if self.shutter_hwobj is not None:
                self.disconnect(
                    self.shutter_hwobj, "shutterStateChanged", self.state_changed
                )
            else:
                self.shutter_hwobj = self.get_hardware_object(new_value)
                self.connect(
                    self.shutter_hwobj, "shutterStateChanged", self.state_changed
                )
                self.shutter_hwobj.update_values()
        else:
            BaseWidget.property_changed(self, property_name, old_value, new_value)

    def state_changed(self, shutter_state):
        """Based on the shutter state enables/disables open and close buttons"""
        self.state_label.setText(str(shutter_state.name.capitalize()))
        if shutter_state in ("UNKOWN", "AUTOMATIC", "DISABLED"):
            Colors.set_widget_color(self.state_label, Colors.LIGHT_GRAY)
        elif shutter_state in ("FAULT", "ERROR"):
            Colors.set_widget_color(self.state_label, Colors.LIGHT_RED)
        else:
            Colors.set_widget_color(self.state_label, Colors.LIGHT_GREEN)
        self.open_button.setEnabled(self.shutter_hwobj.is_closed())
        self.close_button.setEnabled(self.shutter_hwobj.is_open())
